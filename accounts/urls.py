from django.urls import path
from rest_framework_simplejwt.views import (
    TokenObtainPairView,
    TokenRefreshView,
    TokenVerifyView
)
from . import views

urlpatterns = [
    path('token/', TokenObtainPairView.as_view(), name='token_obtain_pair'),
    path('token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),
    path('token/verify/', TokenVerifyView.as_view(), name='token_verify'),
    path('registration/', views.user_registeration_view, name='user_register'),
    path('send_otp/', views.send_otp_view, name='send_otp' ),
    path('verify_otp/', views.verify_otp_view, name='verify_otp'),
    path('dashboard/', views.user_dashboard_view, name='dashboard'),
    path('update/', views.user_update_view, name='user_update'),
    path('profile/', views.profile_view, name='profile'),
    path('password/change/', views.change_password_view, name='password_change'),
    path('get_me/', views.get_me, name='get_me'),

    path("password-reset/", views.password_reset_view, name="password_reset_api"),
    path("reset/<uidb64>/<token>/", views.PasswordResetConfirmTemplateView.as_view(), name="password_reset_confirm"),
    path("reset/done/", views.PasswordResetCompleteTemplateView.as_view(), name="password_reset_complete"),

    path('reset-password/', views.reset_password_view, name='reset-password'),
]
