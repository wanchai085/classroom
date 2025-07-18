# ai_classroom/students/urls.py
from django.urls import path
from . import views

app_name = 'students'

urlpatterns = [
    # /students/
    path('', views.student_dashboard_view, name='dashboard'),

    # /students/subject/10/
    path('subject/<int:enrollment_pk>/', views.student_subject_detail_view, name='subject_detail'),
    path('attendance/submit/', views.attendance_view, name='submit_attendance'),
]
