from django.db import transaction
from .models import UserPoint
from course.models import UserExerciseStatus, QuizUserAnswer, FinalExamUserAnswer
from django.contrib.auth import get_user_model
from notifications.models import Notification

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


# def award_profile_points(user, field_name):
#     """
#     Award points for completing profile fields
#     """
#     if field_name not in PROFILE_FIELD_POINTS:
#         return {'success': False, 'message': 'Invalid field'}
        
#     points = PROFILE_FIELD_POINTS[field_name]
    
#     return award_points(
#         user=user,
#         points=points,
#         activity_type='PROFILE',
#         activity_id=f'profile_{field_name}',
#         details=f'Completed profile field: {field_name}'
#     )

# def award_points(user, points, activity_type, activity_id, details=None):
#     """
#     Generic function to award points for any activity
#     """
#     with transaction.atomic():
#         try:
#             point_record, created = UserPoint.objects.get_or_create(
#                 user=user,
#                 activity_type=activity_type,
#                 activity_id=activity_id,
#                 defaults={
#                     'points': points,
#                     'details': details
#                 }
#             )
#             if not created:
#                 return {'success': False, 'message': 'Points already awarded'}
#             return {'success': True, 'points': point_record}
#         except Exception as e:
#             return {'success': False, 'message': str(e)}

# def reward_points_for_exercise(user, exercise_status):
#     """
#     Award points for exercise completion based on admin-assigned points
#     """
#     if not isinstance(exercise_status, UserExerciseStatus):
#         return {'success': False, 'message': 'Invalid exercise status'}
    
#     if exercise_status.status != 'approved':
#         return {'success': False, 'message': 'Exercise not approved'}
    
#     if not exercise_status.points:
#         return {'success': False, 'message': 'No points assigned'}
        
#     return award_points(
#         user=user,
#         points=exercise_status.points,
#         activity_type='EXERCISE',
#         activity_id=f'exercise_{exercise_status.exercise.id}',
#         details=f'Exercise: {exercise_status.exercise.title}'
#     )

# def reward_points_for_quiz(user, quiz_answers, quiz):
#     """Award points for quiz completion with perfect score"""
#     if not quiz_answers.exists():
#         return {'success': False, 'message': 'No answers found'}
    
#     correct_count = quiz_answers.filter(is_correct=True).count()
#     total_questions = quiz.questions.count()
    
#     # Check if all answers are correct (perfect score)
#     if correct_count == total_questions:
#         points = 500  # Bonus points for perfect score
        
#         return award_points(
#             user=user,
#             points=points,
#             activity_type='QUIZ',
#             activity_id=f'quiz_{quiz.id}_perfect',
#             details=f'Perfect Score in Quiz: {quiz.title}'
#         )
    
#     # Regular points for completed quiz
#     points = correct_count * 50  # Regular points per correct answer
    
#     return award_points(
#         user=user,
#         points=points,
#         activity_type='QUIZ',
#         activity_id=f'quiz_{quiz.id}',
#         details=f'Completed Quiz: {quiz.title}'
#     )

# def reward_points_for_final_exam(user, exam_answers):
#     """Award points for final exam completion"""
#     if not exam_answers:
#         return {'success': False, 'message': 'No answers found'}
        
#     # Ensure exam_answers is a queryset or list
#     if not isinstance(exam_answers, (list, tuple)):
#         exam_answers = [exam_answers]
        
#     total_points = sum(answer.points or 0 for answer in exam_answers)
#     final_exam = exam_answers[0].final_exam if exam_answers else None
    
#     if not final_exam:
#         return {'success': False, 'message': 'Final exam not found'}
    
#     return award_points(
#         user=user,
#         points=total_points,
#         activity_type='FINAL_EXAM',
#         activity_id=f'exam_{final_exam.id}',
#         details=f'Final Exam: {final_exam.title}'
#     )
