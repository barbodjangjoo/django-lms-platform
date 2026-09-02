from django.contrib import admin
from . import models

@admin.register(models.UserPoint)
class UserPointAdmin(admin.ModelAdmin):
    model = models.UserPoint
    list_display = ['user', 'points', 'activity_type', 'activity_id','created_at']
    search_fields = ["user__username__icontains", "user__first_name__icontains", "user__last_name__icontains"]
    ordering = ['user']