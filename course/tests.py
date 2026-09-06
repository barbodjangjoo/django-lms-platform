from django.contrib.auth import get_user_model
from django.db import IntegrityError
from django.test import TestCase

from .models import (
    Category,
    Chapter,
    Course,
    CourseUserStatus,
    Exercise,
    ExerciseUserAnswer,
    FinalExam,
    FinalExamQuestion,
    FinalExamUserStatus,
    Lesson,
    Quiz,
    QuizAttemptTracker,
    QuizQuestion,
    QuizUserAnswer,
    QuizUserStatus,
    UserChapterStatus,
    UserExerciseStatus,
    UserLessonStatus,
)


User = get_user_model()


class CourseModelTests(TestCase):

    def setUp(self):
        self.user = User.objects.create_user(
            username="barbod",
            password="test-password",
        )

        self.category = Category.objects.create(
            title="Backend",
            description="Backend development",
        )

        self.course = Course.objects.create(
            title="Django Backend",
            category=self.category,
            teacher="Barbod",
            order=1,
            course_time="20 hours",
            price=1000000,
        )

        self.chapter = Chapter.objects.create(
            course=self.course,
            title="Django Basics",
            order=1,
            chapter_time="5 hours",
            slug="django-basics",
        )

        self.lesson = Lesson.objects.create(
            course=self.course,
            chapter=self.chapter,
            title="Models",
            order=1,
            lesson_time="30 minutes",
            slug="models",
            description="Django models",
        )

    def test_course_slug_is_generated_when_empty(self):
        course = Course.objects.create(
            title="Advanced Django",
            category=self.category,
            teacher="Barbod",
            order=2,
            course_time="10 hours",
            price=500000,
            slug="",
        )

        self.assertEqual(course.slug, "advanced-django")

    def test_course_string_representation(self):
        self.assertEqual(str(self.course), "Django Backend")

    def test_course_status_is_created_with_locked_state(self):
        status = CourseUserStatus.objects.create(
            user=self.user,
            course=self.course,
        )

        self.assertTrue(status.is_lock)
        self.assertFalse(status.is_seen)
        self.assertFalse(status.is_complited)

    def test_course_status_is_unique_per_user(self):
        CourseUserStatus.objects.create(
            user=self.user,
            course=self.course,
        )

        with self.assertRaises(IntegrityError):
            CourseUserStatus.objects.create(
                user=self.user,
                course=self.course,
            )


class ProgressionModelTests(TestCase):

    def setUp(self):
        self.user = User.objects.create_user(
            username="barbod",
            password="test-password",
        )

        category = Category.objects.create(title="Backend")

        self.course = Course.objects.create(
            title="Django",
            category=category,
            teacher="Barbod",
            order=1,
            course_time="10 hours",
            price=100000,
        )

        self.chapter = Chapter.objects.create(
            course=self.course,
            title="Chapter 1",
            order=1,
            chapter_time="1 hour",
            slug="chapter-1",
        )

        self.lesson = Lesson.objects.create(
            course=self.course,
            chapter=self.chapter,
            title="Lesson 1",
            order=1,
            lesson_time="30 min",
            slug="lesson-1",
            description="Lesson",
        )

    def test_chapter_status_starts_locked(self):
        status = UserChapterStatus.objects.create(
            user=self.user,
            course=self.course,
            chapter=self.chapter,
        )

        self.assertTrue(status.is_lock)
        self.assertFalse(status.is_started)
        self.assertFalse(status.is_completed)

    def test_chapter_status_can_be_completed(self):
        status = UserChapterStatus.objects.create(
            user=self.user,
            course=self.course,
            chapter=self.chapter,
        )

        status.is_lock = False
        status.is_started = True
        status.is_completed = True
        status.save()

        status.refresh_from_db()

        self.assertFalse(status.is_lock)
        self.assertTrue(status.is_started)
        self.assertTrue(status.is_completed)

    def test_lesson_status_starts_locked(self):
        status = UserLessonStatus.objects.create(
            user=self.user,
            course=self.course,
            chapter=self.chapter,
            lesson=self.lesson,
        )

        self.assertTrue(status.is_lock)
        self.assertFalse(status.is_seen)

    def test_lesson_status_is_unique_per_user_and_lesson(self):
        UserLessonStatus.objects.create(
            user=self.user,
            course=self.course,
            chapter=self.chapter,
            lesson=self.lesson,
        )

        with self.assertRaises(IntegrityError):
            UserLessonStatus.objects.create(
                user=self.user,
                course=self.course,
                chapter=self.chapter,
                lesson=self.lesson,
            )


class ExerciseModelTests(TestCase):

    def setUp(self):
        self.user = User.objects.create_user(
            username="barbod",
            password="test-password",
        )

        category = Category.objects.create(title="Backend")

        course = Course.objects.create(
            title="Django",
            category=category,
            teacher="Barbod",
            order=1,
            course_time="10 hours",
            price=100000,
        )

        chapter = Chapter.objects.create(
            course=course,
            title="Chapter 1",
            order=1,
            chapter_time="1 hour",
            slug="chapter-1",
        )

        lesson = Lesson.objects.create(
            course=course,
            chapter=chapter,
            title="Lesson 1",
            order=1,
            lesson_time="30 min",
            slug="lesson-1",
            description="Lesson",
        )

        self.exercise = Exercise.objects.create(
            course=course,
            chapter=chapter,
            lesson=lesson,
            title="Exercise 1",
            question="Write a Django model.",
            order=1,
            slug="exercise-1",
        )

    def test_exercise_status_starts_not_attempted(self):
        status = UserExerciseStatus.objects.create(
            user=self.user,
            exercise=self.exercise,
        )

        self.assertEqual(status.status, "not_attempted")
        self.assertTrue(status.is_lock)

    def test_exercise_status_can_be_approved(self):
        status = UserExerciseStatus.objects.create(
            user=self.user,
            exercise=self.exercise,
        )

        status.status = "approved"
        status.is_lock = False
        status.points = 500
        status.save()

        status.refresh_from_db()

        self.assertEqual(status.status, "approved")
        self.assertEqual(status.points, 500)
        self.assertFalse(status.is_lock)

    def test_exercise_status_is_unique_per_user(self):
        UserExerciseStatus.objects.create(
            user=self.user,
            exercise=self.exercise,
        )

        with self.assertRaises(IntegrityError):
            UserExerciseStatus.objects.create(
                user=self.user,
                exercise=self.exercise,
            )


class QuizModelTests(TestCase):

    def setUp(self):
        self.user = User.objects.create_user(
            username="barbod",
            password="test-password",
        )

        category = Category.objects.create(title="Backend")

        course = Course.objects.create(
            title="Django",
            category=category,
            teacher="Barbod",
            order=1,
            course_time="10 hours",
            price=100000,
        )

        chapter = Chapter.objects.create(
            course=course,
            title="Chapter 1",
            order=1,
            chapter_time="1 hour",
            slug="chapter-1",
        )

        lesson = Lesson.objects.create(
            course=course,
            chapter=chapter,
            title="Lesson 1",
            order=1,
            lesson_time="30 min",
            slug="lesson-1",
            description="Lesson",
        )

        self.quiz = Quiz.objects.create(
            lesson=lesson,
            title="Django Quiz",
            order=1,
            slug="django-quiz",
        )

        self.question = QuizQuestion.objects.create(
            quiz=self.quiz,
            order=1,
            text="Which framework is written in Python?",
            option_1="Django",
            option_2="Laravel",
            option_3="Rails",
            option_4="Spring",
            correct_answer=1,
        )

    def test_quiz_status_starts_locked(self):
        status = QuizUserStatus.objects.create(
            user=self.user,
            quiz=self.quiz,
        )

        self.assertTrue(status.is_lock)
        self.assertFalse(status.is_pass)
        self.assertFalse(status.is_seen)

    def test_quiz_answer_can_be_marked_correct(self):
        answer = QuizUserAnswer.objects.create(
            user=self.user,
            quiz=self.quiz,
            question=self.question,
            selected_option=1,
            is_correct=True,
        )

        self.assertTrue(answer.is_correct)
        self.assertEqual(answer.selected_option, 1)

    def test_quiz_attempt_tracker_starts_at_zero(self):
        tracker = QuizAttemptTracker.objects.create(
            user=self.user,
            quiz=self.quiz,
        )

        self.assertEqual(tracker.attempt_count, 0)

    def test_quiz_attempt_tracker_can_increment(self):
        tracker = QuizAttemptTracker.objects.create(
            user=self.user,
            quiz=self.quiz,
        )

        tracker.increment_attempt()
        tracker.refresh_from_db()

        self.assertEqual(tracker.attempt_count, 1)

    def test_quiz_attempt_tracker_is_unique_per_user(self):
        QuizAttemptTracker.objects.create(
            user=self.user,
            quiz=self.quiz,
        )

        with self.assertRaises(IntegrityError):
            QuizAttemptTracker.objects.create(
                user=self.user,
                quiz=self.quiz,
            )


class FinalExamModelTests(TestCase):

    def setUp(self):
        self.user = User.objects.create_user(
            username="barbod",
            password="test-password",
        )

        category = Category.objects.create(title="Backend")

        course = Course.objects.create(
            title="Django",
            category=category,
            teacher="Barbod",
            order=1,
            course_time="10 hours",
            price=100000,
        )

        chapter = Chapter.objects.create(
            course=course,
            title="Chapter 1",
            order=1,
            chapter_time="1 hour",
            slug="chapter-1",
        )

        self.exam = FinalExam.objects.create(
            chapter=chapter,
            title="Final Exam",
            order=1,
            slug="final-exam",
        )

    def test_final_exam_status_can_store_result(self):
        status = FinalExamUserStatus.objects.create(
            user=self.user,
            final_exam=self.exam,
            is_pass=True,
            is_seen=True,
            points=500,
        )

        self.assertTrue(status.is_pass)
        self.assertTrue(status.is_seen)
        self.assertEqual(status.points, 500)

    def test_final_exam_question_supports_essay_question(self):
        question = FinalExamQuestion.objects.create(
            final_exam=self.exam,
            order=1,
            question_text="Explain Django ORM.",
            is_essay=True,
        )

        self.assertTrue(question.is_essay)