from django.contrib.auth.models import Group
from django.contrib import admin


class UserGroupFilter(admin.SimpleListFilter):
    title = 'User Group'
    parameter_name = 'user_group'

    def lookups(self, request, model_admin):
        return [(group.id, group.name) for group in Group.objects.all()]

    def queryset(self, request, queryset):
        if self.value():
            return queryset.filter(user__groups__id=self.value())
        return queryset
