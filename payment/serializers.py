from rest_framework import serializers
from rest_framework.response import Response

from . import models
from course import models as course

class PurchaseItemInputSerializer(serializers.Serializer):
    reference_id = serializers.CharField()

class FactorSerializer(serializers.ModelSerializer):
    class Meta:
        model = models.Factor
        fields = [
           'id', 'user', 'payment_status', 'datetime_transaction', 'total_price', 'datetime_created', 'datetime_modified'
        ]


class PurchaseItemSerializer(serializers.ModelSerializer):
    item_name = serializers.SerializerMethodField()

    class Meta:
        model = models.PurchaseItem
        fields = [
        'id',
        'user',
        'factor',
        'item_name',
        'type', 
        'reference_id', 
        'price', 
        'payment_status',
        'datetime_created', 
        'datetime_modified',
        ]
    def get_item_name(self, obj):
        if obj.type == 'course':
            try:
                query = course.Course.objects.get(id=obj.reference_id)
                return query.title
            except course.Course.DoesNotExist:
                return None      

class FactorListSerializer(serializers.ModelSerializer):
    purchase_items = PurchaseItemSerializer(many=True, read_only=True)
    # payment_status = serializers.SerializerMethodField()
    class Meta:
        model = models.Factor
        fields = [
            'id',
            'user',
            'payment_status',
            'datetime_transaction',
            'total_price',
            'datetime_created',
            'datetime_modified',
            'purchase_items'
        ]
    
    # def get_payment_status(self, obj):
    #     transaction = models.Transaction.objects.get(id=obj)
    #     if transaction.exists():
    #         return transaction.payment_datetime
    #     else:
    #         return None