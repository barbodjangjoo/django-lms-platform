from django.contrib.auth.decorators import login_required
from django.db.models import Prefetch
from django.shortcuts import get_object_or_404
from rest_framework.response import Response
from rest_framework.decorators import api_view, permission_classes, parser_classes
from rest_framework import status
from rest_framework.permissions import IsAuthenticated
from rest_framework.parsers import MultiPartParser, FormParser
import logging


# from .task import generate_watermarked_video_task

from . import models
from . import serializers
from points import models as points_model
from .permissions import HasAccess
from audit.models import Audit


@api_view()
def category_list_view(request):
    query_set = models.Category.objects.all()
    serializer = serializers.CategorySerializer(query_set, many=True)
    return Response(serializer.data)

@api_view(['GET'])
def course_list_view(request):
    query_set = models.Course.objects.all()
    serializer = serializers.CourseSerializer(query_set, many=True, context={'request':request})
    if request.user.is_authenticated:
        Audit.objects.create(
            user=request.user,
            log_type='COURSES',
            call_function = 'course_list_view',
            http_response_status_code = 200,
            result = serializer.data
        )
        return Response (serializer.data)
    return Response (serializer.data)

@permission_classes([])
@api_view(['GET'])
def course_detail_view(request, pk):
    course = get_object_or_404(
        models.Course.objects.prefetch_related(
            Prefetch(
                'user_statuses',
                queryset=models.CourseUserStatus.objects.filter(user_id=request.user.id)
            )
        ),
        pk=pk
    )
    if request.method == 'GET':
        serializer = serializers.CourseDetailSerializer(course, context={'request': request})
        if request.user.is_authenticated:
            Audit.objects.create(
                user=request.user,
                log_type='COURSES',
                call_function = 'course_detail_view',
                http_response_status_code = 200,
                result = f'user send get method request and result is : {serializer.data}'
            )
        return Response(serializer.data)
    elif request.method == 'PATCH':
        if request.user.is_authenticated:
            old_status = models.CourseUserStatus.objects.get(course=course, user=request.user)
            user_stat = serializers.CourseUserStatusSerializer(old_status ,data=request.data, partial=True)
            user_stat.is_valid(raise_exception=True)
            user_stat.save()
            Audit.objects.create(
                user=request.user,
                log_type='COURSES',
                call_function = 'course_detail_view',
                http_response_status_code = 200,
                result = f'user send PATCH method request and result is : {serializer.data}'
                )
            return Response(user_stat.data, status.HTTP_200_OK)
        return Response("برای دسترسی به این قسمت باید وارد شوہید", status=status.HTTP_401_UNAUTHORIZED)
    
    
@permission_classes([IsAuthenticated, HasAccess])
@api_view(['PATCH'])
def course_update_is_seen_view(request, pk):
    course = get_object_or_404(
        models.Course.objects.prefetch_related(
            Prefetch(
                'user_statuses',
                queryset=models.CourseUserStatus.objects.filter(user_id=request.user.id)
            )
        ),
        pk=pk
    )
    if request.method == 'PATCH':
        if request.user.is_authenticated:
            old_status = models.CourseUserStatus.objects.get(course=course, user=request.user)
            user_stat = serializers.CourseUserStatusSerializer(old_status ,data=request.data, partial=True)
            user_stat.is_valid(raise_exception=True)
            user_stat.save()
            Audit.objects.create(
            user=request.user,
            log_type='COURSES',
            call_function = 'course_update_is_seen_view',
            http_response_status_code = 200,
            result = f'user send PATCH method request and result is : {user_stat.data}'
        )
            return Response(user_stat.data, status.HTTP_200_OK)
        Audit.objects.create(
            user=request.user,
            log_type='COURSES',
            call_function = 'course_update_is_seen_view',
            http_response_status_code = 401,
            result = f'user was not logged in'
        )
        return Response("برای دسترسی به این قسمت باید وارد شوہید", status=status.HTTP_401_UNAUTHORIZED)

@permission_classes([IsAuthenticated, HasAccess])
@api_view(['GET'])
def chapter_list_View(request, pk):
    chapter_list = models.Chapter.objects.filter(course= pk).all()
    for chapter in chapter_list:
        if chapter.order == 1:
            user_chapter_status = models.UserChapterStatus.objects.filter(chapter=chapter, user=request.user).get()
            user_chapter_status.is_lock = False
            user_chapter_status.save()

            Audit.objects.create(
            user=request.user,
            log_type='COURSES',
            call_function = 'chapter_list_View',
            http_response_status_code = 200,
            result = f'chapter is_lock set as unlock {chapter} for {user_chapter_status}'
        )
    serializer = serializers.ChapterSerializer(chapter_list, many=True, context={'request':request})
    Audit.objects.create(
            user=request.user,
            log_type='COURSES',
            call_function = 'chapter_list_View',
            http_response_status_code = 200,
            result = f'user saw chapters : {serializer.data}'
        )
    return Response(serializer.data)

@permission_classes([IsAuthenticated, HasAccess])
@api_view(['GET'])
def chapter_detail_view(request, pk):
    chapter = get_object_or_404(models.Chapter, pk=pk)
    lessons = models.Lesson.objects.filter(chapter=chapter).order_by('order')
    if chapter.order == 1:
        user_chapter_status =models.UserChapterStatus.objects.get(user=request.user, chapter=chapter)
        user_chapter_status.is_lock = False
        user_chapter_status.save()
        Audit.objects.create(
            user=request.user,
            log_type='COURSES',
            call_function = 'chapter_detail_view',
            http_response_status_code = 200,
            result = f'chapter is_lock set as unlock {chapter} for {user_chapter_status}'
        )
    for lesson in lessons:
        if lesson.order== 1:
            user_lesson_status = models.UserLessonStatus.objects.get(user=request.user, lesson=lesson)
            user_lesson_status.is_lock = False
            user_lesson_status.save()
            Audit.objects.create(
            user=request.user,
            log_type='COURSES',
            call_function = 'chapter_detail_view',
            http_response_status_code = 200,
            result = f'lesson one:{lesson.title} set unlock for {request.user}'
        )


    lesson_serializer = serializers.LessonWithDetailsSerializer(lessons, many=True, context={'request': request})
    chapter_serializer = serializers.ChapterSerializer(chapter, context={'request': request})
    Audit.objects.create(
            user=request.user,
            log_type='COURSES',
            call_function = 'chapter_detail_view',
            http_response_status_code = 200,
            result = f'user saw chapter: {chapter_serializer.data} \n and saw these lesson:{lesson_serializer.data}'
        )
    return Response({
        'chapter': chapter_serializer.data,
        'lessons': lesson_serializer.data,
    })
@permission_classes([IsAuthenticated, HasAccess])
@api_view(['PATCH'])
def chapter_update_is_seen_view(request, pk):
    chapter = get_object_or_404(models.Chapter, pk=pk)
    if request.method == 'PATCH':
        if request.user.is_authenticated:
            old_status = models.UserChapterStatus.objects.get(chapter=chapter, user=request.user)
            user_stat = serializers.UserChapterStatusSerializers(old_status ,data=request.data, partial=True)
            user_stat.is_valid(raise_exception=True)
            user_stat.save()
            Audit.objects.create(
            user=request.user,
            log_type='COURSES',
            call_function = 'chapter_update_is_seen_view',
            http_response_status_code = 200,
            result = f'chapter: {chapter.title} is_seen updated'
        )
            return Response(user_stat.data, status.HTTP_200_OK)
        
        Audit.objects.create(
            user=request.user,
            log_type='COURSES',
            call_function = 'chapter_update_is_seen_view',
            http_response_status_code = 401,
            result = "برای دسترسی به این قسمت باید وارد شوہید"
        )

        return Response("برای دسترسی به این قسمت باید وارد شوہید", status=status.HTTP_401_UNAUTHORIZED)
@permission_classes([IsAuthenticated, HasAccess])
@api_view(['GET'])
def chapter_exercises_view(request, pk):
    chapter = get_object_or_404(models.Chapter, pk=pk)
    exercises = models.Exercise.objects.filter(lesson__chapter= chapter).all()
    serializer = serializers.ExerciseSerializer(exercises, many=True, context={'request':request})

    Audit.objects.create(
            user=request.user,
            log_type='COURSES',
            call_function = 'chapter_exercises_view',
            http_response_status_code = 200,
            result = f"user: {request.user} requested to see exercise for chapter"
        )    

    return Response(serializer.data)

@permission_classes([IsAuthenticated, HasAccess])   
@api_view(['PATCH'])
def chapter_unlock_view(request, pk):
    chapter = get_object_or_404(models.Chapter, pk=pk)
    exercises = models.Exercise.objects.filter(lesson__chapter=chapter)
    all_approved = all(
            models.UserExerciseStatus.objects.filter(user=request.user, exercise=ex, status='approved').exists()
            for ex in exercises
        )

# all approve = true
    if chapter.course.is_approve_process == True:
        if all_approved:
            next_chapter = models.Chapter.objects.filter(course=chapter.course, order__gt=chapter.order).order_by('order').first()
            if next_chapter:
                user_chapter_status, _ = models.UserChapterStatus.objects.get_or_create(user=request.user, chapter=next_chapter)
                user_chapter_status.is_lock = False
                user_chapter_status.save()

                Audit.objects.create(
                user=request.user,
                log_type='COURSES',
                call_function = 'chapter_unlock_view',
                http_response_status_code = 200,
                result = f"chapter: {next_chapter} set unlock for user: {user_chapter_status.user}"
            )    
                
                return Response({'detail': f'Chapter "{next_chapter.title}" unlocked.'}, status=200)
            Audit.objects.create(
                user=request.user,
                log_type='COURSES',
                call_function = 'chapter_unlock_view',
                http_response_status_code = 404,
                result = f"{user_chapter_status.user} reached the end of course"
            )    
            return Response({'detail': 'No next chapter found.'}, status=404)
        Audit.objects.create(
                user=request.user,
                log_type='COURSES',
                call_function = 'chapter_unlock_view',
                http_response_status_code = 403,
                result = "Not all exercises are approved"
            )
        return Response({'detail': 'Not all exercises are approved.'}, status=403)
    
    else:
        next_chapter = models.Chapter.objects.filter(course=chapter.course, order__gt=chapter.order).order_by('order').first()
        user_chapter_status, _ = models.UserChapterStatus.objects.get_or_create(user=request.user, chapter=next_chapter)
        user_chapter_status.is_lock = False
        user_chapter_status.save()
        return Response({'detail': f'Chapter "{next_chapter.title}" unlocked.'}, status=200)


@permission_classes([IsAuthenticated, HasAccess])
@api_view(['GET'])
def lesson_list_view(request, pk):
    chapter= get_object_or_404(models.Chapter, pk=pk)
    lessons = models.Lesson.objects.filter(chapter=chapter).all()
    serializer = serializers.LessonListSerializer(lessons, many=True, context={'request': request})

    Audit.objects.create(
            user=request.user,
            log_type='COURSES',
            call_function = 'lesson_list_view',
            http_response_status_code = 200,
            result = f"{request.user} saw lesson list \n {serializer.data}"
        )  
    
    return Response(serializer.data)

@permission_classes([IsAuthenticated, HasAccess])
@api_view(['GET'])
def lesson_detail_view(request, pk):
    if request.user.is_authenticated: 
        user= request.user
        lesson = get_object_or_404(models.Lesson, pk=pk)
        lesson_serializer = serializers.LessonSerializer(lesson, context={'request': request})
        user_status = models.UserLessonStatus.objects.filter(user=user, lesson=lesson).first()
        user_status_serializer= serializers.UserLessonStatusSerializer(user_status)


        Audit.objects.create(
            user=request.user,
            log_type='COURSES',
            call_function = 'lesson_detail_view',
            http_response_status_code = 200,
            result = f"{user} saw {lesson.title}"
        ) 

        return Response({
            "lesson": lesson_serializer.data,
            "user_status": user_status_serializer.data
        })
    return Response("برای دیدن این صفحه باید لاگین کنید")


@permission_classes([IsAuthenticated, HasAccess])
@api_view(['GET'])
def lesson_comment_view(request, pk):
    lesson = get_object_or_404(models.Lesson, pk=pk)
    comments = models.LessonComment.objects.filter(lesson=lesson).all()
    serializer = serializers.LessonCommentSerializer(comments, many=True, context={'request':request})

    Audit.objects.create(
            user=request.user,
            log_type='COURSES',
            call_function = 'lesson_comment_view',
            http_response_status_code = 200,
            result = f"user :{request.user} viewed comments"
        ) 
    return Response(serializer.data)


@permission_classes([IsAuthenticated, HasAccess])
@api_view(['POST'])
def lesson_comment_create_view(request, pk):
    if request.method == 'POST':
        lesson = get_object_or_404(models.Lesson, pk=pk)
        serializer = serializers.LessonCommentSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save(user=request.user, lesson=lesson)
        Audit.objects.create(
            user=request.user,
            log_type='COURSES',
            call_function = 'lesson_comment_create_view',
            http_response_status_code = 201,
            result = f"{request.user} commented on {lesson} \n heres comment: {serializer.data}"
        ) 
        return Response(serializer.data, status=status.HTTP_201_CREATED)
    

@permission_classes([IsAuthenticated, HasAccess])
@api_view(['PATCH'])
def lesson_comment_like_view(request, pk):
    comment = get_object_or_404(models.LessonComment, pk=pk)
    user = request.user
    if comment.like.filter(id=user.id).exists():
        comment.like.remove(user)
        liked = False
    else:
        comment.like.add(user)
        liked = True
    return Response({
        "liked": liked,
        "like_count": comment.like.count()
    }, status=status.HTTP_200_OK)

@permission_classes([IsAuthenticated, HasAccess])
@api_view(['PATCH'])
def lesson_update_is_seen_view(request, pk):
    lesson = get_object_or_404(models.Lesson, pk=pk)
    if request.method == 'PATCH':
        if request.user.is_authenticated:
            old_status = models.UserLessonStatus.objects.get(lesson=lesson, user=request.user)
            user_stat = serializers.UserLessonStatusSerializer(old_status ,data=request.data, partial=True)
            user_stat.is_valid(raise_exception=True)
            user_stat.save()
            Audit.objects.create(
            user=request.user,
            log_type='COURSES',
            call_function = 'lesson_update_is_seen_view',
            http_response_status_code = 200,
            result = f'lessson: {lesson.title} is_seen updated'
        )
            return Response(user_stat.data, status.HTTP_200_OK)
        return Response("برای دسترسی به این قسمت باید وارد شوہید", status=status.HTTP_401_UNAUTHORIZED)
    
@permission_classes([IsAuthenticated, HasAccess])
@api_view(['PATCH'])
def lesson_update_unlock_view(request, pk):
    lesson = get_object_or_404(models.Lesson, pk=pk)
    if request.method == 'PATCH':
        if request.user.is_authenticated:
            old_status = models.UserLessonStatus.objects.get(lesson=lesson, user=request.user)
            user_stat = serializers.UserLessonStatusSerializer(old_status ,data=request.data, partial=True)
            user_stat.is_valid(raise_exception=True)
            user_stat.save()
            Audit.objects.create(
            user=request.user,
            log_type='COURSES',
            call_function = 'lesson_update_unlock_view',
            http_response_status_code = 200,
            result = f'lessson: {lesson.title} is_lock updated for user: {request.user}'
        )
            return Response(user_stat.data, status.HTTP_200_OK)
        
        Audit.objects.create(
            user=request.user,
            log_type='COURSES',
            call_function = 'lesson_update_unlock_view',
            http_response_status_code = 401,
            result = "برای دسترسی به این قسمت باید وارد شوہید"
        )
        return Response("برای دسترسی به این قسمت باید وارد شوہید", status=status.HTTP_401_UNAUTHORIZED)
@permission_classes([IsAuthenticated, HasAccess])
@api_view(['GET'])
def quiz_list_view(request, pk):
    quizzes = models.Quiz.objects.filter(lesson=pk).all()
    serializer = serializers.QuizListSerializer(quizzes, many=True, context={'request':request})
    return Response(serializer.data)


@permission_classes([IsAuthenticated, HasAccess])
@api_view(['GET'])
def quiz_detail_view(request, pk):
    
    quiz= get_object_or_404(
        models.Quiz.objects.prefetch_related(
            Prefetch('questions', queryset=models.QuizQuestion.objects.order_by('order'))
            )
    , pk=pk)

    quiz_serializer= serializers.QuizSerializer(quiz, context={"request":request})
    return Response(quiz_serializer.data)

@permission_classes([IsAuthenticated, HasAccess])
@api_view(['POST'])
def quiz_answer_submit_view(request, pk):
    quiz = get_object_or_404(models.Quiz, pk=pk)
    user = request.user
    answer_data = request.data.get('answers', [])
    
    if not isinstance(answer_data, list):
        Audit.objects.create(
            user=request.user,
            log_type='COURSES',
            call_function = 'quiz_answer_submit_view',
            http_response_status_code = 400,
            result = f"user: {request.user} answer were not supported format"
        )    
        return Response('فرمت ارسالی جواب‌ها درست نمی‌باشد.', status=status.HTTP_400_BAD_REQUEST)
    
    correct_count = 0
    total_questions = quiz.questions.count() # type: ignore
    
    for item in answer_data:
        question_id = item.get('question_id')
        selected_option = item.get('selected_option')

        if question_id is None or selected_option is None:
            continue

        try:
            question = models.QuizQuestion.objects.get(id=question_id, quiz=quiz)
        except models.QuizQuestion.DoesNotExist:
            continue

        is_correct = selected_option == question.correct_answer
        if is_correct:
            correct_count += 1

        models.QuizUserAnswer.objects.update_or_create(
            user=user,
            quiz=quiz,
            question=question,
            defaults={
                'selected_option': selected_option,
                'is_correct': is_correct
            }
        )
    points_awarded = correct_count * 10

    user_point, created = points_model.UserPoint.objects.get_or_create(
        user=user,
        activity_type='QUIZ',
        activity_id=str(quiz.id),
        details = f'امتیاز برای کوییز {quiz.title} ثبت شد',
        defaults={'points': points_awarded}
    )

    if not created and points_awarded > user_point.points:
        user_point.points = points_awarded
        user_point.save()

    score_percentage = (correct_count / total_questions) * 100 if total_questions else 0
    is_pass = score_percentage >= 80 

    models.QuizUserStatus.objects.update_or_create(
        user=user,
        quiz=quiz,
        defaults={
            'is_seen': True,
            'is_pass': is_pass,
            'is_lock': False
        }
    )

    quiz_attempt_tracker, _ = models.QuizAttemptTracker.objects.update_or_create(
        user=user, quiz=quiz
    )
    quiz_attempt_tracker.attempt_count += 1
    quiz_attempt_tracker.save()


    lesson = quiz.lesson
    total_quizzes = models.Quiz.objects.filter(lesson=lesson).count()
    passed_quizzes = models.QuizUserStatus.objects.filter(
        user=user,
        quiz__lesson=lesson,
        is_pass=True
    ).count()
    remaining_quizzes = total_quizzes - passed_quizzes
    Audit.objects.create(
            user=request.user,
            log_type='COURSES',
            call_function = 'quiz_answer_submit_view',
            http_response_status_code = 200,
            result = f"user: {request.user} \n quiz: {quiz} \n correct answers: {correct_count} \n score percentage : {score_percentage} \n is_pass: {is_pass}"
        )    

    return Response({
        'detail': 'Answers submitted successfully.',
        'correct_answers': correct_count,
        'total_questions': total_questions,
        'score_percentage': score_percentage,
        'is_pass': is_pass,
        'total_quizzes': total_quizzes,
        'passed_quizzes': passed_quizzes,
        'remaining_quizzes': remaining_quizzes
    }, status=status.HTTP_200_OK)

@permission_classes([IsAuthenticated, HasAccess])
@api_view(['GET'])
def quiz_resault_view(request, pk):

    quiz = get_object_or_404(models.Quiz, pk=pk)
    lesson_id = quiz.lesson.id
    user_status = models.QuizUserStatus.objects.filter(quiz=quiz, user=request.user).first()
    quiz_user_attempt = models.QuizAttemptTracker.objects.filter(quiz=quiz, user=request.user).first()
    if not quiz_user_attempt:
        return Response({"detail": "هیچ تلاش ثبت نشده است."}, status=status.HTTP_404_NOT_FOUND)
    quiz_user_attempt_serializer = serializers.QuizAttemptTrackerSerializer(quiz_user_attempt)
    if not user_status:
        return Response('هیچ استاتوسی برای این کوییزی با آیدی پیدا نشد', status=status.HTTP_404_NOT_FOUND)
    elif user_status.is_lock:
        return Response("هنوز این مرحله برات قفله!", status=status.HTTP_404_NOT_FOUND)

    has_any_answers = models.QuizUserAnswer.objects.filter(quiz=quiz, user=request.user).all()
    for has_any_answer in has_any_answers:
        if has_any_answer.selected_option == None:
            return Response("هیچ جوابی کاربر هنوز نداده", status=status.HTTP_404_NOT_FOUND)
        continue

    correct_answers = []
    incorrect_answers = []
    unanswered_questions = []
    questions = models.QuizQuestion.objects.filter(quiz=quiz).all()
    total_question = questions.count()
    for question in questions:
        user_answer = models.QuizUserAnswer.objects.filter(question=question, user=request.user).first()
        if user_answer:
            if user_answer.is_correct:
                correct_answers.append({
                    "question_id": question.id,
                    "question_text": question.text,
                    "selected_option": user_answer.selected_option,
                    "question_order": question.order,
                })
            else:
                incorrect_answers.append({
                    "question_id": question.id,
                    "question_text": question.text,
                    "selected_option": user_answer.selected_option,
                    "correct_option": question.correct_answer,
                    "question_order": question.order,
                })
        else:
            unanswered_questions.append({
                "question_id": question.id,
                "question_text": question.text,
                "quiz_user_answer": None,
            })
    user_status_data = serializers.QuizUserStatusSerializer(user_status).data
    Audit.objects.create(
            user=request.user,
            log_type='COURSES',
            call_function = 'quiz_answer_submit_view',
            http_response_status_code = 200,
            result = f"user: {request.user} \n quiz_attempt: {quiz_user_attempt_serializer.data} \n correct_answer: {correct_answers} \n user_status: {user_status_data}"
        )    
    return Response({
        'lesson_id': lesson_id,
        'quiz_attempt': quiz_user_attempt_serializer.data,
        'total_question': total_question,
        'correct_answers': correct_answers,
        'incorrect_answers': incorrect_answers,
        'unanswered_questions': unanswered_questions,
        'user_status': user_status_data,
    })

@permission_classes([IsAuthenticated, HasAccess])    
@api_view(['PATCH'])
def quiz_is_seen_update_view(request, pk):
    quiz= get_object_or_404(models.Quiz, pk=pk)
    user = request.user
    if user.is_authenticated:
        old_status = models.QuizUserStatus.objects.get(quiz=quiz, user=request.user)
        user_status = serializers.QuizUserStatusSerializer(old_status, data=request.data, partial=True)
        user_status.is_valid(raise_exception=True)
        user_status.save()

        Audit.objects.create(
            user=request.user,
            log_type='COURSES',
            call_function = 'quiz_is_seen_update_view',
            http_response_status_code = 200,
            result = f'user: {user} is_seen updated for {quiz.title}'
        )

        return Response(user_status.data, status=status.HTTP_200_OK)
    return Response("برای دسترسی به این قسمت باید وارد شوہید", status=status.HTTP_401_UNAUTHORIZED)
@permission_classes([IsAuthenticated, HasAccess])    
@api_view(['PATCH'])
def quiz_unlock_update_view(request, pk):
    quiz= get_object_or_404(models.Quiz, pk=pk)
    user = request.user
    if user.is_authenticated:
        old_status = models.QuizUserStatus.objects.get(quiz=quiz, user=request.user)
        user_status = serializers.QuizUserStatusSerializer(old_status, data=request.data, partial=True)
        user_status.is_valid(raise_exception=True)
        user_status.save()
        Audit.objects.create(
            user=request.user,
            log_type='COURSES',
            call_function = 'quiz_unlock_update_view',
            http_response_status_code = 200,
            result = f'user: {user} is_lock updated for {quiz.title}'
        )
        return Response(user_status.data, status=status.HTTP_200_OK)
    return Response("برای دسترسی به این قسمت باید وارد شوہید", status=status.HTTP_401_UNAUTHORIZED)
@permission_classes([IsAuthenticated, HasAccess])
@api_view(['GET'])
def exercise_list_view(request, pk):
    lesson = get_object_or_404(models.Lesson, pk=pk)
    exercises = models.Exercise.objects.filter(lesson=lesson).all()
    serializer = serializers.ExerciseSerializer(exercises, many=True, context={'request':request})
    return Response(serializer.data)

@permission_classes([IsAuthenticated, HasAccess])
@api_view(['GET', 'POST'])
def exercise_detail_view(request, pk):
    if request.user.is_authenticated:
        try:
            user = request.user

            exercise = get_object_or_404(models.Exercise, pk=pk)
            lesson = exercise.lesson
            chapter = lesson.chapter
            exercise_serializer = serializers.ExerciseSerializer(exercise, context={'request': request})

            exercise_status = models.UserExerciseStatus.objects.filter(user=user, exercise=exercise).get()
            if exercise_status is None:
                return Response(
                    {"detail": "Exercise status not found."},
                    status=status.HTTP_404_NOT_FOUND
                )
            exercise_status_serializer = serializers.ExerciseUserStatusSerializer(exercise_status)
            user_exercise_answer = models.ExerciseUserAnswer.objects.filter(user=user, exercise=exercise).all().order_by('datetime_created')
            if user_exercise_answer is None:
                return Response(
                    {"detail": "User exercise answer not found."},
                    status=status.HTTP_404_NOT_FOUND
                )
            user_exercise_answer_serializer = serializers.ExerciseUserAnswerSerializer(user_exercise_answer, many=True)

            admin_feedback = models.AdminExerciseFeedback.objects.filter(exercise=exercise, user=user).all().order_by('datetime_created')

            if admin_feedback is None:
                return Response(
                    {"detail": "Admin feedback not found."},
                    status=status.HTTP_404_NOT_FOUND
                )

            admin_feedback_serializer = serializers.AdminFeedBackSerializer(admin_feedback, many=True)


            if request.method == 'GET':
                Audit.objects.create(
                    user=request.user,
                    log_type='COURSES',
                    call_function = 'exercise_detail_view',
                    http_response_status_code = 200,
                    result = f'user saw exercise detail on exercise :{exercise_serializer.data}'
                )

                return Response({
                    "exercise_status": exercise_status_serializer.data,
                    "exercise":exercise_serializer.data,
                    "user_answer":user_exercise_answer_serializer.data,
                    "admin_feedback": admin_feedback_serializer.data,
                    "chapter_slug": chapter.slug,
                    "lesson_slug": lesson.slug,
                    "exercise_slug": exercise.slug,
                    }, status=status.HTTP_200_OK)


            elif request.method == 'POST':
                user_exercise_answer = serializers.ExerciseUserAnswerSerializer(data=request.data)
                if user_exercise_answer.is_valid(raise_exception=True):
                    user_exercise_answer.save(user=user, exercise=exercise, useranswer_status=exercise_status)
                    exercise_status.status = 'pending'
                    exercise_status.useranswers.add(user_exercise_answer.instance)
                    exercise_status.save()
                    total = models.Exercise.objects.filter(lesson=lesson).count()
                    submitted = models.UserExerciseStatus.objects.filter(
                    user=user,
                    exercise__lesson=lesson,
                    status__in=["pending", "approved", "rejected"]
                    ).count()
                    remaining = total - submitted

                    Audit.objects.create(
                    user=request.user,
                    log_type='COURSES',
                    call_function = 'exercise_detail_view',
                    http_response_status_code = 200,
                    result = f'user post exercise on :{exercise.title} \n user answer: {user_exercise_answer.data}'
                )

                    return Response({
                        "user_exercise_answer":user_exercise_answer.data,
                        "remaining_exercises": remaining,
                        "total_exercises":total,
                        "submitted_exercises": submitted,
                        }
                    , status=status.HTTP_201_CREATED)
            else:
                return Response(user_exercise_answer.errors, status=status.HTTP_400_BAD_REQUEST)  # type: ignore

        except Exception as e:
            return Response(
                {"detail": "An error occurred while processing your request."},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )
    else:
        return Response(
            {"detail": "You must be logged in to view this exercise."},
            status=status.HTTP_403_FORBIDDEN
        )
@permission_classes([IsAuthenticated, HasAccess])
@parser_classes([MultiPartParser, FormParser])
@api_view(['POST'])
def exercise_submit_view(request, pk):
    exercise = get_object_or_404(models.Exercise, pk=pk)
    lesson = exercise.lesson
    user= request.user
    user_status = models.UserExerciseStatus.objects.filter(exercise=exercise, user=request.user).get()
    user_answer = serializers.ExerciseUserAnswerSerializer(data=request.data)
    user_answer.is_valid(raise_exception=True)
    user_answer.save(exercise=exercise, user=request.user, useranswer_status=user_status)

    user_status.status = 'pending'
    user_status.useranswers.add(user_answer.instance)
    user_status.save()

    total = models.Exercise.objects.filter(lesson=lesson).count()
    submitted = models.UserExerciseStatus.objects.filter(
    user=user,
    exercise__lesson=lesson,
    status__in=["pending", "approved", "rejected"]
            ).count()
    remaining = total - submitted
    Audit.objects.create(
    user=request.user,
    log_type='COURSES',
    call_function = 'exercise_submit_view',
    http_response_status_code = 200,
    result = f'{user} submited answer for {exercise.title}'
        )
    return Response({
        'total':total,
        'submited':submitted,
        'remaining':remaining,
        'user_answer':user_answer.data
        }, status=status.HTTP_201_CREATED)


@permission_classes([IsAuthenticated, HasAccess])
@api_view(['PATCH'])
def exercise_is_seen_update_view(request, pk):
    exercise = get_object_or_404(models.Exercise, pk=pk)
    user = request.user
    old_status = models.UserExerciseStatus.objects.get(exercise=exercise, user=request.user)
    user_status = serializers.ExerciseUserStatusSerializer(old_status, data=request.data, partial=True)
    user_status.is_valid(raise_exception=True)
    user_status.save()

    Audit.objects.create(
    user=request.user,
    log_type='COURSES',
    call_function = 'exercise_is_seen_update_view',
    http_response_status_code = 200,
    result = f'{user} is seen updated for {exercise.title}'
    )

    return Response(user_status.data, status=status.HTTP_200_OK)

@permission_classes([IsAuthenticated, HasAccess])
@api_view(['PATCH'])
def exercise_unlock_update_view(request, pk):
    exercise = get_object_or_404(models.Exercise, pk=pk)
    user = request.user
    if user.is_authenticated:
        old_status = models.UserExerciseStatus.objects.get(exercise=exercise, user=request.user)
        user_status = serializers.ExerciseUserStatusSerializer(old_status, data=request.data, partial=True)
        user_status.is_valid(raise_exception=True)
        user_status.save()

        Audit.objects.create(
        user=request.user,
        log_type='COURSES',
        call_function = 'exercise_unlock_update_view',
        http_response_status_code = 200,
        result = f'{user} unlocked updated for {exercise.title}'
        )

        return Response(user_status.data, status=status.HTTP_200_OK)
    return Response("برای دسترسی به این قسمت باید وارد شوہید", status=status.HTTP_401_UNAUTHORIZED)

