from django.contrib import admin
from .models import Audit

@admin.register(Audit)
class AuditAdmin(admin.ModelAdmin):
    list_display = ("user", "log_type", "call_function", "http_response_status_code", "log_datetime")
    list_filter = (
        "log_type",
        "http_response_status_code",
        "log_datetime",
        "user",
    )
    search_fields = ("call_function", "result", "user__first_name__icontains", "user__last_name__icontains", "user__phone_number__icontains",)
    date_hierarchy = "log_datetime"
    ordering = ("-log_datetime",)
