import logging
from django.dispatch import receiver
from django.db.models.signals import post_save, pre_save
from django.utils.translation import gettext_lazy as _

from course import models
from .models import Notification
from points.models import UserPoint


@receiver(post_save, sender=models.AdminExerciseFeedback)
def notification_for_adminfeedback(sender, instance, created, *args, **kwargs):
    if created:
        logging.info(f"{instance.user} has received feedback for exercise {instance.exercise.title}")
        Notification.objects.create(
            user=instance.user,
            notification_type='EXERCISE',
            title=_('New mission for you💥'),
            message=_(f'Feed back for «{instance.exercise.title}» has been ready! 🎯'),
            slug = instance.exercise.slug,
            
        )

@receiver(post_save, sender=models.QuizUserStatus)
def notification_for_quiz_status(sender, instance, created, *args, **kwargs):
    if created and instance.is_pass:
        Notification.objects.create(
            user=instance.user,
            notification_type='QUIZ',
            title=_('Mission pass successfully! 🏆'),
            message=_(f'You passed your quiz «{instance.quiz.title}») successfully🚀'),
            slug=instance.quiz.slug,
            )
@receiver(pre_save, sender=models.UserChapterStatus)
def notifications_for_chapter_status(sender, instance, **kwargs):
    if instance.is_lock == True:
        Notification.objects.create(
            user= instance.user,
            notification_type='CHANGE_STATUS',
            title= _('New chapter has been unlocked 🔓'),
            message=_(f'Chapter {instance.chapter.title} has been unlocked'),
            chapter_id= instance.chapter.id,
            chapter_slug= instance.chapter.slug,
        )

@receiver(post_save, sender=UserPoint)
def notification_for_user_point(sender, instance, created, *args, **kwargs):
    if created:
        Notification.objects.create(
            user=instance.user,
            notification_type='POINTS',
            title=_('New points awarded!'),
            message=f'You have new {instance.points} has been awarded',
        )

@receiver(post_save, sender = challenges.UserMissionStatus)
def user_mission_status_points_notification(sender, instance, **args,):
    logging.info(f'notification signal before if')
    if instance.admin_points != None:
        logging.info(f'enetering the if')
        notification = Notification.objects.create(
            user=instance.user,
            notification_type = 'CHALLENGE',
            title='امتیاز جدید! 🎉',
            message = f'تبریک می گم! {instance.admin_points} به امتیازات اضافه شد'
        )
