from django.urls import path

from . import views
# slug -> id

urlpatterns = [
    path('courses/', views.course_list_view, name='course_list'),
    path('courses/<int:pk>/', views.course_detail_view, name='course_detail'),
    path('courses/<int:pk>/is_seen/', views.course_update_is_seen_view, name='course_is_seen'),
    path('courses/<int:pk>/chapters/', views.chapter_list_View, name='chapter_list'),
    path('chapters/<int:pk>/detail', views.chapter_detail_view, name='chapter_detail'),
    path('chapters/<int:pk>/is_started/', views.chapter_update_is_seen_view, name='chapter_is_seen'),
    path('chapters/<int:pk>/unlock/', views.chapter_unlock_view, name='chapter_unlock'), # should develop after exercise
    path('chapters/<int:pk>/lessons/', views.lesson_list_view, name='lesson_list'), #user stat should be here
    path('lessons/<int:pk>/', views.lesson_detail_view, name='lesson_detail'),
    path('lessons/<int:pk>/comments/', views.lesson_comment_view, name='lesson_comment'),
    path('lessons/<int:pk>/comments/submit/', views.lesson_comment_create_view, name='lesson_comment_create'),
    path('comments/<int:pk>/like/', views.lesson_comment_like_view, name='comment_like'),
    path('lessons/<int:pk>/is_seen/', views.lesson_update_is_seen_view, name='lesson_is_seen'),
    path('lessons/<int:pk>/unlock/', views.lesson_update_unlock_view, name='lesson_unlock'),
    path('lessons/<int:pk>/quizzes/', views.quiz_list_view, name='quiz_list'),
    path('quizzes/<int:pk>/', views.quiz_detail_view, name='quiz_detail'),
    path('quizzes/<int:pk>/submit/', views.quiz_answer_submit_view, name='quiz_submit'), #should work on it
    path('quizzes/<int:pk>/resault/', views.quiz_resault_view, name='quiz_resault'),
    path('quizzes/<int:pk>/is_seen/', views.quiz_is_seen_update_view, name='quiz_is_seen'),
    path('quizzes/<int:pk>/unlock/', views.quiz_unlock_update_view, name='quiz_is_seen'),
    path('chapters/<int:pk>/exercises/', views.chapter_exercises_view, name='chapter_exercises'),
    path('lessons/<int:pk>/exercises/', views.exercise_list_view, name='exercise_list'),
    path('exercises/<int:pk>/', views.exercise_detail_view, name='exercise_detail'),
    path('exercises/<int:pk>/submit/', views.exercise_submit_view, name='exercise_submit'),
    path('exercises/<int:pk>/is_seen/', views.exercise_is_seen_update_view, name='exercise_is_seen'),
    path('exercises/<int:pk>/unlock/', views.exercise_unlock_update_view, name='exercise_unlock'),
]
