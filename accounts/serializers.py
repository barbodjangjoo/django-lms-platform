from rest_framework import serializers
from django.utils.translation import gettext_lazy as _


from .models import CustomUser
from notifications.models import Notification
from points.models import UserPoint

class RegisterSerializer(serializers.ModelSerializer):
    # password = serializers.CharField(max_length=128, write_only=True)
    # password2 = serializers.CharField(max_length=128, write_only=True)
    class Meta:
        model = CustomUser
        fields = [
            # 'first_name', changed
            # 'last_name',  changed
            # 'birth_date', changed
            # 'gender', changed
            # 'username', changed
            # 'city', changed
            'phone_number', 
            # 'email',  changed
            # 'find',   changed
            # 'password',  changed
            # 'password2' changed
            ]
        
    # def validate(self, attrs):
    #     if attrs['password'] != attrs['password2']:
    #         raise serializers.ValidationError({"password": _("رمز عبور و تکرار آن یکسان نیست.")})
    #     return attrs
        
    # def create(self, validated_data):
    #     password = validated_data.pop('password')
    #     validated_data.pop('password2')
    #     user = CustomUser.objects.create_user(**validated_data)
    #     user.set_password(password)
    #     user.save()
    #     return user

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
        
class DashboardNotificationSerializers(serializers.ModelSerializer):
    class Meta:
        model = Notification
        fields = ["id", 'title',"message", "is_read"]

class DashboardPointsSerializers(serializers.ModelSerializer):
    class Meta:
        model = UserPoint
        fields = ['points', 'created_at']

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
            raise serializers.ValidationError({'error': 'رمز عبور و تکرار آن برابر نیستند.'})

        return attrs
