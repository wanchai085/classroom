# D:\classroom\academics\urls.py
from django.urls import path
from . import views

app_name = 'academics'

urlpatterns = [
    # URLs สำหรับจัดการ Assignment
    path('assignment/<int:pk>/', views.assignment_detail_view, name='assignment_detail'),
    path('assignment/<int:pk>/update/', views.assignment_update_view, name='assignment_update'),
    path('assignment/<int:pk>/delete/', views.assignment_delete_view, name='assignment_delete'),

    # URLs สำหรับจัดการนักเรียน (ที่ถูกเรียกโดยครู)
    path('student/<str:pk>/update/', views.student_update_view, name='student_update'),

    # ===== เพิ่มบรรทัดนี้เข้าไป! =====
    path('classroom/<int:classroom_pk>/student/<str:student_pk>/remove/', views.student_remove_from_classroom_view,
         name='student_remove_from_classroom'),

    # URLs สำหรับการส่งงานและให้คะแนน
    path('submission/<int:pk>/grade/', views.grade_submission_view, name='grade_submission'),

    # URLs สำหรับเครื่องมืออื่นๆ
    path('classroom/<int:pk>/gradebook/', views.gradebook_view, name='gradebook'),
    path('upload-students/', views.upload_students_view, name='upload_students'),
    path('classroom/<int:to_classroom_pk>/copy-students/', views.copy_students_view, name='copy_students'),
]