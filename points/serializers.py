from rest_framework import serializers
from points.models import UserPoint
from challenge.models import UserMissionStatus
from challenge import models as challenges

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

class UserMissionPointsSerializer(serializers.ModelSerializer):
    activity_type = serializers.SerializerMethodField()
    points = serializers.SerializerMethodField()
    activity_id = serializers.SerializerMethodField()
    created_at = serializers.DateTimeField(source="datetime_modified",read_only=True)
    details = serializers.SerializerMethodField()
    class Meta:
        model = UserMissionStatus
        fields = [
            'id',
            'user',
            'points',
            'activity_type',
            "activity_id",
            'details',
            'created_at',
        ]
    
    def get_activity_type(self, obj):
        return "CHALLENGE"
    
    def get_activity_id(self, obj):
        return obj.id
    
    def get_points(self, obj):
        return obj.admin_points 
    
    def get_details(self, obj):
        return f'امتیاز برای چلنج {obj.challenge.title} کسب شده است!'
