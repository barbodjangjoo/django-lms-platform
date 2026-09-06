from django.contrib.auth import get_user_model
from django.db import IntegrityError
from django.test import TestCase

from .models import UserPoint
from .serializers import UserPointSerializer


User = get_user_model()


class UserPointModelTests(TestCase):

    def setUp(self):
        self.user = User.objects.create_user(
            username="barbod",
            password="test-password",
        )

    def test_user_point_is_created(self):
        point = UserPoint.objects.create(
            user=self.user,
            points=500,
            activity_type="QUIZ",
            activity_id="quiz-1",
            details="Passed quiz",
        )

        self.assertEqual(point.points, 500)
        self.assertEqual(point.activity_type, "QUIZ")
        self.assertEqual(point.activity_id, "quiz-1")

    def test_user_point_default_points_is_zero(self):
        point = UserPoint.objects.create(
            user=self.user,
            activity_type="PROFILE",
            activity_id="profile-complete",
        )

        self.assertEqual(point.points, 0)

    def test_user_point_activity_is_unique(self):
        UserPoint.objects.create(
            user=self.user,
            points=500,
            activity_type="QUIZ",
            activity_id="quiz-1",
        )

        with self.assertRaises(IntegrityError):
            UserPoint.objects.create(
                user=self.user,
                points=350,
                activity_type="QUIZ",
                activity_id="quiz-1",
            )

    def test_same_activity_type_can_have_different_activity_ids(self):
        UserPoint.objects.create(
            user=self.user,
            points=500,
            activity_type="QUIZ",
            activity_id="quiz-1",
        )

        UserPoint.objects.create(
            user=self.user,
            points=350,
            activity_type="QUIZ",
            activity_id="quiz-2",
        )

        self.assertEqual(
            UserPoint.objects.filter(
                user=self.user,
                activity_type="QUIZ",
            ).count(),
            2,
        )

    def test_different_users_can_have_same_activity(self):
        second_user = User.objects.create_user(
            username="another-user",
            password="test-password",
        )

        UserPoint.objects.create(
            user=self.user,
            points=500,
            activity_type="QUIZ",
            activity_id="quiz-1",
        )

        UserPoint.objects.create(
            user=second_user,
            points=500,
            activity_type="QUIZ",
            activity_id="quiz-1",
        )

        self.assertEqual(UserPoint.objects.count(), 2)


class UserPointSerializerTests(TestCase):

    def setUp(self):
        self.user = User.objects.create_user(
            username="barbod",
            password="test-password",
        )

        UserPoint.objects.create(
            user=self.user,
            points=500,
            activity_type="QUIZ",
            activity_id="quiz-1",
        )

        UserPoint.objects.create(
            user=self.user,
            points=350,
            activity_type="EXERCISE",
            activity_id="exercise-1",
        )

    def test_serializer_returns_total_points(self):
        point = UserPoint.objects.first()

        serializer = UserPointSerializer(point)

        self.assertEqual(serializer.data["sum_points"], 850)

    def test_serializer_contains_expected_fields(self):
        point = UserPoint.objects.first()

        serializer = UserPointSerializer(point)

        self.assertEqual(
            set(serializer.data.keys()),
            {
                "id",
                "user",
                "points",
                "activity_type",
                "activity_id",
                "details",
                "created_at",
                "sum_points",
            },
        )