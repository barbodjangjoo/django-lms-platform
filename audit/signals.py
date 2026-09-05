# audits/signals.py
import datetime
from django.db.models.signals import post_save
from django.dispatch import receiver
from django.utils import timezone
from .models import Audit


@receiver(post_save, sender=Audit)
def clean_old_audits(sender, instance, **kwargs):
    now = timezone.now()

    two_days_ago = now - datetime.timedelta(days=2)
    Audit.objects.filter(
        http_response_status_code=200,
        log_datetime__lt=two_days_ago
    ).delete()

    two_weeks_ago = now - datetime.timedelta(days=14)
    Audit.objects.exclude(
            http_response_status_code=200
        ).filter(
            log_datetime__lt=two_weeks_ago
        ).delete()

