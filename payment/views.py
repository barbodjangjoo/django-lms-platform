import requests
import json
from django.shortcuts import get_object_or_404, redirect, render
from rest_framework.decorators import api_view, permission_classes
from rest_framework.response import Response 
from rest_framework.permissions import IsAuthenticated
from rest_framework import status
from django.http import HttpResponse, JsonResponse
import logging
from django.db import transaction
from django.utils.translation import gettext_lazy as _

from . import models
from . import serializers
from course import models as coursemodel
from audit.models import Audit
from config.settings import MERCHANT_ID
import logging

logger = logging.getLogger(__name__)


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def add_purchased_item_view(request):
    serializer = serializers.PurchaseItemInputSerializer(data=request.data)
    serializer.is_valid(raise_exception=True)

    reference_id = serializer.validated_data['reference_id']
    user = request.user

    item = coursemodel.Course.objects.get(id=reference_id)
    discount = item.discount 

    old_purchases = models.PurchaseItem.objects.filter(
        user=user,
        reference_id=reference_id
    )

    old_purchases.filter(payment_status__in=["pending", "failed"]).update(payment_status="failed")

    models.Factor.objects.filter(
        user=user,
        payment_status="pending"
    ).update(payment_status="failed")
    price_after_discount = item.price * (1 - discount / 100)

    factor = models.Factor.objects.create(
        user=user,
        payment_status="pending",
        total_price=price_after_discount,
)

    Audit.objects.create(
        user=request.user,
        log_type = "PAYMENTS",
        call_function = 'add_purchased_item_view',
        http_response_status_code = 201,
        result = 'user created factor and change old factor to failed'
    )
    purchase_item = models.PurchaseItem.objects.create(
        user=user,
        factor=factor,
        reference_id=reference_id,
        price=price_after_discount,
        payment_status="pending"
    )

    serializer = serializers.FactorListSerializer(factor)
    return Response(serializer.data, status=201)

@api_view(['GET'])
@permission_classes(IsAuthenticated)
def factors_list_view(request):

    user = request.user
    factors = models.Factor.objects.filter(user=user).all()
    serializer = serializers.FactorListSerializer(factors, many=True)
    return Response(serializer.data)

@api_view(['GET'])
@permission_classes(IsAuthenticated)
def factor_detail_view(request, pk):
    factor = get_object_or_404(models.Factor, pk=pk)
    serializer = serializers.FactorListSerializer(factor)
    return Response(serializer.data)

def calculate_total_price_with_discount(factor):
    total = 0
    for item in factor.items.all():  
        course = item.course
        price = course.price
        discount = course.discount 
        price_after_discount = price * (1 - discount / 100)
        total += price_after_discount
    return total

# redirect
@transaction.atomic
def invoice_pay(request, pk):
    factor = get_object_or_404(models.Factor, pk=pk)

    rial_total_price = factor.total_price * 10

    callback_url = request.GET.get('callback_url')

    request.session['frontend_callback_url'] = callback_url 

    zarinpal_request_url = "https://payment.zarinpal.com/pg/v4/payment/request.json"

    reqeust_header = {
        'accept': "application/json",
        'content-type': "application/json"
    }

    request_data = {
        'merchant_id': MERCHANT_ID,
        'amount': rial_total_price,
        'description': f'#{factor.id} : {factor.user.first_name} - {factor.user.last_name}',
        'callback_url': 'http://api.rhino-teams.com/payment/payment_check',
    }


    res = requests.post(url=zarinpal_request_url, data=json.dumps(request_data), headers=reqeust_header)

    data = res.json()['data']
    authority = data['authority']

    models.Transaction.objects.create(
        factor=factor,
        user=factor.user,
        payment_authority=authority
    )

    if 'errors' not in res.json() or len(res.json().get('errors', [])) == 0:

        
        return redirect(f'https://payment.zarinpal.com/pg/StartPay/{authority}')
    else:
        return HttpResponse('Error from zarinpal')


@transaction.atomic
def check_payment(request):
    payment_authority = request.GET.get('Authority')
    payment_status = request.GET.get('Status')

    frontend_callback_url = request.session.get('frontend_callback_url')
    logger.info(f'frontend callback url recieved: {frontend_callback_url}')

    transaction = get_object_or_404(models.Transaction, payment_authority=payment_authority)
    rial_total_price = transaction.factor.total_price * 10


    if payment_status == 'OK':
        reqeust_header = {
            'accept': "application/json",
            'content-type': "application/json"
        }
        request_data = {
            'merchant_id': MERCHANT_ID,
            'amount': rial_total_price,
            'authority': payment_authority
        }

        res = requests.post(
            url='https://payment.zarinpal.com/pg/v4/payment/verify.json',
            data=json.dumps(request_data),
            headers=reqeust_header,
        )
        resp = res.json()

        if 'data' in resp and ('errors' not in resp or len(resp.get('errors', [])) == 0):
            data = resp['data']
            payment_code = data['code']

            transaction.zarinpal_ref_id = data['ref_id']
            transaction.zarinpal_data = data
            transaction.save()

            purchase_item = models.PurchaseItem.objects.get(factor=transaction.factor)
            purchase_item.payment_status = 'successful'
            purchase_item.save()

            factor = transaction.factor
            factor.payment_status = 'successful'
            factor.datetime_transaction = transaction.payment_datetime
            factor.save()

            Audit.objects.create(
            user = request.user,
            log_type = "PAYMENTS",
            call_function = 'check_payment',
            http_response_status_code = 200,
            result = f'user: {request.user} changed payment status into successful'
        )


            if payment_code == 100:
                return render(request, 'payment/success.html', {
                    'ref_id': data['ref_id'],
                    'frontend_callback_url': frontend_callback_url
                })
            else:
                return render(request, 'payment/already_paid.html', {
                    'ref_id': data['ref_id'],
                    'frontend_callback_url': frontend_callback_url
                })

        else:
            errors = resp.get('errors', {})
            error_code = errors.get('code', 'unknown')
            error_messages = errors.get('message', 'unknown error')
            transaction.factor.payment_status = 'failed'
            transaction.factor.save()

            Audit.objects.create(
            user = request.user,
            log_type = "PAYMENTS",
            call_function = 'check_payment',
            http_response_status_code = int(error_code),
            result = f'user: {request.user} got errors \n error messages: {error_messages}')

            return HttpResponse(_(f'Payment has been failed due: {error_code} - {error_messages}'))
        


    else:
        factor = transaction.factor
        factor.payment_status = 'failed'
        factor.save()

    return render(request, 'payment/failed.html', {
        "error_code": "NOK",
        "error_message": _('Payment has been canceled'),
        "frontend_callback_url": frontend_callback_url
    })

