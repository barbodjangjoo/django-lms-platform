from django.db import models
from django.contrib.auth import get_user_model

class Notification(models.Model):
    NOTIFICATION_TYPES = [
        ('POINTS', 'Points Awarded'),
        ('EXERCISE', 'Exercise Status'),
        ('QUIZ', 'Quiz Result'),
        ('PROFILE', 'Profile Update'),
        ('EXAM', 'Final Exam Result'),
        ('ADMIN_NOTIFICATION', 'Admin Notification'),
        ('CHANGE_STATUS', 'Changes_status'),
        ('CHALLENGE', 'challenge')
    ]

    user = models.ForeignKey(get_user_model(), on_delete=models.CASCADE, related_name='notifications')
    notification_type = models.CharField(max_length=20, choices=NOTIFICATION_TYPES)
    title = models.CharField(max_length=255)
    message = models.TextField()
    is_read = models.BooleanField(default=False)
    slug = models.SlugField(max_length=255, blank=True, null=True)
    chapter_slug = models.SlugField(max_length=255, blank=True, null=True)
    lesson_slug = models.SlugField(max_length=255, blank=True, null=True)
    course_slug = models.SlugField(max_length=255, blank=True, null=True)
    chapter_id = models.PositiveIntegerField(blank=True, null=True)  # chapter_id
    lesson_id = models.PositiveIntegerField(blank=True, null=True) # lesson_id 
    course_id = models.PositiveIntegerField(blank=True, null=True) # course_id

    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return f"{self.user.username} - {self.notification_type} - {self.created_at}"
