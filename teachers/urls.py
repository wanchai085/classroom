# D:\classroom\teachers\urls.py
from django.urls import path
from . import views

app_name = 'teachers'

urlpatterns = [
    path('', views.teacher_dashboard_view, name='dashboard'),
    path('subject/create/', views.subject_create_view, name='subject_create'),
    path('subject/<int:pk>/update/', views.subject_update_view, name='subject_update'),
    path('subject/<int:pk>/delete/', views.subject_delete_view, name='subject_delete'),
    path('subjects/', views.subject_list_view, name='subject_list'),
    path('subject/<int:pk>/', views.subject_detail_view, name='subject_detail'),
    # URL หลักของห้องเรียน
    path('classroom/<int:pk>/', views.classroom_detail_view, name='classroom_detail'),
    # URL สำหรับแก้ไขห้องเรียน เช่น /teachers/classroom/10/update/
    path('classroom/<int:pk>/update/', views.classroom_update_view, name='classroom_update'),
    # URL สำหรับลบห้องเรียน เช่น /teachers/classroom/10/delete/
    path('classroom/<int:pk>/delete/', views.classroom_delete_view, name='classroom_delete'),
    # URL รายละเอียดนักเรียน
    path('classroom/<int:classroom_pk>/student/<str:student_pk>/', views.student_detail_teacher_view,
         name='student_detail'),

    # ===== ปิด URL เหล่านี้ชั่วคราว =====
     path('classroom/<int:classroom_pk>/attendance/', views.manage_attendance_session, name='manage_attendance'),
     path('api/attendance-session/<int:session_pk>/records/', views.get_attendance_records_api, name='api_get_attendance_records'),
    path('risk-students/', views.risk_students_view, name='risk_students'),
    path('document-storage/', views.document_storage_view, name='document_storage'),
]