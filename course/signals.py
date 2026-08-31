from django.db.models.signals import post_save, pre_save
from django.dispatch import receiver

import logging

# from notifications.models import Notification
from . import models



# # def create_points_and_notification(user, points, activity_type, title, instance, ):
# #     """Helper function to create points and notification"""
# #     UserPoint.objects.get_or_create(
# #         user=user,
# #         activity_type=activity_type,
# #         activity_id=f"{activity_type}_{instance}",
# #         defaults={
# #             'points': points,
# #             'details': f"{activity_type}: {instance}"
# #         }
# #     )

# #     Notification.objects.create(
# #         user=user,
# #         notification_type=activity_type,
# #         title=title,
# #         message=f'شما {points} امتیاز برای {instance} دریافت کردید!',
# #     )

# @receiver(post_save, sender=UserExerciseStatus)
# def handle_notification_exercise_status(sender, instance, created, **kwargs):
#     logging.info(f"Status changed for user {instance.user} for exercise {instance.exercise.title}")
#     if instance.is_lock == False:
#         # جلوگیری از ساخت چندباره
#         if not models.AdminExerciseFeedback.objects.filter(user=instance.user, exercise=instance.exercise).exists():
#             logging.info(f"Creating notification for user {instance.user} for exercise {instance.exercise.title}")
#             models.AdminExerciseFeedback.objects.create(
#                 user=instance.user,
#                 exercise=instance.exercise,
#                 feedback_text="سلام خیلی خوش اومدی به این تمرین! امیدوارم ازش لذت ببری. اگر سوالی داشتی، حتما بپرس!",
#             )
#             logging.info(f"adminfeedback created for user {instance.user} for exercise {instance.exercise.title}")



# # @receiver(post_save, sender=UserExerciseStatus)
# # def handle_exercise_status_update(sender, instance, **kwargs):
# #     if instance.status == 'approved':
# #         exercise_link = f"/courses/exercise/{instance.exercise.title}"

# # @receiver(pre_save, sender=FinalExamUserAnswer)
# # def handle_final_exam_status_update(sender, instance, **kwargs):
# #     try:
# #         old_instance = sender.objects.get(pk=instance.pk)
# #         if (old_instance.exam_status != 'approved' and
# #             instance.exam_status == 'approved' and
# #             instance.points is not None):

# #             reward_points_for_final_exam(instance.user, instance)

# #             Notification.objects.create(
# #                 user=instance.user,
# #                 notification_type='FINAL_EXAM',
# #                 title="آزمون نهایی قبول شد!",
# #                 message=f' {instance.final_exam.title} با {instance.points} امتیاز تایید شد!',
# #                 slug = instance.final_exam.slug,
# #                 chapter_slug = instance.final_exam.chapter.slug,
# #                 course_slug = instance.final_exam.chapter.course.slug,
# #             )
# #     except sender.DoesNotExist:
# #         pass


# @receiver(post_save, sender=models.Exercise)
# def create_exercise_status_for_users(sender, instance, created, **kwargs):
#     if created:
#         User = get_user_model()
#         status_objects = [
#             models.UserExerciseStatus(
#                 user=user,
#                 exercise=instance,
#                 is_lock=True,
#                 is_seen=False
#             )
#             for user in User.objects.all()
#         ]
#         models.UserExerciseStatus.objects.bulk_create(status_objects)

# @receiver(post_save, sender=models.QuizQuestion)
# def create_Quiz_status_for_users(sender, instance, created, **kwargs):
#     if created:
#         users = CustomUser.objects.all()
#         quiz = models.QuizQuestion.objects.filter(quiz=instance.quiz).all()

#         for user in users:
#             models.QuizUserAnswer.objects.get_or_create(
#                 user=user,
#                 quiz=instance.quiz,
#                 question=instance,
#             )
#             logging.info(f"Quiz answer created for user {user} and question {instance}")
#         logging.info("Quiz answers creation completed")

@receiver(post_save, sender=models.UserExerciseStatus)
def handle_chapter_is_lock(sender, instance, **kwargs):
    if instance.status != "approved":
        return

    current_chapter = instance.exercise.lesson.chapter

    user_exercises_in_chapter = models.UserExerciseStatus.objects.filter(
        user=instance.user,
        exercise__lesson__chapter=current_chapter,
    )
    if user_exercises_in_chapter.filter(status="approved").count() == user_exercises_in_chapter.count():
        next_chapter = models.Chapter.objects.filter(
            course=current_chapter.course,
            order__gt=current_chapter.order
        ).order_by('order').first()

        if next_chapter:
            models.UserChapterStatus.objects.update_or_create(
                user=instance.user,
                chapter=next_chapter,
                defaults={'is_lock': False}
            )
            logging.info(f"Chapter '{next_chapter.title}' unlocked for user '{instance.user}'")
    else:
        logging.info(f"Chapter '{current_chapter.title}' is still locked for user '{instance.user}'")

@receiver(post_save, sender=models.UserExerciseStatus)
def handle_chapter_is_lock_for (sender, instance, **kwargs):
    current_chapter = instance.exercise.lesson.chapter

    user_exercises_in_chapter = models.UserExerciseStatus.objects.filter(
        user=instance.user,
        exercise__lesson__chapter=current_chapter,
    )
    if user_exercises_in_chapter.filter(status="pending").count() == user_exercises_in_chapter.count():
        next_chapter = models.Chapter.objects.filter(
            course=current_chapter.course,
            order__gt=current_chapter.order
        ).order_by('order').first()

        if next_chapter:
            models.UserChapterStatus.objects.update_or_create(
                user=instance.user,
                chapter=next_chapter,
                defaults={'is_lock': False}
            )
            logging.info(f"Chapter '{next_chapter.title}' unlocked for user '{instance.user}'")
    else:
        logging.info(f"Chapter '{current_chapter.title}' is still locked for user '{instance.user}'")
