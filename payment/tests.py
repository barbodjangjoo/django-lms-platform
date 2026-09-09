from django.test import TestCase
from django.contrib.auth import get_user_model

from .models import Factor, PurchaseItem, Transaction
from .serializers import (
    PurchaseItemInputSerializer,
    FactorSerializer,
    FactorListSerializer,
)


User = get_user_model()


class PaymentTestMixin:

    def create_user(self, phone_number="09120000001"):
        return User.objects.create_user(
            phone_number=phone_number,
            password="TestPassword123!",
        )


class FactorModelTests(PaymentTestMixin, TestCase):

    def test_factor_creation(self):
        user = self.create_user()

        factor = Factor.objects.create(
            user=user,
            total_price=1000000,
        )

        self.assertEqual(factor.user, user)
        self.assertEqual(factor.total_price, 1000000)
        self.assertEqual(factor.payment_status, "pending")

    def test_factor_default_status_is_pending(self):
        user = self.create_user()

        factor = Factor.objects.create(
            user=user,
            total_price=500000,
        )

        self.assertEqual(
            factor.payment_status,
            "pending",
        )

    def test_factor_string_representation(self):
        user = self.create_user()

        factor = Factor.objects.create(
            user=user,
            total_price=500000,
        )

        self.assertIn(user.phone_number, str(factor))


class PurchaseItemModelTests(PaymentTestMixin, TestCase):

    def test_purchase_item_creation(self):
        user = self.create_user()

        factor = Factor.objects.create(
            user=user,
            total_price=1000000,
        )

        item = PurchaseItem.objects.create(
            user=user,
            factor=factor,
            reference_id="1",
            price=1000000,
        )

        self.assertEqual(item.factor, factor)
        self.assertEqual(item.reference_id, "1")
        self.assertEqual(item.price, 1000000)
        self.assertEqual(item.payment_status, "pending")

    def test_purchase_item_belongs_to_factor(self):
        user = self.create_user()

        factor = Factor.objects.create(
            user=user,
            total_price=1000000,
        )

        PurchaseItem.objects.create(
            user=user,
            factor=factor,
            reference_id="1",
            price=1000000,
        )

        self.assertEqual(
            factor.purchase_items.count(),
            1,
        )


class TransactionModelTests(PaymentTestMixin, TestCase):

    def test_transaction_creation(self):
        user = self.create_user()

        factor = Factor.objects.create(
            user=user,
            total_price=1000000,
        )

        transaction = Transaction.objects.create(
            factor=factor,
            user=user,
            payment_authority="AUTH-123",
        )

        self.assertEqual(transaction.factor, factor)
        self.assertEqual(transaction.user, user)
        self.assertEqual(
            transaction.payment_authority,
            "AUTH-123",
        )

    def test_transaction_can_store_zarinpal_reference(self):
        user = self.create_user()

        factor = Factor.objects.create(
            user=user,
            total_price=1000000,
        )

        transaction = Transaction.objects.create(
            factor=factor,
            user=user,
            payment_authority="AUTH-123",
            zarinpal_ref_id="REF-123",
            code=100,
        )

        self.assertEqual(
            transaction.zarinpal_ref_id,
            "REF-123",
        )
        self.assertEqual(transaction.code, 100)


class PaymentSerializerTests(PaymentTestMixin, TestCase):

    def test_purchase_item_input_serializer(self):
        serializer = PurchaseItemInputSerializer(
            data={"reference_id": "10"}
        )

        self.assertTrue(serializer.is_valid())
        self.assertEqual(
            serializer.validated_data["reference_id"],
            "10",
        )

    def test_purchase_item_input_serializer_requires_reference_id(self):
        serializer = PurchaseItemInputSerializer(
            data={}
        )

        self.assertFalse(serializer.is_valid())

    def test_factor_serializer(self):
        user = self.create_user()

        factor = Factor.objects.create(
            user=user,
            total_price=1000000,
        )

        serializer = FactorSerializer(factor)

        self.assertEqual(
            serializer.data["total_price"],
            1000000,
        )

    def test_factor_list_serializer(self):
        user = self.create_user()

        factor = Factor.objects.create(
            user=user,
            total_price=1000000,
        )

        serializer = FactorListSerializer(factor)

        self.assertIn(
            "purchase_items",
            serializer.data,
        )