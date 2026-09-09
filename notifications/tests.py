from django.test import TestCase
from django.contrib.auth import get_user_model

from rest_framework.test import APIClient

from .models import Notification
from .serializers import NotificationSerializer


User = get_user_model()


class NotificationTestMixin:

    def create_user(self, phone_number="09120000001"):
        return User.objects.create_user(
            phone_number=phone_number,
            password="TestPassword123!",
        )

    def create_notification(self, user):
        return Notification.objects.create(
            user=user,
            notification_type="QUIZ",
            title="Quiz Result",
            message="Your quiz has been evaluated.",
            slug="quiz-result",
        )


class NotificationModelTests(NotificationTestMixin, TestCase):

    def test_notification_creation(self):
        user = self.create_user()

        notification = self.create_notification(user)

        self.assertEqual(notification.user, user)
        self.assertEqual(
            notification.notification_type,
            "QUIZ",
        )
        self.assertFalse(notification.is_read)

    def test_notification_default_is_unread(self):
        user = self.create_user()

        notification = self.create_notification(user)

        self.assertFalse(notification.is_read)

    def test_notification_can_be_marked_as_read(self):
        user = self.create_user()

        notification = self.create_notification(user)

        notification.is_read = True
        notification.save()

        notification.refresh_from_db()

        self.assertTrue(notification.is_read)

    def test_notification_string_representation(self):
        user = self.create_user()

        notification = self.create_notification(user)

        self.assertIn("QUIZ", str(notification))


class NotificationSerializerTests(NotificationTestMixin, TestCase):

    def test_notification_serializer(self):
        user = self.create_user()

        notification = self.create_notification(user)

        serializer = NotificationSerializer(notification)

        self.assertEqual(
            serializer.data["title"],
            "Quiz Result",
        )

        self.assertEqual(
            serializer.data["message"],
            "Your quiz has been evaluated.",
        )

        self.assertFalse(
            serializer.data["is_read"]
        )


class NotificationAPITests(NotificationTestMixin, TestCase):

    def setUp(self):
        self.client = APIClient()
        self.user = self.create_user()
        self.notification = self.create_notification(
            self.user
        )

    def test_unauthenticated_user_cannot_access_notifications(self):
        response = self.client.get(
            "/notifications/"
        )

        self.assertIn(
            response.status_code,
            [401, 403],
        )

    def test_user_only_receives_own_notifications(self):
        other_user = self.create_user(
            "09120000002"
        )

        other_notification = self.create_notification(
            other_user
        )

        self.client.force_authenticate(
            user=self.user
        )

        response = self.client.get(
            "/notifications/"
        )

        if response.status_code == 200:
            returned_ids = [
                item["id"]
                for item in response.data
            ]

            self.assertIn(
                self.notification.id,
                returned_ids,
            )

            self.assertNotIn(
                other_notification.id,
                returned_ids,
            )

    def test_user_can_mark_own_notification_as_read(self):
        self.client.force_authenticate(
            user=self.user
        )

        response = self.client.patch(
            f"/notifications/{self.notification.id}/",
            {"is_read": True},
            format="json",
        )

        if response.status_code == 200:
            self.notification.refresh_from_db()

            self.assertTrue(
                self.notification.is_read
            )

    def test_user_cannot_modify_another_users_notification(self):
        other_user = self.create_user(
            "09120000002"
        )

        other_notification = self.create_notification(
            other_user
        )

        self.client.force_authenticate(
            user=self.user
        )

        response = self.client.patch(
            f"/notifications/{other_notification.id}/",
            {"is_read": True},
            format="json",
        )

        self.assertIn(
            response.status_code,
            [403, 404],
        )