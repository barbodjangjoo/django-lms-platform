from django.core.management.base import BaseCommand
from course.models import UserLessonStatus, UserExerciseStatus, QuizUserAnswer, UserChapterStatus

class Command(BaseCommand):
    help = 'Unlocks all locked items for all users'

    def handle(self, *args, **kwargs):
        lesson_updates = UserLessonStatus.objects.all().update(is_lock=False)
        self.stdout.write(f"Unlocked {lesson_updates} lessons")

        exercise_updates = UserExerciseStatus.objects.filter(is_lock=True).update(is_lock=False)
        self.stdout.write(f"Unlocked {exercise_updates} exercises")

        quiz_updates = QuizUserAnswer.objects.filter(is_lock=True).update(is_lock=False)
        self.stdout.write(f"Unlocked {quiz_updates} quiz answers")

        chapter_updates = UserChapterStatus.objects.filter(is_lock=True).update(is_lock=False)
        self.stdout.write(f"Unlocked {chapter_updates} chapters")

        self.stdout.write(self.style.SUCCESS('Successfully unlocked all items'))
