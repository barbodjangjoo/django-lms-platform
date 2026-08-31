from datetime import timezone
from django.db import models
from django.contrib.auth import get_user_model
from django.utils.text import slugify
from tinymce.models import HTMLField
from ckeditor_uploader.fields import RichTextUploadingField

# from points.models import UserPoint


class Category(models.Model):
    title = models.CharField(max_length=255, unique=True)
    description =models.TextField(blank=True, null=True)

    def __str__(self):
        return self.title


class Course(models.Model):
    cover = models.ImageField(upload_to='course_cover/', blank=True, null=True)
    title = models.CharField(max_length=255)
    slug = models.SlugField(allow_unicode=True, unique=True)
    category = models.ForeignKey(Category, on_delete=models.PROTECT, related_name='categories')
    teacher = models.CharField(max_length=255)
    description = RichTextUploadingField(blank=True)
    top_section = RichTextUploadingField(blank=True)
    bottom_section = RichTextUploadingField(blank=True)
    order = models.PositiveIntegerField()
    course_time = models.CharField(max_length=100)
    discount = models.IntegerField(default=0)
    price = models.PositiveBigIntegerField()
    is_approve_process = models.BooleanField(default=False)

    create_at = models.DateTimeField(auto_now_add=True)
    update_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f'{self.title}'


    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.title, allow_unicode=True)
        super().save(*args, **kwargs)

    class Meta:
        ordering = ['order']


class CourseUserStatus(models.Model):
    user = models.ForeignKey(get_user_model(), on_delete=models.CASCADE, related_name='course_statuses')
    course = models.ForeignKey('Course', on_delete=models.CASCADE, related_name='user_statuses')
    is_seen = models.BooleanField(default=False)
    is_lock = models.BooleanField(default=True)
    is_complited = models.BooleanField(default=False)

    datetime_created = models.DateTimeField(auto_now_add=True)
    datetime_modified = models.DateTimeField(auto_now=True)

    class Meta:
        unique_together = ('user', 'course')

    def __str__(self):
        return f'{self.user.first_name} - {self.user.last_name} - {self.course.title}'


# class CourseComment(models.Model):
#     REACTION_CHOICES = (
#         ('1','☹️'),
#         ('2','🙁'),
#         ('3','😐'),
#         ('4','☺️'),
#         ('5','😍'),
#     )
#     course = models.ForeignKey(Course, on_delete=models.CASCADE)
#     user = models.ForeignKey(get_user_model(), on_delete=models.CASCADE)
#     reaction = models.CharField(max_length=1, choices=REACTION_CHOICES, blank=True, null=True)
#     body = models.TextField()
#     parent = models.ForeignKey(
#         'self', null=True, blank=True, on_delete=models.CASCADE, related_name='replies'
#     )

#     is_active = models.BooleanField(default=True)
#     create_at = models.DateTimeField(auto_now_add=True)


#     def __str__(self):
#         return f'{self.user} - {self.description}'


class Chapter(models.Model):
    course = models.ForeignKey(Course, on_delete=models.PROTECT, related_name='chapters')
    cover = models.ImageField(upload_to='chapter_cover/', blank=True, null=True)
    title = models.CharField(max_length=255)
    slug = models.SlugField(allow_unicode=True, unique=True)
    description = HTMLField(blank=True, null=True)
    order = models.PositiveIntegerField()
    chapter_time = models.CharField(max_length = 100)

    create_at = models.DateTimeField(auto_now_add=True)
    update_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['order']

    def __str__(self):
        return self.title

class UserChapterStatus(models.Model):
    user = models.ForeignKey(get_user_model(), on_delete=models.CASCADE)
    course = models.ForeignKey(Course, on_delete=models.CASCADE, related_name='course_chapter_status',blank=True, null=True)
    chapter = models.ForeignKey(Chapter, on_delete=models.CASCADE, related_name='chapter_status',blank=True, null=True)
    is_lock = models.BooleanField(default=True)
    is_started = models.BooleanField(default=False)
    is_completed = models.BooleanField(default=False)

    datetime_created = models.DateTimeField(auto_now_add=True)
    datetime_modified = models.DateTimeField(auto_now=True)

    class Meta:
        unique_together = ('user', 'chapter')

    def __str__(self):
        return f"{self.user.username} - {self.chapter}"

# class ChapterComment(models.Model):
#     REACTION_CHOICES = (
#         ('1','☹️'),
#         ('2','🙁'),
#         ('3','😐'),
#         ('4','☺️'),
#         ('5','😍'),
#     )
#     chapter = models.ForeignKey(Chapter, on_delete=models.CASCADE)
#     user = models.ForeignKey(get_user_model(), on_delete=models.CASCADE)
#     reaction = models.CharField(max_length=1, choices=REACTION_CHOICES)
#     body = models.TextField()
#     parent = models.ForeignKey(
#         'self', null=True, blank=True, on_delete=models.CASCADE, related_name='replies'
#     )

#     is_active = models.BooleanField(default=True)
#     create_at = models.DateTimeField(auto_now_add=True)

#     def __str__(self):
#         return f'{self.user} - {self.chapter} - {self.body}'

class Lesson(models.Model):
    course = models.ForeignKey(Course, on_delete=models.PROTECT, related_name='course')
    chapter= models.ForeignKey(Chapter, on_delete=models.PROTECT, related_name='lessons')
    cover = models.ImageField(upload_to='lesson_cover/', blank=True, null=True, default='lesson_cover/game.png')
    video = models.FileField(upload_to='lesson_videos/', null=True, blank=True)
    title = models.CharField(max_length=255)
    lesson_image= models.ImageField(upload_to='lesson_image/', blank=True, null=True)
    slug = models.SlugField(allow_unicode=True, unique=True)
    description = models.TextField()
    order = models.PositiveIntegerField()
    lesson_time = models.CharField(max_length = 100)

    create_at = models.DateTimeField(auto_now_add=True)
    update_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['order']

    def __str__(self):
        return f'{self.title} - {self.order} - {self.lesson_time}'

class LessonComment(models.Model):
    lesson = models.ForeignKey(Lesson, on_delete=models.CASCADE)
    user = models.ForeignKey(get_user_model(), on_delete=models.CASCADE)
    body = models.TextField(blank=True, null=True)
    like = models.ManyToManyField(get_user_model(), default=0, blank=True, related_name='lesson_likes')
    parent = models.ForeignKey(
        'self', null=True, blank=True, on_delete=models.CASCADE, related_name='replies'
    )
    is_active = models.BooleanField(default=True)

    datetime_created = models.DateTimeField(auto_now_add=True)
    datetime_modified = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f'{self.user} - {self.lesson} - {self.body}'


class UserLessonStatus(models.Model):
    course = models.ForeignKey(Course, on_delete=models.CASCADE, related_name='course_lesson_status', null=True, blank=True)
    chapter = models.ForeignKey(Chapter, on_delete=models.CASCADE, related_name='chapter_lesson_status', null=True, blank=True)
    user = models.ForeignKey(get_user_model(), on_delete=models.CASCADE)
    lesson = models.ForeignKey(Lesson, on_delete=models.CASCADE,related_name='user_lesson_statuses')
    watermarked_video = models.FileField(upload_to='watermarked_videos/', null=True, blank=True)
    is_seen = models.BooleanField(default=False)
    is_lock = models.BooleanField(default=True)
    seen_at = models.DateTimeField(auto_now=True)

    datetime_created = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ('user', 'lesson')

    def __str__(self):
        return f"{self.user.username} - {self.lesson.title}"

class Exercise(models.Model):
    course = models.ForeignKey(Course, on_delete=models.CASCADE, related_name='exercises', blank=True, null= True)
    chapter = models.ForeignKey(Chapter, on_delete=models.CASCADE, related_name='exercise_chapter', blank=True, null= True)
    cover = models.ImageField(upload_to='exercise_cover/', blank=True, null=True)
    lesson = models.ForeignKey(Lesson, on_delete=models.PROTECT)
    title = models.CharField(max_length=255)
    slug = models.SlugField(allow_unicode=True, unique=True)
    question = models.TextField()
    order = models.PositiveIntegerField()

    class Meta:
        ordering = ['order']

    def __str__(self):
        return self.title

class UserExerciseStatus(models.Model):
    STATUS_CHOICES = [
        ('not_attempted', 'Not Attempted'),
        ('pending', 'Pending'),
        ('approved', 'Approved'),
        ('rejected', 'Rejected'),
    ]
    POINT_CHOICES = [
        (500, 'Perfect(500pt)'),
        (350, 'Good(350pt)'),
        (250, 'Bad(250pt)'),
        (0, 'Not Done(0pt)'),
    ]
    user = models.ForeignKey(get_user_model(), on_delete=models.CASCADE, related_name='exercise_statuses')
    exercise = models.ForeignKey(Exercise, on_delete=models.CASCADE, related_name='user_statuses')
    is_seen = models.BooleanField(default=False)
    status = models.CharField(max_length=15, choices=STATUS_CHOICES, blank=True, default='not_attempted')
    is_lock = models.BooleanField(default=True)
    points = models.IntegerField(choices=POINT_CHOICES, blank=True, null=True)
    adminfeedback = models.ManyToManyField('AdminExerciseFeedback', blank=True, related_name='feedback_from_admin')
    useranswers = models.ManyToManyField('ExerciseUserAnswer', blank=True, related_name='answers_from_exercise')
    lastuseranswer = models.DateTimeField()
    lastadminfeedback = models.DateTimeField()

    datetime_crated = models.DateTimeField(auto_now_add=True)
    datetime_modfied = models.DateTimeField(auto_now=True)


    class Meta:
        unique_together = ('user', 'exercise')

    def __str__(self):
        try:
            # Try to access user.username, which will trigger a query if not prefetched
            username = self.user.username
            return f'{username} - {self.status}'
        except (AttributeError, KeyError):
            # Fallback if user is not loaded or doesn't exist
            user_id = getattr(self, 'user_id', '?')
            return f'User #{user_id} - {self.status}'

class ExerciseUserAnswer(models.Model):
    user = models.ForeignKey(get_user_model(), on_delete=models.CASCADE)
    exercise = models.ForeignKey(Exercise, on_delete=models.CASCADE)
    user_text_answer = models.TextField(blank=True, null=True)
    user_file_answer = models.FileField(upload_to='user_answer/', blank=True, null=True)
    useranswer_status = models.ForeignKey(UserExerciseStatus, on_delete=models.CASCADE, blank=True, null=True, related_name='user_answer_status')

    datetime_created = models.DateTimeField(auto_now_add=True)
   

    def __str__(self):
        try:
            # Try to access user.username and exercise.title, which will trigger queries if not prefetched
            username = self.user.username
            exercise_title = self.exercise.title
            return f'{username} - {exercise_title}'
        except (AttributeError, KeyError):
            # Fallback if user or exercise is not loaded or doesn't exist
            user_id = getattr(self, 'user_id', '?')
            exercise_id = getattr(self, 'exercise_id', '?')
            return f'User #{user_id} - Exercise #{exercise_id}'

class AdminExerciseFeedback(models.Model):
    user = models.ForeignKey(get_user_model(), on_delete=models.CASCADE)
    exercise = models.ForeignKey(Exercise, on_delete=models.CASCADE)
    exercise_useranswer = models.ForeignKey(UserExerciseStatus, on_delete=models.CASCADE, blank=True, null=True)
    feedback_text = models.TextField(blank=True, null=True)
    feedback_file = models.FileField(upload_to='admin_feedback/', blank=True, null=True)
    adminfeedback_exercise_status = models.ForeignKey(UserExerciseStatus, on_delete=models.CASCADE, blank=True, null=True, related_name='feedback_status')

    datetime_created = models.DateTimeField(auto_now_add=True)
    

    def __str__(self):
        try:
            # Try to access exercise.title and user.username, which will trigger queries if not prefetched
            exercise_title = self.exercise.title
            username = self.user.username
            return f'{exercise_title} - {username}'
        except (AttributeError, KeyError):
            # Fallback if exercise or user is not loaded or doesn't exist
            exercise_id = getattr(self, 'exercise_id', '?')
            user_id = getattr(self, 'user_id', '?')
            return f'Exercise #{exercise_id} - User #{user_id}'


# class ExerciseComment(models.Model):
#     exercise = models.ForeignKey(Exercise, on_delete=models.CASCADE)
#     user = models.ForeignKey(get_user_model(), on_delete=models.CASCADE)
#     body = models.TextField()
#     parent = models.ForeignKey(
#         'self', null=True, blank=True, on_delete=models.CASCADE, related_name='replies'
#     )


class Quiz(models.Model):
    cover = models.ImageField(upload_to='quiz_cover/', blank=True, null=True)
    lesson = models.ForeignKey(Lesson, on_delete=models.CASCADE, related_name='quizzes')
    title = models.CharField(max_length=255)
    slug = models.SlugField(allow_unicode=True, unique=True)
    create_at = models.DateTimeField(auto_now_add=True)
    update_at = models.DateTimeField(auto_now=True)
    order = models.PositiveIntegerField()

    def __str__(self):
        return f'{self.title} for {self.lesson.title}'

class QuizQuestion(models.Model):
    quiz = models.ForeignKey(Quiz, on_delete=models.CASCADE, related_name='questions')
    order = models.PositiveIntegerField()
    text = models.TextField()
    option_1 = models.CharField(max_length=255, blank=True, null=True)
    option_2 = models.CharField(max_length=255, blank=True, null=True)
    option_3 = models.CharField(max_length=255, blank=True, null=True)
    option_4 = models.CharField(max_length=255, blank=True, null=True)
    correct_answer = models.PositiveSmallIntegerField(choices=[(1, 'Option 1'), (2, 'Option 2'), (3, 'Option 3'), (4, 'Option 4')])

    def __str__(self):
        return f'{self.quiz.title} - {self.text}'
    
class QuizUserStatus(models.Model):
    user = models.ForeignKey(get_user_model(), on_delete=models.CASCADE)
    quiz = models.ForeignKey(Quiz, on_delete=models.CASCADE, related_name='quiz_user_status')
    points = models.IntegerField(blank=True, null=True)
    is_seen = models.BooleanField(default=False)
    is_pass = models.BooleanField(default=False)
    is_lock = models.BooleanField(default=True)

    def __str__(self):
        return f'{self.user.username} - {self.quiz.title}'

class QuizUserAnswer(models.Model):
    user = models.ForeignKey(get_user_model(), on_delete=models.CASCADE)
    quiz = models.ForeignKey(Quiz, on_delete=models.CASCADE)
    question = models.ForeignKey(QuizQuestion, on_delete=models.CASCADE)
    selected_option = models.PositiveSmallIntegerField(choices=[(1, 'Option 1'), (2, 'Option 2'), (3, 'Option 3'), (4, 'Option 4')], blank=True, null=True)
    is_correct = models.BooleanField(default=False)
    is_seen = models.BooleanField(default=False)
    is_pass = models.BooleanField(default=False)
    is_lock = models.BooleanField(default=True)

    def __str__(self):
        return f'Answer by {self.user} for {self.question}'

class QuizAttemptTracker(models.Model):
    user = models.ForeignKey(get_user_model(), on_delete=models.CASCADE)
    quiz = models.ForeignKey(Quiz, on_delete=models.CASCADE)
    attempt_count = models.PositiveIntegerField(default=0)

    class Meta:
        unique_together = ('user', 'quiz')
    


    def increment_attempt(self):
        self.attempt_count += 1
        self.save()


class FinalExam(models.Model):
    cover= models.ImageField(upload_to='finalexam_cover/', blank=True, null=True)
    chapter = models.ForeignKey(Chapter, on_delete=models.CASCADE, related_name='final_exams')
    title = models.CharField(max_length=255)
    slug = models.SlugField(unique=True,allow_unicode=True)
    order = models.PositiveIntegerField()

    datetime_created = models.DateTimeField(auto_now_add=True)
    datetime_modified = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['order']

    def __str__(self):
        return f'{self.title} for {self.chapter.title}'


class FinalExamQuestion(models.Model):
    final_exam = models.ForeignKey(FinalExam, on_delete=models.CASCADE, related_name='questions')
    order = models.PositiveIntegerField()
    question_text = models.TextField()
    option_1 = models.CharField(max_length=255, blank=True, null=True)
    option_2 = models.CharField(max_length=255, blank=True, null=True)
    option_3 = models.CharField(max_length=255, blank=True, null=True)
    option_4 = models.CharField(max_length=255, blank=True, null=True)
    correct_answer = models.PositiveSmallIntegerField(
        choices=[(1, 'Option 1'), (2, 'Option 2'), (3, 'Option 3'), (4, 'Option 4')],
        blank=True,
        null=True
    )
    is_essay = models.BooleanField(default=False)

    class Meta:
        ordering = ['order']

    def __str__(self):
        return f'{self.question_text} (Essay: {self.is_essay})'
    
class FinalExamUserStatus(models.Model):
    STATUS_CHOICES = [
        ('not_attempted', 'Not Attempted'),
        ('pending', 'Pending'),
        ('approved', 'Approved'),
        ('rejected', 'Rejected'),
    ]
    POINT_CHOICES = [
        (500, 'Perfect(500pt)'),
        (350, 'Good(350pt)'),
        (250, 'Bad(250pt)'),
        (0, 'Not Done(0pt)'),
    ]
    user = models.ForeignKey(get_user_model(), on_delete=models.CASCADE)
    final_exam = models.ForeignKey(FinalExam, on_delete=models.CASCADE)
    is_pass = models.BooleanField(blank=True, null=True)
    is_seen = models.BooleanField(default=False)
    points = models.IntegerField(choices=POINT_CHOICES, blank=True, null=True)
    adminfeedback = models.ManyToManyField("FinalExamAdminFeedback", related_name="finalexam_feedback",blank=True)
    useranswer = models.ManyToManyField("FinalExamUserAnswer",blank=True, null=True)
    

    datetime_created = models.DateTimeField(auto_now_add=True)
    datetime_modified = models.DateTimeField(auto_now=True)

class FinalExamAdminFeedback(models.Model):
    user = models.ForeignKey(get_user_model(), on_delete=models.CASCADE)
    finalexam = models.ForeignKey(FinalExam, on_delete=models.CASCADE, blank=True, null=True)
    final_exam_status = models.ForeignKey(FinalExamUserStatus, on_delete=models.CASCADE, related_name="finalexam_adminfeedback", blank=True, null=True)
    adminfeedback = models.TextField()
    adminfile = models.FileField(upload_to='finalexam_admin_feedback/', blank=True, null=True)

    datetime_created = models.DateTimeField(auto_now_add=True)
    datetime_modified = models.DateTimeField(auto_now=True)

class FinalExamUserAnswer(models.Model):
    user = models.ForeignKey(get_user_model(), on_delete=models.CASCADE)
    final_exam_status = models.ForeignKey(FinalExam, on_delete=models.CASCADE, null=True, blank=True)
    exam_status = models.ForeignKey(FinalExamUserStatus, on_delete=models.CASCADE, blank=True, null=True)
    question = models.ForeignKey(FinalExamQuestion, on_delete=models.CASCADE, null=True, blank=True)
    selected_option = models.PositiveSmallIntegerField(
        choices=[(1, 'Option 1'), (2, 'Option 2'), (3, 'Option 3'), (4, 'Option 4')],
        null=True,
        blank=True
    )
    user_answer = models.TextField(blank=True, null=True)
    user_fileanswer = models.FileField(blank=True, null=True)

    datetime_created = models.DateTimeField(auto_now_add=True)
    datetime_modified = models.DateTimeField(auto_now=True)
    class Meta:
        unique_together = ('user', 'question')

    def __str__(self):
        return f'Answer by {self.user} for {self.question}'


# __________________________------------------


# class FinalExam(models.Model):
#     course = models.ForeignKey(Course, on_delete=models.CASCADE)
#     chapter = models.ForeignKey(Chapter, on_delete=models.CASCADE)  
#     title = models.CharField(max_length=255)
#     description = models.TextField(blank=True)

#     datetime_created = models.DateTimeField(auto_now_add=True)

# class FinalExamQuestion(models.Model):
#     QUESTION_TYPES = (
#         ('MCQ', 'Multiple Choice'),
#         ('TEXT', 'Descriptive'),
#     )
#     exam = models.ForeignKey(FinalExam, on_delete=models.CASCADE, related_name="questions")
#     question_text = models.TextField()
#     question_type = models.CharField(max_length=10, choices=QUESTION_TYPES)
#     order = models.PositiveIntegerField(default=0)
#     # choices = models.JSONField(blank=True, null=True) # berese be
#     correct_answer = models.CharField(max_length=10, blank=True, null=True)  

#     datetime_created = models.DateTimeField(auto_now_add=True)
#     datetime_modified = models.DateTimeField(auto_now=True)

# class FinalExamStatus(models.Model):
#     STATUS_CHOICES = [
#         ('not_attempted', 'Not Attempted'),
#         ('pending', 'Pending'),
#         ('approved', 'Approved'),
#         ('rejected', 'Rejected'),
#     ]
#     POINT_CHOICES = [
#         (1000, 'Perfect(1000pt)'),
#         (500, 'Good(500pt)'),
#         (350, 'Bad(350pt)'),
#         (0, 'Not Done(0pt)'),
#     ]
#     user = models.ForeignKey(get_user_model(), on_delete=models.CASCADE)
#     exam = models.ForeignKey(FinalExam, on_delete=models.CASCADE, related_name='submissions')
#     points = models.IntegerField(choices=POINT_CHOICES, blank=True, null=True)
#     status = models.CharField(choices=STATUS_CHOICES, max_length=10)
#     overall_feedback = models.TextField(blank=True, null=True)

#     datetime_created = models.DateTimeField(auto_now_add=True)

# class FinalExamAnswer(models.Model):
#     status = models.ForeignKey(FinalExamStatus, on_delete=models.CASCADE, related_name='answers')
#     question = models.ManyToManyField(FinalExamQuestion, on_delete=models.CASCADE)
#     answer_text = models.TextField()  
#     is_correct = models.BooleanField(null=True, blank=True)
#     feedback = models.TextField(blank=True, null=True)  
#     # score = models.FloatField(blank=True, null=True)

# # class FinalExamAdminFeedback(models.Model)