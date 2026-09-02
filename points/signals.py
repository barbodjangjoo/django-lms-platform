from django.db.models.signals import pre_save, post_save
from django.dispatch import receiver
from accounts.models import CustomUser
# from course.models import UserExerciseStatus, FinalExamUserAnswer
# from notifications.models import Notification
from .models import UserPoint
# from .services import reward_points_for_exercise, reward_points_for_final_exam

# logger = logging.getLogger(__name__)

@receiver(post_save, sender=CustomUser)
def points_handler_profile(instance, created, **kwargs):
    if created:
        UserPoint.objects.create(
            user=instance,
            points=1000,
            activity_type='PROFILE',
            activity_id=instance.id,
)
    
@receiver(pre_save, sender=CustomUser)
def points_handler_completation(instance, **kwargs):
    PROFILE_FIELD_POINTS = {
    'profile_picture': 100,
    'cover_profile': 100,
    'first_name': 100,
    'last_name': 100,
    'birth_date': 100,
    'gender': 100,
    'city': 100,
    'address': 100,
    'marital_status': 100,
    'educational_status': 100,
    'national_id': 100,
    'national_card': 100,
    'phone_number': 100,
    'email': 100,
    'job_status': 100,
    'job_title': 100,
    'job_experience': 100,
    'find': 100,
    'join': 100
}
    old_instance = CustomUser.objects.filter(id=instance.id).first()
    if old_instance:
        if old_instance.profile_picture != instance.profile_picture:
            UserPoint.objects.get_or_create(
                user=instance,
                activity_type='PROFILE',
                activity_id='profile_picture',
                defaults={
                    'points': PROFILE_FIELD_POINTS.get('profile_picture', 0),
                    'details': 'Updated profile picture',
                }
            )
        elif old_instance.address != instance.address:
            UserPoint.objects.get_or_create(
                user=instance,
                activity_type='PROFILE',
                activity_id='address',
                defaults={
                    'points': PROFILE_FIELD_POINTS.get('address', 0),
                    'details': 'Updated address',
                }
            )
        elif old_instance.marital_status != instance.marital_status:
            UserPoint.objects.get_or_create(
                user=instance,
                activity_type='PROFILE',
                activity_id='marital_status',
                defaults={
                    'points': PROFILE_FIELD_POINTS.get('marital_status', 0),
                    'details': 'Updated marital status',
                }
            )
        elif old_instance.educational_status != instance.educational_status:
            UserPoint.objects.get_or_create(
                user=instance,
                activity_type='PROFILE',
                activity_id='educational_status',
                defaults={
                    'points': PROFILE_FIELD_POINTS.get('educational_status', 0),
                    'details': 'Updated educational status',
                }
            )
        elif old_instance.national_id != instance.national_id:
            UserPoint.objects.get_or_create(
                user=instance,
                activity_type='PROFILE',
                activity_id='national_id',
                defaults={
                    'points': PROFILE_FIELD_POINTS.get('national_id', 0),
                    'details': 'Updated national ID',
                }
            )
        elif old_instance.national_card != instance.national_card:
            UserPoint.objects.get_or_create(
                user=instance,
                activity_type='PROFILE',
                activity_id='national_card',
                defaults={
                    'points': PROFILE_FIELD_POINTS.get('national_card', 0),
                    'details': 'Updated national card',
                }
            )
        elif old_instance.job_status != instance.job_status:
            UserPoint.objects.get_or_create(
                user=instance,
                activity_type='PROFILE',
                activity_id='job_status',
                defaults={
                    'points': PROFILE_FIELD_POINTS.get('job_status', 0),
                    'details': 'Updated job status',
                }
            )
        elif old_instance.job_title != instance.job_title:
            UserPoint.objects.get_or_create(
                user=instance,
                activity_type='PROFILE',
                activity_id='job_title',
                defaults={
                    'points': PROFILE_FIELD_POINTS.get('job_title', 0),
                    'details': 'Updated job title',
                }
            )
        elif old_instance.job_experience != instance.job_experience:
            UserPoint.objects.get_or_create(
                user=instance,
                activity_type='PROFILE',
                activity_id='job_experience',
                defaults={
                    'points': PROFILE_FIELD_POINTS.get('job_experience', 0),
                    'details': 'Updated job experience',
                }
            )
            

        

#     Handle exercise status updates and award points when approved
#     """
#     try:
#         old_instance = sender.objects.get(pk=instance.pk)
#         # Check if status changed from pending and points were assigned
#         if (old_instance.status == 'pending' and 
#             instance.status != 'pending' and 
#             instance.points is not None):
            
#             # Award points and create notification
#             reward_points_for_exercise(instance.user, instance)
            
#             # Create status change notification with slug
#             Notification.objects.create(
#                 user=instance.user,
#                 notification_type='EXERCISE',
#                 title='تمرین شما تصحیح شد! ✅',
#                 message=f'تمرین "{instance.exercise.title}" با {instance.points} امتیاز تصحیح شد!',
#                 slug=instance.exercise.slug,
#                 chapter_slug = instance.exercise.lesson.chapter.slug,
#                 lesson_slug = instance.exercise.lesson.slug,
#                 course_slug = instance.exercise.lesson.chapter.course.slug
#             )
        
#     except sender.DoesNotExist:
#         pass  # New instance, no need to handle

# @receiver(pre_save, sender=FinalExamUserAnswer)
# def handle_final_exam_status_update(sender, instance, **kwargs):
#     try:
#         old_instance = sender.objects.get(pk=instance.pk)
#         logger.debug(f"Old exam status: {old_instance.exam_status}, New exam status: {instance.exam_status}")
#         logger.debug(f"Points: {instance.points}")
#         # Check if exam status changed from pending and points were assigned
#         if (old_instance.exam_status == 'pending' and
#             instance.exam_status != 'pending' and 
#             instance.points is not None):

#             reward_points_for_final_exam(instance.user, instance)

#             Notification.objects.create(
#                 user=instance.user,
#                 notification_type='EXAM',
#                 title="امیحانت تصحیح شد",
#                 message=f'تمرین "{instance.final_exam.title}" با {instance.points} امتیاز تصحیح شد!',
#                 slug=instance.final_exam.slug,
#                 chapter_slug = instance.final_exam.chapter.slug,
#                 course_slug = instance.final_exam.chapter.course.slug
#             )
#     except sender.DoesNotExist:
#         pass