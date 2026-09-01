from django.shortcuts import get_object_or_404
from rest_framework.decorators import api_view, permission_classes
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from .models import Notification
from .serializers import NotificationSerializer

@api_view(['GET'])
@permission_classes([IsAuthenticated])
def notification_list_view(request):
    notification_queryset = Notification.objects.filter(user=request.user).order_by('-created_at')
    serializer = NotificationSerializer(notification_queryset, many=True)
    return Response(serializer.data)

@api_view(['PATCH'])
@permission_classes([IsAuthenticated])
def mark_notifications_read_view(request, pk):
    notification = get_object_or_404(Notification, pk=pk, user=request.user)
    updated = NotificationSerializer(notification ,data=request.data, partial=True)
    updated.is_valid(raise_exception=True)
    updated.save()
    return Response(updated.data)
    
