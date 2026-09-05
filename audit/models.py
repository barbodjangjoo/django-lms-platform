from django.db import models
from django.contrib.auth import get_user_model

class Audit(models.Model):
    LOG_CHOICES = (
        ('AUTHENTICATIONS', 'Authentications'),
        ('COURSES', 'Courses'),
        ('POINTS', 'Points'),
        ('NOTIFICATIONS', 'Notifications'),
        ('PAYMENTS', 'Payment')
    )
    user = models.ForeignKey(get_user_model(), on_delete=models.CASCADE)
    log_type = models.CharField(max_length=15, choices=LOG_CHOICES)
    call_function = models.CharField(max_length=255)
    http_response_status_code = models.IntegerField()
    log_datetime = models.DateTimeField(auto_now=True)
    result = models.TextField()

    def __str__(self):
        return f"{self.user} : {self.call_function}"