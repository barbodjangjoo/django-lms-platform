from rest_framework import serializers
from django.utils.translation import gettext_lazy as _


from .models import CustomUser

class RegisterSerializer(serializers.ModelSerializer):
    class Meta:
        model = CustomUser
        fields = [
            'phone_number', 
        ]    

class SendOTPSerializer(serializers.Serializer):
    phone_number = serializers.CharField(max_length=11)


class VerifyOTPSerializer(serializers.Serializer):
    phone_number = serializers.CharField(max_length=11)
    code = serializers.CharField(max_length=6)


class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = CustomUser
        fields = [
            'id',
            'profile_picture',
            'first_name',
            'last_name',
            'birth_date',
            'gender',
            'username',
            'city',
            'address',
            'marital_status',
            'educational_status',
            'national_id',
            'national_card',
            'phone_number',
            'email',
            'job_status',
            'job_title',
            'job_experience',
            'find',
            'join',
        ]

class ChangePasswordSerializer(serializers.Serializer):
    old_password = serializers.CharField(required=True)
    new_password = serializers.CharField(required=True)

class PasswordResetRequestSerializer(serializers.Serializer):
    phone_number = serializers.CharField()

class SendResetOTPSerializer(serializers.Serializer):
    phone_number = serializers.CharField()

class VerifyResetOTPSerializer(serializers.Serializer):
    phone_number = serializers.CharField()
    code = serializers.CharField(max_length=6)

class ResetPasswordSerializer(serializers.Serializer):
    new_password = serializers.CharField()
    new_password_confirm = serializers.CharField(write_only=True, min_length=6)
    
    def validate(self, attrs):
        new_password = attrs.get('new_password')
        new_password_confirm = attrs.get('new_password_confirm')

        if new_password != new_password_confirm:
            raise serializers.ValidationError({'error': _('Your password and repeat does not match!')})

        return attrs
