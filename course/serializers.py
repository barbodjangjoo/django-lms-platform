from rest_framework import serializers

from . import models
from notifications.models import Notification
# from payment import models as payment_model
# from payment import serializers as payment_serializer
# from cart.models import UserCourseAccess

class ChapterListForCourseDetailSerializer(serializers.ModelSerializer):
    class Meta:
        model= models.Chapter
        fields = [
            'id',
            'course',
            'title',
            'description',
            'order',
            'chapter_time'
        ]

class CategorySerializer(serializers.ModelSerializer):
    class Meta:
        model = models.Category
        fields = ['id', 'title', 'description']

class CourseUserStatusSerializer(serializers.ModelSerializer):
    factor = serializers.SerializerMethodField()
    has_access = serializers.SerializerMethodField()
    class Meta:
        model = models.CourseUserStatus
        fields = [
        "user",
        "course",
        "is_seen",
        "is_lock",
        "is_complited",
        "datetime_created",
        "datetime_modified",
        "has_access",
        'factor',
        ]

        
    def get_factor(self, obj):
        purchase_item = payment_model.PurchaseItem.objects.filter(
            user=obj.user,
            reference_id = obj.course.id
        ).select_related('factor').last()

        if purchase_item:
            serializer = payment_serializer.FactorSerializer(
                purchase_item.factor
            )
            return serializer.data
        return None

    def get_has_access(self, obj):
        access = UserCourseAccess.objects.filter(
            user= obj.user,
            course= obj.course.id
        ).exists()
        if access:
            return True
        return None
    
class CourseSerializer(serializers.ModelSerializer):
    user_status = serializers.SerializerMethodField()

    class Meta:
        model = models.Course
        fields = [
            'id',
            'cover',
            'title',
            'slug',
            'category',
            'teacher',
            'description',
            'top_section',
            'bottom_section',
            'order',
            'course_time',
            'price',
            'discount',
            'create_at',
            'update_at',
            'user_status'
        ]
    def get_user_status(self, obj):
        request = self.context.get('request')
        user = request.user
        if user.is_authenticated:
            user_stat = models.CourseUserStatus.objects.filter(user=user, course=obj) 
            if user_stat.exists():
                serializer= CourseUserStatusSerializer(user_stat, many=True)
                return serializer.data
        return None

class CourseDetailSerializer(serializers.ModelSerializer):
    user_status = serializers.SerializerMethodField()
    chapters = serializers.SerializerMethodField()
    class Meta:
        model = models.Course
        fields = [
            'id',
            'cover',
            'title',
            'slug',
            'category',
            'teacher',
            'description',
            'top_section',
            'bottom_section',
            'order',
            'course_time',
            'price',
            'discount',
            'create_at',
            'update_at',
            'chapters',
            'user_status',
        ]
    def get_user_status(self, obj):
        request = self.context.get('request')
        user = request.user
        if user.is_authenticated:
            user_stat = models.CourseUserStatus.objects.filter(user=user, course=obj) 
            if user_stat.exists():
                serializer= CourseUserStatusSerializer(user_stat, many=True)
                return serializer.data
        return None
    
    def get_chapters(self, obj):
        chapters = models.Chapter.objects.filter(course=obj).all()
        serializer = ChapterListForCourseDetailSerializer(chapters, many=True)
        return serializer.data
    
class UserChapterStatusSerializers(serializers.ModelSerializer):
    class Meta:
        model = models.UserChapterStatus
        fields = [
            'id', 
            'user',
            'course',
            'chapter',
            'is_lock',
            'is_started',
            'is_completed',
        ]


class ChapterSerializer(serializers.ModelSerializer):
    user_status= serializers.SerializerMethodField()
    class Meta:
        model = models.Chapter
        fields = [
            'id',
            'course',
            'cover',
            'title',
            'slug',
            'description',
            'order',
            'chapter_time',
            'user_status'
        ]

    def get_user_status(self, obj):
        request = self.context.get('request')
        user = request.user
        if user.is_authenticated:
            user_stat = models.UserChapterStatus.objects.filter(user=user, chapter=obj) 
            if user_stat.exists():
                serializer= UserChapterStatusSerializers(user_stat, many=True)
                return serializer.data
        return None
    


class UserLessonStatusSerializer(serializers.ModelSerializer):
    class Meta:
        model = models.UserLessonStatus
        fields = [
            'id',
            'course',
            'chapter',
            'user',
            'lesson',
            'watermarked_video',
            'is_seen',
            'is_lock',
            'seen_at',
            'datetime_created'
        ]

class LessonListSerializer(serializers.ModelSerializer):
    user_status = serializers.SerializerMethodField()
    class Meta:
        model = models.Lesson
        fields = [
        "id",
        "course"
        , "chapter"
        , "cover"
        , "title"
        , "slug"
        , "order"
        , "lesson_time"
        , "create_at"
        , "update_at"
        ,'video_url'
        ,'user_status'
        ]
    def get_user_status(self, obj):
        request = self.context.get('request')
        user = request.user
        if user.is_authenticated:
            user_stat = models.UserLessonStatus.objects.filter(user=user, lesson=obj).first()
            if user_stat:
                serializer= UserLessonStatusSerializer(user_stat, context=self.context)
                return serializer.data
        return None

class LessonSerializer(serializers.ModelSerializer):
    # user_status = serializers.SerializerMethodField()
    # cover = serializers.ImageField()
    # cover_url = serializers.SerializerMethodField()
    video_url = serializers.SerializerMethodField()
    first_name = serializers.SerializerMethodField()
    last_name = serializers.SerializerMethodField()
    phone_number = serializers.SerializerMethodField()
    class Meta:
        model = models.Lesson
        fields = ['id', 'chapter', 'video_url', 'cover', 'title', 'lesson_image', 'slug', 'description', 'order', 'lesson_time', 'first_name', 'last_name', 'phone_number']

    # def get_user_status(self, obj):
    #     request = self.context.get('request')
    #     user = request.user
    #     if user.is_authenticated:
    #         user_stat = models.UserLessonStatus.objects.filter(user=user, lesson=obj).get()
    #         if user_stat:
    #             serializer= UserLessonStatusSerializer(user_stat, many=True, context=self.context)
    #             return serializer.data
    #     return None
    def get_video_url(self, obj):
        request = self.context.get('request')
        if not request or not request.user.is_authenticated:
            return None

        user = request.user
        
        # Get or create user lesson status
        user_status = models.UserLessonStatus.objects.filter(
            user=user, 
            lesson=obj
        ).first()

        # If no video exists, return None
        if not obj.video:
            return None

        # If watermarked video exists, return it
        if user_status and user_status.watermarked_video:
            return request.build_absolute_uri(user_status.watermarked_video.url)
        
        # If no watermarked video, create user status and trigger watermark generation
        if not user_status:
            user_status = models.UserLessonStatus.objects.create(
                user=user,
                lesson=obj
            )
        
        # Trigger watermark generation task
        # from .task import generate_watermarked_video_task_fast
        # generate_watermarked_video_task_fast.delay(
        #     lesson_id=obj.id,
        #     user_id=user.id,
        #     status_id=user_status.id
        # )
        
        # Return original video temporarily
        return request.build_absolute_uri(obj.video.url)

    def get_cover_url(self, obj):
        request = self.context.get('request')
        if obj.cover and request:
            return request.build_abolute_uri(obj.cover.url)
        return None
    
    def get_first_name(self, obj):
        request = self.context.get('request')
        user= request.user
        return user.first_name
    
    def get_last_name(self, obj):
        request = self.context.get('request')
        user= request.user
        return user.last_name
    
    def get_phone_number(self, obj):
        request = self.context.get('request')
        user= request.user
        return user.phone_number


    def get_video_url(self, obj):
        request = self.context.get('request')
        if obj.video and request:
            return request.build_absolute_uri(obj.video.url)
        return None


class LessonCommentSerializer(serializers.ModelSerializer):
    first_name = serializers.CharField(source='user.first_name', required=False)
    last_name = serializers.CharField(source='user.last_name', required=False)
    replies = serializers.SerializerMethodField()
    like_count = serializers.SerializerMethodField()
    like = serializers.SerializerMethodField()

    class Meta:
        model = models.LessonComment
        read_only_fields = ['id', 'datetime_created']
        fields = ['id', 'lesson', 'first_name', 'last_name', 'body', 'parent', 'like', 'like_count', 'replies', 'datetime_created']

    def get_like(self, obj):
        request = self.context.get('request')
        if request and hasattr(request, 'user') and request.user.is_authenticated:
            return obj.like.filter(id=request.user.id).exists()
        return False


    def get_replies(self, comment):
        replies = models.LessonComment.objects.filter(parent_id=comment.id)
        return LessonCommentSerializer(replies, many=True, context=self.context).data

    def get_like_count(self, obj):
        return obj.like.count()
    
class QuizUserStatusSerializer(serializers.ModelSerializer):
    class Meta:
        model = models.QuizUserStatus
        fields = ['user', 'quiz', 'is_seen', 'is_pass', 'is_lock']

    def create(self, validated_data):
        user = self.context['user']
        quiz = self.context['quiz']
        return models.QuizUserStatus.objects.create(user=user, quiz=quiz, **validated_data)


class QuizListSerializer(serializers.ModelSerializer):
    type = serializers.SerializerMethodField()
    user_attempt = serializers.SerializerMethodField()
    user_status = serializers.SerializerMethodField()
    class Meta:
        model = models.Quiz
        fields = ['id', 'lesson','cover','type', 'title', 'slug', 'order', 'user_status', 'user_attempt']
    def get_type(self, obj):
        return 'quiz'

    def get_user_status(self, obj):
        request = self.context.get('request')
        user = request.user
        if user.is_authenticated:
            user_stat = models.QuizUserStatus.objects.filter(user=user, quiz=obj).all()
            if user_stat:
                serializer= QuizUserStatusSerializer(user_stat, many=True, context=self.context)
                return serializer.data
        return None
    
    def get_user_attempt(self, obj):
        request = self.context.get('request')
        if request.user.is_authenticated:
            attempt_query = models.QuizAttemptTracker.objects.filter(quiz=obj, user=request.user).first()
            if attempt_query:
                return QuizAttemptTrackerSerializer(attempt_query).data
            else:
                return None  
        else:
            return None


class QuizUserAnswerSerializer(serializers.ModelSerializer):
    class Meta:
        model = models.QuizUserAnswer
        fields = ['id', 'user', 'quiz', 'question', 'selected_option']

class QuizQuestionSerializer(serializers.ModelSerializer):
    class Meta:
        model = models.QuizQuestion
        fields = ['id', 'order', 'text', 'option_1', 'option_2', 'option_3', 'option_4']

class QuizAttemptTrackerSerializer(serializers.ModelSerializer):
    class Meta:
        model = models.QuizAttemptTracker
        fields = ['id', 'quiz', 'attempt_count']


class QuizSerializer(serializers.ModelSerializer):
    questions = QuizQuestionSerializer(many=True)
    user_attempt = serializers.SerializerMethodField()

    class Meta:
        model = models.Quiz
        fields = ['id', 'cover', 'user_attempt' ,'title', 'order','questions']

    def get_cover_url(self, obj):
        request = self.context.get('request')
        if obj.cover and request:
            return request.build_absolute_uri(obj.cover.url)
        return None
    
    def get_user_attempt(self, obj):
        request = self.context.get('request')
        if request.user.is_authenticated:
            attempt_query = models.QuizAttemptTracker.objects.filter(quiz=obj, user=request.user).first()
            if attempt_query:
                return QuizAttemptTrackerSerializer(attempt_query).data
            else:
                return None  
        else:
            return None

class QuizDetailSerializer(serializers.ModelSerializer):
    questions = QuizQuestionSerializer(many=True)
    user_answers = serializers.SerializerMethodField()

    class Meta:
        model = models.Quiz
        fields = ['id', 'title', 'slug', 'order', 'questions', 'user_answers']

    def get_user_answers(self, obj):
        user = self.context.get('request').user
        user_answers = models.QuizUserAnswer.objects.filter(
            user=user, quiz=obj)
        return [
            {
                'question_id': answer.question.id,
                'selected_option': answer.selected_option,
                'is_correct': answer.is_correct
            }
            for answer in user_answers
        ]


# class ExerciseSerializer(serializers.ModelSerializer):

    # user_status = serializers.SerializerMethodField()

    # class Meta:
    #     model = models.Exercise
    #     fields = [
    #         'id',
    #         'cover',
    #         'lesson',
    #         'title',
    #         'slug',
    #         'question',
    #         'order',
    #         'user_status'
    #     ]
    #     read_only_fields = ['id' , 'cover','lesson', 'title', 'slug', 'question', 'order']

    # def get_user_status(self, obj):
    #     user = self.context.get('request').user
    #     try:
    #         user_status = models.UserExerciseStatus.objects.get(user=user, exercise=obj)
    #         return {
    #             'is_seen': user_status.is_seen,
    #             'status': user_status.status,
    #             'user_answer': user_status.user_answer,
    #             'user_answer_file': user_status.user_answer_file.url if user_status.user_answer_file else None,
    #             'admin_feedback': user_status.admin_feedback,
    #             'points': user_status.points,
    #         }
    #     except models.UserExerciseStatus.DoesNotExist:
    #         return {
    #             'is_seen': False,
    #             'status': 'not_started',
    #             'user_answer': None,
    #             'user_answer_file': None,
    #             'admin_feedback': None,
    #             'points': None,
    #         }
    # def get_cover_url(self, obj):
    #     request = self.context.get('request')
    #     if obj.cover and request:
    #         return request.build_absolute_uri(obj.cover.url)
    #     return None

class ExerciseUserStatusSerializer(serializers.ModelSerializer):
    class Meta:
        model = models.UserExerciseStatus
        fields = [
            'is_seen',
            'is_lock',
            'status',
            'points'
        ]
class NotificationMessageSerializer(serializers.ModelSerializer):
    id = serializers.IntegerField(source='pk')
    feedback_text = serializers.CharField(source='message')
    datetime_created = serializers.DateTimeField(source='created_at')

    class Meta:
        model = Notification
        fields = ['id', 'feedback_text', 'datetime_created']

class ExerciseSerializer(serializers.ModelSerializer):
    user_status= serializers.SerializerMethodField()
    type = serializers.SerializerMethodField()
    class Meta:
        model = models.Exercise
        fields = ['id', 'course', 'chapter', 'cover','type', 'lesson', 'title', 'slug', 'question', 'order', 'user_status', ]

    def get_type(self, obj):
        return 'exercise'

    def get_user_status(self, obj):
        request = self.context.get('request')
        user= request.user
        if user.is_authenticated:
            user_stat = models.UserExerciseStatus.objects.filter(user=user, exercise=obj).all()
            if user_stat:
                serializer = ExerciseUserStatusSerializer(user_stat, many=True, context=self.context)
                return serializer.data
        return None

class ExerciseUserAnswerSerializer(serializers.ModelSerializer):
    class Meta:
        model = models.ExerciseUserAnswer
        fields = ['id', 'user_text_answer',
                  'user_file_answer', 'datetime_created', ]


class AdminFeedBackSerializer(serializers.ModelSerializer):
    class Meta:
        model = models.AdminExerciseFeedback
        fields = ['id', 'feedback_text', 'feedback_file', 'datetime_created']


class FinalExamQuestionSerializer(serializers.ModelSerializer):
    class Meta:
        model = models.FinalExamQuestion
        fields = ['id', 'question_text', 'option_1', 'option_2',
                  'option_3', 'option_4', 'correct_answer', 'is_essay']


class FinalExamSerializer(serializers.ModelSerializer):
    questions = FinalExamQuestionSerializer(many=True)

    class Meta:
        model = models.FinalExam
        fields = ['id', 'cover', 'title', 'slug', 'create_at',
                  'update_at', 'order', 'questions', 'is_seen']

    def get_cover_url(self, obj):
        request = self.context.get('request')
        if obj.cover and request:
            return request.build_absolute_uri(obj.cover.url)
        return None
    
class LessonWithDetailsSerializer(serializers.ModelSerializer):
    exercises = serializers.SerializerMethodField()
    quizzes = serializers.SerializerMethodField()
    user_status = serializers.SerializerMethodField()
    type= serializers.SerializerMethodField()

    class Meta:
        model = models.Lesson
        fields = ['id', 'title', 'order', 'lesson_time','type','user_status', 'exercises', 'quizzes',  ] 
    
    def get_type(self, obj):
        return 'lesson'

    def get_user_status(self, obj):
        request = self.context.get('request')
        user = request.user
        if user.is_authenticated:
            user_stat = models.UserLessonStatus.objects.filter(user=user, lesson=obj).first()
            if user_stat:
                serializer= UserLessonStatusSerializer(user_stat, context=self.context)
                return serializer.data
        return None

    def get_exercises(self, obj):
        request = self.context.get('request')
        exercises = models.Exercise.objects.filter(lesson=obj)
        return ExerciseSerializer(exercises, many=True, context={'request': request}).data

    def get_quizzes(self, obj):
        request = self.context.get('request')
        quizzes = models.Quiz.objects.filter(lesson=obj)
        return QuizListSerializer(quizzes, many=True, context={'request': request}).data
