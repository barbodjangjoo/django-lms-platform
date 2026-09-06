from django.db import models
from django.contrib.auth import get_user_model


class Factor(models.Model):
    PAYMENT_CHOICES =[
        ('pending', 'Pending'),
        ('successful', 'Successful'),
        ('failed', 'Failed')
    ]

    user = models.ForeignKey(get_user_model(), on_delete=models.CASCADE)
    payment_status = models.CharField(max_length=10, choices=PAYMENT_CHOICES, default="pending")
    # factor_id = models.UUIDField()
    # purchase= models.ForeignKey('PurchaseItem', on_delete=models.PROTECT)
    datetime_transaction = models.DateTimeField(blank=True, null=True)
    total_price = models.IntegerField()
    datetime_created = models.DateTimeField(auto_now_add=True)
    datetime_modified = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.user} - {self.payment_status}"

class PurchaseItem(models.Model):
    PAYMENT_CHOICES =[
        ('pending', 'Pending'),
        ('successful', 'Successful'),
        ('failed', 'Failed')
    ]
    user= models.ForeignKey(get_user_model(), on_delete=models.CASCADE)
    factor = models.ForeignKey(Factor, on_delete=models.CASCADE, related_name='purchase_items')
    reference_id = models.CharField(max_length=3)
    price = models.IntegerField()
    payment_status = models.CharField(max_length=10, choices=PAYMENT_CHOICES, default='pending')

    datetime_created = models.DateTimeField(auto_now_add=True)
    datetime_modified = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.user} - {self.type}"
    
class Transaction(models.Model):
    factor = models.ForeignKey(Factor, on_delete=models.CASCADE)
    user = models.ForeignKey(get_user_model(), on_delete=models.CASCADE)
    payment_authority = models.CharField(max_length=36, blank=True, null=True)
    code = models.IntegerField(blank=True, null=True)
    errors = models.TextField(blank=True, null=True)
    zarinpal_ref_id = models.CharField(max_length=150, blank=True, null=True)
    zarinpal_data = models.TextField( blank=True, null=True)
    payment_datetime = models.DateTimeField(auto_now_add=True)

def __str__(self):
    return f'{self.user} - {self.factor} Transaction'