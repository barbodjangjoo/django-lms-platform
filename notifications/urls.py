from django.urls import path
from . import views


urlpatterns = [
    path('list/', views.notification_list_view, name='notification_list'),
    path('<int:pk>/read/', views.mark_notifications_read_view, name='mark_notifications_read'),
    # path('', views.NotificationListView.as_view(), name='notification-list'),
]
