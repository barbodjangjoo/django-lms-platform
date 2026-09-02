from django.db import models
from django.contrib.auth import get_user_model



class UserPoint(models.Model):
    user = models.ForeignKey(get_user_model(), on_delete=models.CASCADE, related_name='points')
    points = models.IntegerField(default=0) 
    ACTIVITY_TYPES = [
        ('QUIZ', 'Quiz completion'),
        ('EXERCISE', 'Exercise completion'),
        ('FINAL_EXAM', 'Final exam completion'),
        ('PROFILE', 'Profile completion'),
        ('ADMIN_CUSTOM', 'Admin custom points'), 
        ('CHALLENGE', 'Challenge'),
    ]
    activity_type = models.CharField(max_length=50, choices=ACTIVITY_TYPES)
    activity_id = models.CharField(max_length=50) 
    details = models.TextField(blank=True, null=True) 
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ('user', 'activity_type', 'activity_id')

    def __str__(self):
        return f"{self.user} - {self.points} points for {self.activity_type} ({self.activity_id})"
