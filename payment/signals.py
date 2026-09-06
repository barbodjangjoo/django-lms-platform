from django.dispatch import receiver
from django.db.models.signals import post_save
import logging

from . import models
from course import models as courses


@receiver(post_save, sender=models.Factor)
def handle_access_for_course(sender, instance, created, **kwargs):
    if instance.payment_status == 'successful':
        user = instance.user
        purchase_item = models.PurchaseItem.objects.get(
            factor=instance,
            user=user,
            payment_status = 'successful'
            )
        logging.info(f'{purchase_item} is found for signal')



@receiver(post_save, sender=models.PurchaseItem)
def create_user_challenge_access(sender, instance, created, **kwargs):
    if instance.type == 'course':
        

        course = courses.Course.objects.get(id=instance.reference_id)
        logging.info(f'found challenge for user_challenge_Status signal :{course}!')

        user_course_staus, _= courses.CourseUserStatus.objects.get_or_create(
            course=course,
            user=instance.user,
        )

        logging.info(f'create user_course in signal : {user_course_staus}')