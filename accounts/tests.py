from datetime import timedelta
from unittest.mock import patch, MagicMock

from django.contrib.auth import get_user_model
from django.core import mail
from django.test import TestCase, override_settings
from django.urls import reverse

from rest_framework import status
from rest_framework.test import APITestCase, APIClient

from .models import CustomUser
from .serializers import (
    RegisterSerializer,
    SendOTPSerializer,
    VerifyOTPSerializer,
    ChangePasswordSerializer,
    ResetPasswordSerializer,
)
from .otp_handler import (
    normalize_phone,
    can_send_otp,
    store_otp,
    verify_code_from_redis,
    can_send_reset_email,
)
from .tasks import send_otp_to_user


User = get_user_model()


# ============================================================
# Model Tests
# ============================================================

class CustomUserModelTests(TestCase):

    def test_create_user_with_phone_number(self):
        user = CustomUser.objects.create_user(
            phone_number="09120000000",
            password="TestPassword123",
        )

        self.assertEqual(user.phone_number, "09120000000")
        self.assertTrue(user.check_password("TestPassword123"))
        self.assertTrue(user.is_active)

    def test_phone_number_must_be_unique(self):
        CustomUser.objects.create_user(
            phone_number="09120000000",
            password="TestPassword123",
        )

        with self.assertRaises(Exception):
            CustomUser.objects.create_user(
                phone_number="09120000000",
                password="AnotherPassword123",
            )

    def test_email_must_be_unique(self):
        CustomUser.objects.create_user(
            phone_number="09120000001",
            email="test@example.com",
            password="TestPassword123",
        )

        with self.assertRaises(Exception):
            CustomUser.objects.create_user(
                phone_number="09120000002",
                email="test@example.com",
                password="AnotherPassword123",
            )

    def test_username_field_is_phone_number(self):
        self.assertEqual(CustomUser.USERNAME_FIELD, "phone_number")

    def test_user_string_representation(self):
        user = CustomUser.objects.create_user(
            phone_number="09120000003",
            first_name="Barbod",
            last_name="Jangjo",
            password="TestPassword123",
        )

        self.assertEqual(str(user), "Barbod - Jangjo")


# ============================================================
# Serializer Tests
# ============================================================

class RegisterSerializerTests(TestCase):

    def test_register_serializer_accepts_valid_phone_number(self):
        serializer = RegisterSerializer(
            data={"phone_number": "09120000000"}
        )

        self.assertTrue(serializer.is_valid())
        self.assertEqual(
            serializer.validated_data["phone_number"],
            "09120000000",
        )

    def test_register_serializer_rejects_phone_longer_than_11(self):
        serializer = RegisterSerializer(
            data={"phone_number": "091200000000"}
        )

        self.assertFalse(serializer.is_valid())
        self.assertIn("phone_number", serializer.errors)


class SendOTPSerializerTests(TestCase):

    def test_send_otp_serializer_accepts_valid_phone(self):
        serializer = SendOTPSerializer(
            data={"phone_number": "09120000000"}
        )

        self.assertTrue(serializer.is_valid())

    def test_send_otp_serializer_rejects_long_phone(self):
        serializer = SendOTPSerializer(
            data={"phone_number": "091200000000"}
        )

        self.assertFalse(serializer.is_valid())
        self.assertIn("phone_number", serializer.errors)


class VerifyOTPSerializerTests(TestCase):

    def test_verify_otp_serializer_accepts_valid_data(self):
        serializer = VerifyOTPSerializer(
            data={
                "phone_number": "09120000000",
                "code": "123456",
            }
        )

        self.assertTrue(serializer.is_valid())

    def test_verify_otp_serializer_rejects_code_longer_than_6(self):
        serializer = VerifyOTPSerializer(
            data={
                "phone_number": "09120000000",
                "code": "1234567",
            }
        )

        self.assertFalse(serializer.is_valid())
        self.assertIn("code", serializer.errors)


class ChangePasswordSerializerTests(TestCase):

    def test_change_password_serializer_accepts_valid_data(self):
        serializer = ChangePasswordSerializer(
            data={
                "old_password": "OldPassword123",
                "new_password": "NewPassword123",
            }
        )

        self.assertTrue(serializer.is_valid())

    def test_change_password_serializer_requires_old_password(self):
        serializer = ChangePasswordSerializer(
            data={
                "new_password": "NewPassword123",
            }
        )

        self.assertFalse(serializer.is_valid())
        self.assertIn("old_password", serializer.errors)

    def test_change_password_serializer_requires_new_password(self):
        serializer = ChangePasswordSerializer(
            data={
                "old_password": "OldPassword123",
            }
        )

        self.assertFalse(serializer.is_valid())
        self.assertIn("new_password", serializer.errors)


class ResetPasswordSerializerTests(TestCase):

    def test_reset_password_accepts_matching_passwords(self):
        serializer = ResetPasswordSerializer(
            data={
                "new_password": "NewPassword123",
                "new_password_confirm": "NewPassword123",
            }
        )

        self.assertTrue(serializer.is_valid())

    def test_reset_password_rejects_different_passwords(self):
        serializer = ResetPasswordSerializer(
            data={
                "new_password": "NewPassword123",
                "new_password_confirm": "DifferentPassword123",
            }
        )

        self.assertFalse(serializer.is_valid())
        self.assertIn("error", serializer.errors)

    def test_reset_password_requires_minimum_password_length(self):
        serializer = ResetPasswordSerializer(
            data={
                "new_password": "123",
                "new_password_confirm": "123",
            }
        )

        self.assertFalse(serializer.is_valid())
        self.assertIn("new_password_confirm", serializer.errors)


# ============================================================
# OTP Handler Tests
# ============================================================

class NormalizePhoneTests(TestCase):

    def test_normalize_iranian_international_phone(self):
        result = normalize_phone("+989120000000")

        self.assertEqual(result, "09120000000")

    def test_normalize_phone_removes_spaces(self):
        result = normalize_phone(" 09120000000 ")

        self.assertEqual(result, "09120000000")

    def test_normalize_local_phone_without_changes(self):
        result = normalize_phone("09120000000")

        self.assertEqual(result, "09120000000")


class OTPHandlerTests(TestCase):

    @patch("accounts.otp_handler.redis_client")
    def test_store_otp(self, mock_redis):
        store_otp(
            phone_number="09120000000",
            purpose="LOGIN",
            code="123456",
        )

        mock_redis.setex.assert_called_once_with(
            "otp:login:09120000000",
            300,
            "123456",
        )

    @patch("accounts.otp_handler.redis_client")
    def test_can_send_otp_first_request(self, mock_redis):
        mock_redis.get.return_value = None
        mock_redis.incr.return_value = 1

        result = can_send_otp(
            phone_number="09120000000",
            purpose="LOGIN",
        )

        self.assertTrue(result)

        mock_redis.incr.assert_called_once_with(
            "otp:send:login:09120000000"
        )

        mock_redis.expire.assert_called_once_with(
            "otp:send:login:09120000000",
            300,
        )

    @patch("accounts.otp_handler.redis_client")
    def test_can_send_otp_rejects_after_maximum_requests(self, mock_redis):
        mock_redis.get.return_value = "3"

        result = can_send_otp(
            phone_number="09120000000",
            purpose="LOGIN",
            max_send=3,
        )

        self.assertFalse(result)

        mock_redis.incr.assert_not_called()

    @patch("accounts.otp_handler.redis_client")
    def test_verify_correct_otp(self, mock_redis):
        mock_redis.get.side_effect = [
            None,
            "123456",
        ]

        result = verify_code_from_redis(
            phone_number="09120000000",
            purpose="LOGIN",
            code="123456",
        )

        self.assertEqual(result, "success")

        mock_redis.delete.assert_any_call(
            "otp:login:09120000000"
        )

        mock_redis.delete.assert_any_call(
            "otp:attempt:login:09120000000"
        )

    @patch("accounts.otp_handler.redis_client")
    def test_verify_wrong_otp(self, mock_redis):
        mock_redis.get.side_effect = [
            None,
            "123456",
        ]

        result = verify_code_from_redis(
            phone_number="09120000000",
            purpose="LOGIN",
            code="654321",
        )

        self.assertEqual(result, "invalid_code")

    @patch("accounts.otp_handler.redis_client")
    def test_verify_otp_after_maximum_attempts(self, mock_redis):
        mock_redis.get.return_value = "3"

        result = verify_code_from_redis(
            phone_number="09120000000",
            purpose="LOGIN",
            code="123456",
            max_attempts=3,
        )

        self.assertEqual(result, "too_many_attempts")

        mock_redis.incr.assert_not_called()

    @patch("accounts.otp_handler.redis_client")
    def test_verify_otp_increments_attempt_counter(self, mock_redis):
        mock_redis.get.side_effect = [
            None,
            None,
        ]
        mock_redis.incr.return_value = 1

        result = verify_code_from_redis(
            phone_number="09120000000",
            purpose="LOGIN",
            code="123456",
        )

        self.assertEqual(result, "invalid_code")

        mock_redis.incr.assert_called_once_with(
            "otp:attempt:login:09120000000"
        )

        mock_redis.expire.assert_called_once_with(
            "otp:attempt:login:09120000000",
            300,
        )

    @patch("accounts.otp_handler.redis_client")
    def test_can_send_reset_email_first_request(self, mock_redis):
        mock_redis.get.return_value = None

        result = can_send_reset_email(
            user_id=10,
            limit=3,
            window=timedelta(minutes=5),
        )

        self.assertTrue(result)

        mock_redis.setex.assert_called_once_with(
            "password_reset:10",
            300,
            1,
        )

    @patch("accounts.otp_handler.redis_client")
    def test_can_send_reset_email_rejects_after_limit(self, mock_redis):
        mock_redis.get.return_value = "3"

        result = can_send_reset_email(
            user_id=10,
            limit=3,
        )

        self.assertFalse(result)

        mock_redis.incr.assert_not_called()

    @patch("accounts.otp_handler.redis_client")
    def test_can_send_reset_email_increments_existing_counter(
        self,
        mock_redis,
    ):
        mock_redis.get.return_value = "1"

        result = can_send_reset_email(
            user_id=10,
            limit=3,
        )

        self.assertTrue(result)

        mock_redis.incr.assert_called_once_with(
            "password_reset:10"
        )


# ============================================================
# Task Tests
# ============================================================

class OTPTaskTests(TestCase):

    @patch("accounts.tasks.send_sms_code.delay")
    @patch("accounts.tasks.store_otp")
    @patch("accounts.tasks.random.randint")
    def test_send_otp_to_user(
        self,
        mock_randint,
        mock_store_otp,
        mock_delay,
    ):
        mock_randint.return_value = 123456

        result = send_otp_to_user(
            phone_number="+989120000000",
            purpose="LOGIN",
        )

        self.assertEqual(result, "123456")

        mock_store_otp.assert_called_once_with(
            "09120000000",
            "login",
            "123456",
        )

        mock_delay.assert_called_once_with(
            "09120000000",
            "123456",
        )


# ============================================================
# API View Tests
# ============================================================

class AuthenticationViewTests(APITestCase):

    def setUp(self):
        self.client = APIClient()

        self.user = CustomUser.objects.create_user(
            phone_number="09120000000",
            email="barbod@example.com",
            password="OldPassword123",
            first_name="Barbod",
            last_name="Jangjo",
        )

    # --------------------------------------------------------
    # Registration
    # --------------------------------------------------------

    @patch("accounts.views.send_otp")
    def test_user_registration(self, mock_send_otp):
        mock_send_otp.return_value = "123456"

        response = self.client.post(
            reverse("user_register"),
            {
                "phone_number": "09121111111",
            },
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_201_CREATED,
        )

        self.assertTrue(
            CustomUser.objects.filter(
                phone_number="09121111111"
            ).exists()
        )

        self.assertEqual(
            response.data["otp"]["purpose"],
            "SIGNUP",
        )

        self.assertIn("tokens", response.data)

        mock_send_otp.assert_called_once()

    def test_registration_with_duplicate_phone_number(self):
        response = self.client.post(
            reverse("user_register"),
            {
                "phone_number": "09120000000",
            },
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_400_BAD_REQUEST,
        )

    # --------------------------------------------------------
    # Send OTP
    # --------------------------------------------------------

    @patch("accounts.views.send_otp_to_user")
    @patch("accounts.views.can_send_otp")
    def test_send_otp_success(
        self,
        mock_can_send,
        mock_send_otp,
    ):
        mock_can_send.return_value = True
        mock_send_otp.return_value = "123456"

        response = self.client.post(
            reverse("send_otp"),
            {
                "phone_number": "+989120000000",
            },
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_200_OK,
        )

        self.assertEqual(
            response.data["OTP"],
            "123456",
        )

        mock_can_send.assert_called_once_with(
            "09120000000",
            purpose="LOGIN",
        )

        mock_send_otp.assert_called_once_with(
            "09120000000",
            purpose="LOGIN",
        )

    @patch("accounts.views.can_send_otp")
    def test_send_otp_rate_limit(
        self,
        mock_can_send,
    ):
        mock_can_send.return_value = False

        response = self.client.post(
            reverse("send_otp"),
            {
                "phone_number": "09120000000",
            },
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_429_TOO_MANY_REQUESTS,
        )

        self.assertIn("error", response.data)

    def test_send_otp_rejects_invalid_phone_length(self):
        response = self.client.post(
            reverse("send_otp"),
            {
                "phone_number": "0912",
            },
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_400_BAD_REQUEST,
        )

    # --------------------------------------------------------
    # Change Password
    # --------------------------------------------------------

    def test_change_password_requires_authentication(self):
        response = self.client.patch(
            reverse("password_change"),
            {
                "old_password": "OldPassword123",
                "new_password": "NewPassword123",
            },
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_401_UNAUTHORIZED,
        )

    def test_change_password_success(self):
        self.client.force_authenticate(user=self.user)

        response = self.client.patch(
            reverse("password_change"),
            {
                "old_password": "OldPassword123",
                "new_password": "NewPassword123",
            },
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_200_OK,
        )

        self.user.refresh_from_db()

        self.assertTrue(
            self.user.check_password("NewPassword123")
        )

        self.assertFalse(
            self.user.check_password("OldPassword123")
        )

    def test_change_password_with_wrong_old_password(self):
        self.client.force_authenticate(user=self.user)

        response = self.client.patch(
            reverse("password_change"),
            {
                "old_password": "WrongPassword123",
                "new_password": "NewPassword123",
            },
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_400_BAD_REQUEST,
        )

        self.assertIn(
            "old_password",
            response.data,
        )

    def test_change_password_rejects_weak_password(self):
        self.client.force_authenticate(user=self.user)

        response = self.client.patch(
            reverse("password_change"),
            {
                "old_password": "OldPassword123",
                "new_password": "123",
            },
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_400_BAD_REQUEST,
        )

        self.assertIn(
            "new_password",
            response.data,
        )

    # --------------------------------------------------------
    # Reset Password
    # --------------------------------------------------------

    def test_reset_password_requires_authentication(self):
        response = self.client.post(
            reverse("reset-password"),
            {
                "new_password": "NewPassword123",
                "new_password_confirm": "NewPassword123",
            },
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_401_UNAUTHORIZED,
        )

    def test_reset_password_success(self):
        self.client.force_authenticate(user=self.user)

        response = self.client.post(
            reverse("reset-password"),
            {
                "new_password": "NewPassword123",
                "new_password_confirm": "NewPassword123",
            },
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_200_OK,
        )

        self.user.refresh_from_db()

        self.assertTrue(
            self.user.check_password("NewPassword123")
        )

    def test_reset_password_rejects_different_passwords(self):
        self.client.force_authenticate(user=self.user)

        response = self.client.post(
            reverse("reset-password"),
            {
                "new_password": "NewPassword123",
                "new_password_confirm": "DifferentPassword123",
            },
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_400_BAD_REQUEST,
        )

    # --------------------------------------------------------
    # Password Reset Request
    # --------------------------------------------------------

    @override_settings(
        DEFAULT_FROM_EMAIL="no-reply@example.com"
    )
    @patch("accounts.views.send_mail")
    @patch("accounts.views.can_send_reset_email")
    def test_password_reset_request_success(
        self,
        mock_can_send_reset,
        mock_send_mail,
    ):
        mock_can_send_reset.return_value = True

        response = self.client.post(
            reverse("password_reset_api"),
            {
                "phone_number": "09120000000",
            },
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_200_OK,
        )

        self.assertIn(
            "detail",
            response.data,
        )

        mock_send_mail.assert_called_once()

    def test_password_reset_request_user_not_found(self):
        response = self.client.post(
            reverse("password_reset_api"),
            {
                "phone_number": "09129999999",
            },
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_404_NOT_FOUND,
        )

    @override_settings(
        DEFAULT_FROM_EMAIL="no-reply@example.com"
    )
    @patch("accounts.views.send_mail")
    @patch("accounts.views.can_send_reset_email")
    def test_password_reset_request_rate_limit(
        self,
        mock_can_send_reset,
        mock_send_mail,
    ):
        mock_can_send_reset.return_value = False

        response = self.client.post(
            reverse("password_reset_api"),
            {
                "phone_number": "09120000000",
            },
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_429_TOO_MANY_REQUESTS,
        )

        mock_send_mail.assert_not_called()