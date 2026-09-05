from rest_framework import serializers
from points.models import UserPoint


class StageSerializer(serializers.ModelSerializer):
    first_name = serializers.SerializerMethodField()
    last_name = serializers.SerializerMethodField()

    class Meta:
        model = UserPoint
        fields = ['id', 'user', 'first_name', 'last_name', 'points']
    

class UserPointSerializer(serializers.ModelSerializer):
    sum_points = serializers.SerializerMethodField()
    class Meta:
        model = UserPoint
        fields = ['id', 'user', 'points', 'activity_type', 'activity_id', 'details', 'created_at',  'sum_points']
    
    def get_sum_points(self, obj):
        user_point =  UserPoint.objects.filter(user=obj.user).all()
        return sum(point.points for point in user_point)    

