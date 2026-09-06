from rest_framework.permissions import BasePermission
from rest_framework.response import Response
from rest_framework import status
from django.utils.translation import gettext_lazy as _

from .models import CourseUserStatus

class HasAccess(BasePermission):
    message = _('You dont have access to this course please purchase it first!')

    def has_permission(self, request, view):
        if not request.user or not request.user.is_authenticated:
            self.message = _('To use this you need to login first')
            return False
        course_id = view.kwargs.get('course_id') 
        if course_id:
            return CourseUserStatus.objects.filter(user=request.user, course_id=course_id).exists()
        return False
