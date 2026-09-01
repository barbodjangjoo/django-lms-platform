from django.contrib import admin
from . import models

@admin.register(models.Notification)
class NotificationsAdmin(admin.ModelAdmin):
    resource_class = models.Notification
    list_display = ['user', 'notification_type', 'title', 'created_at']
    search_fields = ["user__username__icontains", "user__first_name__icontains", "user__last_name__icontains"]
    ordering = ['created_at']