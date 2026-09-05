from django.contrib.auth import get_user_model
from django.db.models import Sum
# from django.utils.translation import gettext as _
# from rest_framework.views import APIView
# from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.decorators import api_view
from rest_framework import status

from accounts import models as accounts_models
from course.models import UserExerciseStatus
from course.serializers import ExerciseUserStatusSerializer
from .models import UserPoint
from .serializers import  UserPointSerializer

@api_view(['GET'])
def stage_view(request):
    User = get_user_model()
    users = User.objects.all()
    result = []
    for user in users:
        user_points = UserPoint.objects.filter(user=user).aggregate(total=Sum('points'))['total'] or 0
        exercise_points = UserExerciseStatus.objects.filter(user=user).aggregate(total=Sum('points'))['total'] or 0
        total_points = user_points + exercise_points
        if total_points > 0:
            result.append({
                "id": f'{user.id}',
                "username": f'{user.first_name} - {user.last_name}',
                "total_points": total_points
            })
    result = sorted(result, key=lambda x: x['total_points'], reverse=True)
    return Response({"rankings": result})
        
@api_view(['GET'])
def user_points_view(request):
    if request.user.is_authenticated:
        user = request.user
        user_points = UserPoint.objects.filter(user=user).order_by('-created_at')
        serializer = UserPointSerializer(user_points, many=True)
        exercise_statuses = UserExerciseStatus.objects.filter(user=user, points__gt=0).order_by('-datetime_crated')
        exercise_serializer = ExerciseUserStatusSerializer(exercise_statuses, many=True) 
        total_userpoint = UserPoint.objects.filter(user=user).aggregate(total=Sum('points'))['total'] or 0
        total_exercise = UserExerciseStatus.objects.filter(user=user).aggregate(total=Sum('points'))['total'] or 0
        total_points = total_userpoint + total_exercise 
        return Response({
            "total_points": total_points,
            "userpoint_history": serializer.data,
            "exercisepoint_history": exercise_serializer.data,
        })
    return Response({"detail": "Authentication credentials were not provided."}, status=status.HTTP_401_UNAUTHORIZED) 