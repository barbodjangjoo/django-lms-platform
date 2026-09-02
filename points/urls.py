from django.urls import path

from . import views

app_name = 'points'

urlpatterns = [
    path('stage/', views.stage_view, name='stage_view'),
    path('user/', views.user_points_view, name='user_points_view'),
]