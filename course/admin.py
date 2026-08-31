from django.contrib import admin
# from import_export.admin import ExportMixin
# from import_export import resources, fields
from . import models
from .filters import UserGroupFilter
from tinymce.widgets import TinyMCE

# --------- resources ---------
# class UserLessonStatusResource(resources.ModelResource):
#       class Meta:
#             model = models.UserLessonStatus
#             fields = ('user__username', 'lesson', 'is_seen', 'is_lock', 'seen_at')
#             export_order = ('user_username', 'lesson__title', 'is_seen', 'is_lock', 'seen_at')

# class UserExerciseStatusResource(resources.ModelResource):
#     class Meta:
#         model = models.UserExerciseStatus
#         fields = (
#             'user__username',
#             'exercise__title',
#             'status',
#             'is_seen',
#             'is_lock',
#             'points',
#             'datetime_crated',
#             'datetime_modfied',
#         )
#         export_order = (
#             'user__username',
#             'exercise__title',
#             'status',
#             'is_seen',
#             'is_lock',
#             'points',
#             'datetime_crated',
#             'datetime_modfied',
#         )
# class ExerciseUserAnswerResource(resources.ModelResource):
#     user__username = fields.Field(attribute='user__username', column_name='Username')
#     exercise__title = fields.Field(attribute='exercise__title', column_name='Exercise Title')

#     class Meta:
#         model = models.ExerciseUserAnswer
#         fields = (
#             'user__username',
#             'exercise__title',
#             'user_text_answer',
#             'user_file_answer',
#             'useranswer_status',
#             'datetime_created',
#         )
#         export_order = (
#             'user__username',
#             'exercise__title',
#             'user_text_answer',
#             'user_file_answer',
#             'useranswer_status',
#             'datetime_created',
#         )
# class AdminExerciseFeedbackResource(resources.ModelResource):
#     user__username = fields.Field(attribute='user__username', column_name='Username')
#     exercise__title = fields.Field(attribute='exercise__title', column_name='Exercise Title')

#     class Meta:
#         model = models.AdminExerciseFeedback
#         fields = (
#             'user__username',
#             'exercise__title',
#             'exercise_useranswer',
#             'adminfeedback_exercise_status',
#             'feedback_text',
#             'feedback_file',
#             'datetime_created',
#         )
#         export_order = (
#             'user__username',
#             'exercise__title',
#             'exercise_useranswer',
#             'adminfeedback_exercise_status',
#             'feedback_text',
#             'feedback_file',
#             'datetime_created',
#         )
# class QuizResource(resources.ModelResource):
#     lesson__title = fields.Field(attribute='lesson__title', column_name='Lesson Title')

#     class Meta:
#         model = models.Quiz
#         fields = (
#             'lesson__title',
#             'title',
#             'slug',
#             'order',
#             'create_at',
#             'update_at',
#         )
#         export_order = (
#             'lesson__title',
#             'title',
#             'slug',
#             'order',
#             'create_at',
#             'update_at',
#         )

# class QuizQuestionResource(resources.ModelResource):
#     quiz__title = fields.Field(attribute='quiz__title', column_name='Quiz Title')

#     class Meta:
#         model = models.QuizQuestion
#         fields = (
#             'quiz__title',
#             'order',
#             'text',
#             'option_1',
#             'option_2',
#             'option_3',
#             'option_4',
#             'correct_answer',
#         )
#         export_order = (
#             'quiz__title',
#             'order',
#             'text',
#             'option_1',
#             'option_2',
#             'option_3',
#             'option_4',
#             'correct_answer',
#         )
# --------- tabular inlines ---------
# class CourseCommentInline(admin.TabularInline):
#     model = models.CourseComment
#     fields = ['user', 'reaction', 'body', 'is_active']
#     extra= 1

class ChapterAdminInline(admin.TabularInline):
        model = models.Chapter
        list_display =[
            'title',
            'course',
            'description',
            'chapter_time',
             'order'
             ]
        extra = 0

class LessonCommentTabularAdmin(admin.TabularInline):
      model = models.LessonComment
      extra = 0
      list_display = ["user", "body", "parent" ,"is_active"]
      # readonly_fields = ["user",]

class UserLessonStatus(admin.TabularInline):
      model = models.UserLessonStatus
      list_display = ["user", "lesson", "is_seen", "is_lock", "seen_at"]
      readonly_fields = ["user", "lesson","watermarked_video", "is_seen", "seen_at"]
      extra = 0

class LessonTabularAdmin(admin.StackedInline):
        model = models.Lesson
        extra = 0
        list_display = ['title', 'description', 'order', 'chapter', 'slug']
        inlines = [
              LessonCommentTabularAdmin
        ]
class QuizQuestionStackedInline(admin.StackedInline):
      model = models.QuizQuestion
      extra = 0
      list_display = ["quiz", "order", "text", "option_1", "option_2", "option_3", "option_4", "correct_answer"]

class QuizUserAnswerTabular(admin.StackedInline):
      model = models.QuizUserAnswer
      extra = 0
      list_display = [
            "user",
            "quiz",
            "question",
            "selected_option",
            "is_correct",
            "is_seen",
            "is_pass",
            "is_lock",
      ]
      readonly_fields= ['user', 'question', 'quiz', 'selected_option', 'is_correct', 'is_seen', 'is_pass']

class QuizAttemptTrackerInline(admin.TabularInline):
      model = models.QuizAttemptTracker
      extra = 0
      list_display = ["user", "attempt_count"]

class ExerciseTabularAdmin(admin.TabularInline):
      model= models.Exercise
      list_display = ["lesson", "title", "slug", "order"]
      extra = 0

# class ExerciseCommentTabular(admin.TabularInline):
#       model = models.ExerciseComment
#       list_display = ["user", "body"]
#       extra = 0
#       readonly_fields = ['user', 'body']
#       min_num = 1

class ExerciseAdminFeedbackTabular(admin.TabularInline):
      model = models.AdminExerciseFeedback
      list_display = ["user", "exercise", "datetime_created"]
      extra = 0
      readonly_fields = ["user", "exercise"]
      search_fields = ["user__username__icontains", "user__first_name__icontains", "user__last_name__icontains", "exercise__title"]
      list_filter = ['user', 'exercise',]
      def get_queryset(self, request):
            return super().get_queryset(request).select_related('user', 'exercise')

class AdminExerciseFeedbackExerciseInline(admin.StackedInline):
    model = models.AdminExerciseFeedback
    extra = 0
    fields = ("exercise" ,"feedback_text", "feedback_file", )
    fk_name = 'adminfeedback_exercise_status'




class ExerciseUserAnswerExerciseInline(admin.StackedInline): # type: ignore
      model = models.ExerciseUserAnswer
      extra = 0
      fields = ("user", "exercise", "user_text_answer", "user_file_answer", )
      fk_name = 'useranswer_status'
      
# class FinalExamQuestionsTabular(admin.StackedInline):
#       model = models.FinalExamQuestion
#       list_display = ["order", "question_text", "option_1", "option_2", "option_3", "option_4", "correct_answer", "is_essay"]
#       extra = 0

# class FinalExamUserAnswerTabular(admin.TabularInline):
#       model = models.FinalExamUserAnswer
#       list_display = [
#             "user", "exam_status", "question", "selected_option", "admin_feedback", "is_correct", "user_answer", "user_fileanswer", "points"
#       ]
#       extra = 0
#       readonly_fields = ["user", "question", "selected_option", "user_answer", "user_fileanswer"]

@admin.register(models.Course)
class CourseAdmin(admin.ModelAdmin):
      # class Media:
      #       js = (
      #       'https://cdn.jsdelivr.net/npm/tinymce@6.8.3/tinymce.min.js',
      #       'js/tinymce_setup.js',
      # )
      resource_class = models.Course
      list_display = ["title", "slug", "teacher", "order"]
      list_filter = ('category', 'teacher', 'create_at', )
      fieldsets = (
            ("general", {'fields':("title","slug","teacher", "is_approve_process", "order","price", 'discount', 'cover', 'category', 'description', 'top_section', 'bottom_section','course_time')}),
      )
      inlines = [
            # CourseCommentInline,
            ChapterAdminInline,
                 ]

      def get_queryset(self, request):
            chapter = models.Lesson.objects.select_related('course', 'chapter')
            return super().get_queryset(request).prefetch_related('chapters',)
@admin.register(models.Chapter)
class ChapterAdmin(admin.ModelAdmin):
      resouce_class= models.Chapter
      list_display= ["course", "title", "slug", "description", "order"]
      fieldsets = (
            ("general", {"fields":("cover", "course", "title", "slug", "description", "order", "chapter_time")}),
      )
      inlines = [
            LessonTabularAdmin,
      ]
      list_filter = ("course", "title", "order")
@admin.register(models.Lesson)
class LessonAdmin(admin.ModelAdmin):
      resource_class = models.Lesson
      list_display = ["id","course" ,"chapter", "title", "slug", "order"]
      list_filter = ['course', 'chapter', 'order']
      fieldsets = (
            ("general", {"fields":( "course", "chapter", "cover", "video", "title", "lesson_image", "slug", "description", "order", "lesson_time",
            )}),
      )
      inlines = [
            LessonCommentTabularAdmin,
            UserLessonStatus,
            ExerciseTabularAdmin
      ]
@admin.register(models.Quiz)
class QuizAdmin(admin.ModelAdmin):
      resource_class = models.Quiz
      list_display = ['lesson', 'title', 'slug', 'order',]
      list_filter = ['lesson', 'title', 'order', 'lesson__chapter', 'lesson__chapter__course']
      fieldset = (
            ("general", {"fields":( "lesson", "title", "slug", "create_at", "update_at", "order")}),
      )
      inlines = [
            QuizQuestionStackedInline,
      ]

@admin.register(models.QuizUserStatus)
class QuizUserStatus(admin.ModelAdmin):
       model = models.QuizUserStatus
       fields = ['user', 'quiz', 'points', 'is_seen', 'is_pass', 'is_lock']

class ExerciseStatusTabularAdmin(admin.TabularInline):
    model = models.UserExerciseStatus
    fields = ["user", "exercise", "points", "status"]
    readonly_fields = ["user", "exercise"]
    extra = 0

class ExerciseUserAnswerExerciseInline(admin.TabularInline):
      model = models.ExerciseUserAnswer

      extra = 0
      list_display = ["user", "exercise", "datetime_created"]
      readonly_fields = ["user", "exercise", "datetime_created"]
      search_fields = ["user__username__icontains", "user__first_name__icontains", "user__last_name__icontains","exercise__title"]
      list_filter = ['user','exercise',]


@admin.register(models.Exercise)
class ExerciseAdmin(admin.ModelAdmin):
      resource_class= models.Exercise
      list_display = ["lesson", "title", "slug", "order"]
      list_filter = [ 'lesson__chapter__course','lesson__chapter','lesson', 'order']
      inlines = [
            # ExerciseCommentTabular,
      ]

# @admin.register(models.FinalExam)
# class FinalExamAdmin(admin.ModelAdmin):
#       resource_class = models.FinalExam
#       list_display = ["chapter", "title", "slug", "order"]
#       list_filter = ['chapter', 'order']
#       inlines = [
#             FinalExamQuestionsTabular,
#             FinalExamUserAnswerTabular
#       ]
@admin.register(models.CourseUserStatus)
class CourseUserStatusAdmin(admin.ModelAdmin):
      resource_class = models.CourseUserStatus
      list_display = ["user", "course", "is_seen"]
      list_filter = ['course', 'is_seen', UserGroupFilter]
      search_fields = ["user__username__icontains", "user__first_name__icontains", "user__last_name__icontains", "course__title"]

@admin.register(models.UserChapterStatus)
class UserChapterStatusAdmin(admin.ModelAdmin):
      resource_class = models.UserChapterStatus
      list_display = ["user", "chapter", "is_lock"]
      list_filter = [
            'user',
            UserGroupFilter,
            'chapter',
            'is_lock',
            'chapter__course'
      ]
      search_fields = ["user__username__icontains", "user__first_name__icontains", "user__last_name__icontains", "chapter__title"]

@admin.register(models.UserLessonStatus)
class UserLessonStatusAdmin(admin.ModelAdmin):
      resource_class = models.UserLessonStatus
      list_display = ["id", "user", "lesson",  "watermarked_video", "is_seen", "is_lock", "seen_at",]
      search_fields = ["user__username__icontains", "user__first_name__icontains", "user__last_name__icontains", "lesson__title"]
      list_filter = [
            'user',
            UserGroupFilter,
            'is_seen',
            'is_lock',
            'lesson__course',
            'lesson__chapter',
            'seen_at',
      ]


@admin.register(models.QuizUserAnswer)
class QuizUserAnswerAdmin(admin.ModelAdmin):
      resource_class = models.QuizUserAnswer
      list_display = ["user", "quiz", "is_correct", "is_pass", "is_lock"]
      list_per_page = 15
      search_fields = ["user__username__icontains", "user__first_name__icontains", "user__last_name__icontains","quiz__title"]
      list_filter = [
      'user',
      UserGroupFilter,
      'is_correct',
      'is_pass',
      'is_lock',
      'quiz',
      'selected_option',
      ]
@admin.register(models.ExerciseUserAnswer)
class ExerciseUserAnswerAdmin(admin.ModelAdmin):
      resource_class = models.ExerciseUserAnswer
      list_display = ["user", "exercise", "datetime_created"]
      readonly_fields = ["user", "exercise", "datetime_created",]
      raw_id_fields = ["useranswer_status"]  # Use raw_id for better performance (avoids loading all records)
      list_per_page = 15
      search_fields = ["user__username__icontains", "user__first_name__icontains", "user__last_name__icontains","exercise__title"]
      list_filter = ['user', 'exercise', 'exercise__lesson', 'exercise__lesson__chapter', 'exercise__lesson__course', UserGroupFilter, 'exercise__order', ]
      
      def get_queryset(self, request):
            return super().get_queryset(request).select_related('user', 'exercise', 'useranswer_status', 'useranswer_status__user', 'useranswer_status__exercise')
      
      def get_form(self, request, obj=None, **kwargs):
            form = super().get_form(request, obj, **kwargs)
            # Optimize the queryset for the raw_id field popup
            # When editing, filter to only show relevant statuses
            if obj and obj.pk and 'useranswer_status' in form.base_fields:
                  if obj.user_id and obj.exercise_id:
                        # Filter to only show statuses for the same user and exercise
                        form.base_fields['useranswer_status'].queryset = models.UserExerciseStatus.objects.filter(
                              user_id=obj.user_id,
                              exercise_id=obj.exercise_id
                        ).select_related('user', 'exercise')
                  else:
                        # Limit to recent records if user/exercise not available
                        form.base_fields['useranswer_status'].queryset = models.UserExerciseStatus.objects.select_related(
                              'user', 'exercise'
                        ).order_by('-datetime_modfied')[:1000]
            return form


@admin.register(models.UserExerciseStatus)
class ExerciseStatusAdmin(admin.ModelAdmin):
	resource_class = models.UserExerciseStatus
	list_display = ('user', 'exercise', 'status', 'points', 'is_seen', 'is_lock', 'datetime_modfied')
	list_filter = [
			'user',
			'exercise',
			UserGroupFilter,
			'exercise__lesson__chapter',
			'exercise__lesson__chapter__course',
			'exercise__lesson',
			'is_lock',
			'status'
		]
	fieldsets = (
		("General Info", {"fields": ("user", "exercise", "is_seen", "status", "is_lock", "points",)}),
	)
	search_fields = ["user__username__icontains", "user__first_name__icontains", "user__last_name__icontains", "exercise__title"]
	readonly_fields = ["user", "exercise"]
	inlines = [ExerciseUserAnswerExerciseInline, AdminExerciseFeedbackExerciseInline]
	list_per_page = 50  # Limit items per page for better performance in popup

	def get_queryset(self, request):
		return super().get_queryset(request).select_related('user', 'exercise')

	def save_formset(self, request, form, formset, change):
		instances = formset.save(commit=False)
		for obj in instances:
			if not obj.user_id:
					obj.user = form.instance.user  
			obj.save()
		formset.save_m2m()


@admin.register(models.AdminExerciseFeedback)
class AdminFeedbackExercise(admin.ModelAdmin):
      resource_class = models.AdminExerciseFeedback
      list_display = ["user", "exercise", "datetime_created"]
      list_filter = ['user', UserGroupFilter, 'exercise', 'exercise__lesson__chapter', 'exercise__lesson__chapter__course']
      search_fields = ["user__username__icontains", "user__first_name__icontains", "user__last_name__icontains", "exercise__title"]
      raw_id_fields = ["exercise_useranswer", "adminfeedback_exercise_status"]  # Use raw_id for better performance
      
      def get_queryset(self, request):
            return super().get_queryset(request).select_related('user', 'exercise', 'exercise_useranswer', 'exercise_useranswer__user', 'exercise_useranswer__exercise', 'adminfeedback_exercise_status', 'adminfeedback_exercise_status__user', 'adminfeedback_exercise_status__exercise')
      
      def get_form(self, request, obj=None, **kwargs):
            form = super().get_form(request, obj, **kwargs)
            # Optimize the queryset for the raw_id fields popup
            # When editing, filter to only show relevant statuses
            if obj and obj.pk:
                  if 'exercise_useranswer' in form.base_fields:
                        if obj.user_id and obj.exercise_id:
                              form.base_fields['exercise_useranswer'].queryset = models.UserExerciseStatus.objects.filter(
                                    user_id=obj.user_id,
                                    exercise_id=obj.exercise_id
                              ).select_related('user', 'exercise')
                        else:
                              form.base_fields['exercise_useranswer'].queryset = models.UserExerciseStatus.objects.select_related(
                                    'user', 'exercise'
                              ).order_by('-datetime_modfied')[:1000]
                  
                  if 'adminfeedback_exercise_status' in form.base_fields:
                        if obj.user_id and obj.exercise_id:
                              form.base_fields['adminfeedback_exercise_status'].queryset = models.UserExerciseStatus.objects.filter(
                                    user_id=obj.user_id,
                                    exercise_id=obj.exercise_id
                              ).select_related('user', 'exercise')
                        else:
                              form.base_fields['adminfeedback_exercise_status'].queryset = models.UserExerciseStatus.objects.select_related(
                                    'user', 'exercise'
                              ).order_by('-datetime_modfied')[:1000]
            return form
