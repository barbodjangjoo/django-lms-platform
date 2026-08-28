from rest_framework.decorators import api_view, permission_classes
from rest_framework.response import Response
from rest_framework import status
from rest_framework_simplejwt.tokens import RefreshToken
from django.db.models import Sum
from rest_framework.permissions import IsAuthenticated, AllowAny
from django.contrib.auth.password_validation import validate_password
from django.shortcuts import get_object_or_404
from django.utils.translation import gettext_lazy as _
import random
from django.contrib.auth.tokens import default_token_generator
from django.utils.http import urlsafe_base64_encode
from django.utils.encoding import force_bytes
from django.conf import settings
from django.core.mail import send_mail
from django.contrib.auth.views import PasswordResetConfirmView, PasswordResetCompleteView
from django.urls import reverse, reverse_lazy
from django.conf import settings

# from audit.models import Audit
# from course.models import UserExerciseStatus


from . import serializers
from .models import CustomUser

from .otp_handler import verify_code_from_redis, can_send_otp, normalize_phone, can_send_reset_email
from .tasks import send_otp_to_user



def send_otp(user, purpose="SIGNUP"):
    code = f"{random.randint(100000, 999999)}"
    verify_code_from_redis(user.phone_number, purpose, code)

    print(f"OTP for {user.phone_number} is {code}")

    return code

@api_view(['POST'])
def user_registeration_view(request):
    serializer = serializers.RegisterSerializer(data=request.data)
    serializer.is_valid(raise_exception=True)
    user = serializer.save()

    code = send_otp(user, purpose="SIGNUP")

    refresh = RefreshToken.for_user(user)
    tokens = {
        'refresh': str(refresh),
        'access': str(refresh.access_token),
    }

    response_data = serializer.data
    response_data['otp'] = {"purpose": "SIGNUP"} 
    response_data['tokens'] = tokens

    return Response(response_data, status=status.HTTP_201_CREATED)

@api_view(["POST"])
def send_otp_view(request):
    serializer = serializers.SendOTPSerializer(data=request.data)
    serializer.is_valid(raise_exception=True)

    raw_phone = serializer.validated_data['phone_number']
    phone_number = normalize_phone(raw_phone)

    if not can_send_otp(phone_number, purpose="LOGIN"):
        return Response(
            {"error": _("You reached the maximum amount of attempt")},
            status=status.HTTP_429_TOO_MANY_REQUESTS
        )

    otp = send_otp_to_user(phone_number, purpose="LOGIN")

    return Response({
        "message": _("Code has been sent!"),
        'OTP': otp
    }, status=status.HTTP_200_OK)


@api_view(["POST"])
def verify_otp_view(request):
    serializer = serializers.VerifyOTPSerializer(data=request.data)
    serializer.is_valid(raise_exception=True)

    raw_phone = serializer.validated_data['phone_number']
    code = serializer.validated_data['code']

    phone_number = normalize_phone(raw_phone)

    result = verify_code_from_redis(phone_number, "LOGIN", code)
    if result == "too_many_attempts":
        return Response(
            {"error": _("You have reached the maximum amount of code")},
            status=status.HTTP_429_TOO_MANY_REQUESTS
        )
    elif result == "invalid_code":
        return Response({"error": _("Wrong or Expired code")},
                        status=status.HTTP_400_BAD_REQUEST)

    user, created = CustomUser.objects.get_or_create(
        phone_number=phone_number,
        defaults={

        }
    )


    refresh = RefreshToken.for_user(user)
    return Response({
        "refresh": str(refresh),
        "access": str(refresh.access_token),
        "user": serializers.UserSerializer(user).data,
        "created": created ,
        "code": code
    }, status=status.HTTP_200_OK)


@api_view(["POST"])
def send_reset_otp_view(request):
    serializer = serializers.SendResetOTPSerializer(data=request.data)
    serializer.is_valid(raise_exception=True)

    raw_phone = serializer.validated_data['phone_number']
    phone_number = normalize_phone(raw_phone)

    if not CustomUser.objects.filter(phone_number=phone_number).exists():
        return Response({"error": _("There is no user with this phone number")},
                        status=status.HTTP_404_NOT_FOUND)

    if not can_send_otp(phone_number, purpose="RESET_PASSWORD"):
        return Response(
            {"error": _("Too many attempt")},
            status=status.HTTP_429_TOO_MANY_REQUESTS
        )

    otp = send_otp_to_user(phone_number, purpose="RESET_PASSWORD")
    if settings.debug:
        return Response({
            "message": _("Code has been sent"),
            "OTP": otp  # For develope only
        })
    return Response({
        "message": _("Your recovery code has been sent")
    })

@api_view(["POST"])
def verify_reset_otp_view(request):
    serializer = serializers.VerifyResetOTPSerializer(data=request.data)
    serializer.is_valid(raise_exception=True)

    raw_phone = serializer.validated_data['phone_number']
    code = serializer.validated_data['code']
    phone_number = normalize_phone(raw_phone)

    result = verify_code_from_redis(phone_number, "RESET_PASSWORD", code)
    if result == "too_many_attempts":
        return Response({"error": _("Too many attempt")}, status=status.HTTP_429_TOO_MANY_REQUESTS)
    elif result == "invalid_code":
        return Response({"error": _("Invalid code or expired")}, status=status.HTTP_400_BAD_REQUEST)

    return Response({"message": _("Code recieve successfully!")}, status=status.HTTP_200_OK)

@api_view(["POST"])
@permission_classes([IsAuthenticated])
def reset_password_view(request):
    user= request.user
    user = get_object_or_404(CustomUser, id=user.id)

    serializer = serializers.ResetPasswordSerializer(data=request.data)
    serializer.is_valid(raise_exception=True)

    new_password = serializer.validated_data['new_password']


    user.set_password(new_password)
    user.save()

    return Response({"message": _("Your password has been changed successfully")}, status=status.HTTP_200_OK)




@api_view(['GET'])
def profile_view(request):
    user= request.user
    queryset = CustomUser.objects.filter(id=user.id)
    if user.is_authenticated:
        serializer = serializers.UserSerializer(user)
        Audit.objects.create(
            user=user,
            log_type = 'AUTHENTICATIONS',
            call_function='profile_view',
            http_response_status_code = 200,
            result = 'loged in'
        )
        return Response(serializer.data, status=status.HTTP_200_OK)
    Audit.objects.create(
        user=user,
        log_type = 'AUTHENTICATIONS',
        call_function='profile_view',
        http_response_status_code = 401,
        result = 'User is not Authenticated'
    )
    return Response({"detail": "User not authenticated."}, status=status.HTTP_401_UNAUTHORIZED)

@api_view(['PATCH'])    
def user_update_view(request):
    if request.user.is_authenticated:
        user= request.user
        serializer = serializers.UserSerializer(user, data=request.data, partial=True)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        # Audit.objects.create(
        #     user=user,
        #     log_type = 'AUTHENTICATIONS',
        #     call_function='user_update_view',
        #     http_response_status_code = 200,
        #     result = f'update profile {request.data} for {user}'
        # )
        return Response(serializer.data, status=status.HTTP_200_OK)
    
    # Audit.objects.create(
    #     user=user,
    #     log_type = 'AUTHENTICATIONS',
    #     call_function='user_update_view',
    #     http_response_status_code = 401,
    #     result = 'user is not authenticated'
    # )
    return Response({"detail": "User not authenticated."}, status=status.HTTP_401_UNAUTHORIZED)



@api_view(['PATCH'])
@permission_classes([IsAuthenticated])
def change_password_view(request):
    user= request.user
    serializer = serializers.ChangePasswordSerializer(data=request.data)
    serializer.is_valid(raise_exception=True)

    old_password = serializer.validated_data['old_password']
    new_password = serializer.validated_data['new_password']

    if not user.check_password(old_password):
        return Response({'old_password': _("Current password is wrong")}, status=status.HTTP_400_BAD_REQUEST)

    try:
        validate_password(new_password, user)
    except Exception as e:
        return Response({'new_password': e.messages}, status=status.HTTP_400_BAD_REQUEST)

    user.set_password(new_password)
    user.save()
    
    # Audit.objects.create(
    #     user=user,
    #     log_type = 'AUTHENTICATIONS',
    #     call_function='user_dashboard_view',
    #     http_response_status_code = 200,
    #     result = 'user password has changed successfully for user '
    # )
    return Response({'detail': _("Password changed successfully")}, status=status.HTTP_200_OK)

@api_view(['GET'])
@permission_classes([IsAuthenticated])
def get_me(request):
    user = request.user
    if user.is_authenticated:
        serializer = serializers.UserSerializer(user)
        return Response(serializer.data)
    return Response({
        'detail': _("User is not logged in")},
        status = status.HTTP_401_UNAUTHORIZED
    )


@api_view(['POST'])
def password_reset_view(request):
    serializer = serializers.PasswordResetRequestSerializer(data=request.data)
    serializer.is_valid(raise_exception=True)
    phone_number = serializer.validated_data['phone_number']

    users = CustomUser.objects.filter(phone_number=phone_number, is_active=True)
    if not users.exists():
        return Response({"detail": _("No user was found with this phone number.")}, status=status.HTTP_404_NOT_FOUND)

    for user in users:
        if not can_send_reset_email(user.id, limit=3):
            return Response(
                {"detail": _("The maximum number of password reset requests has been reached.")},
                status=status.HTTP_429_TOO_MANY_REQUESTS
            )

        token = default_token_generator.make_token(user)
        uid = urlsafe_base64_encode(force_bytes(user.pk))
        reset_link = request.build_absolute_uri(
            reverse('password_reset_confirm', kwargs={'uidb64': uid, 'token': token})
        )

        send_mail(
            subject=_("Password Reset"),
            message=_("Click the link below to reset your password:\n{reset_link}\n\nThis link is valid for 5 minutes.").format(reset_link=reset_link),
            from_email=settings.DEFAULT_FROM_EMAIL,
            recipient_list=[user.email],
            fail_silently=False,
        )

    return Response({"detail": _("The password reset link has been sent!")}, status=status.HTTP_200_OK)


class PasswordResetConfirmTemplateView(PasswordResetConfirmView):
    template_name = 'accounts/password_reset_confirm.html'
    success_url = reverse_lazy('password_reset_complete')


    def form_valid(self, form):
        form.save() 
        return super().form_valid(form)


class PasswordResetCompleteTemplateView(PasswordResetCompleteView):
    template_name = 'accounts/password_reset_complete.html'

    