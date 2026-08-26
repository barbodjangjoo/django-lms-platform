from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from jalali_date.admin import ModelAdminJalaliMixin

from .models import CustomUser


@admin.register(CustomUser)
class CustomUserAdmin(ModelAdminJalaliMixin ,UserAdmin):
    list_display = ["id" ,"first_name", "last_name", "phone_number"]
    list_filter = ["birth_date", "gender", "city", "address", "educational_status", "find"]
    add_fieldsets = (
        (
            None,
            {
                "classes": ("wide",),
                "fields": (
                    "username",
                    "password1",
                    "password2",
                    "profile_picture",
                    "first_name",
                    "last_name",
                    "birth_date",
                    "gender",
                    "city",
                    "address",
                    "educational_status",
                    "phone_number",
                    "email",
                    "find",
                    ),
            },
        ),
    )
    fieldsets = (
        (
            ("Permissions"),
            {
                "fields": (
                    "is_active",
                    "is_staff",
                    "is_superuser",
                    "groups",
                    "user_permissions",
                ),
            },
        ),
        (None,
            {
                "fields": (
                    "username",
                    "password",
                    "profile_picture",
                    "first_name",
                    "last_name",
                    "birth_date",
                    "gender",
                    "city",
                    "address",
                    "educational_status",
                    "phone_number",
                    "email",
                    "find",
                ),
            },
        ),
    )
