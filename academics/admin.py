# academics/admin.py
from django.contrib import admin
from .models import Subject, Classroom, Enrollment, Assignment, Submission, GradeComponent, BehaviorRecord

@admin.register(Subject)
class SubjectAdmin(admin.ModelAdmin):
    list_display = ('name', 'teacher')
    list_filter = ('teacher',)
    search_fields = ('name',)

@admin.register(Classroom)
class ClassroomAdmin(admin.ModelAdmin):
    list_display = ('class_name', 'subject', 'get_teacher')
    list_filter = ('subject__teacher', 'subject')
    search_fields = ('class_name', 'subject__name')

    @admin.display(description='Teacher')
    def get_teacher(self, obj):
        return obj.subject.teacher.get_full_name() or obj.subject.teacher.username

@admin.register(Enrollment)
class EnrollmentAdmin(admin.ModelAdmin):
    list_display = ('student', 'classroom', 'total_score', 'final_grade')
    list_filter = ('classroom__subject__teacher', 'classroom')
    search_fields = ('student__full_name', 'classroom__class_name')
    readonly_fields = ('total_score', 'final_grade') # ทำให้สองฟิลด์นี้แก้ไขใน admin ไม่ได้

# ลงทะเบียนโมเดลอื่นๆ ที่เหลือแบบง่ายๆ
admin.site.register(Assignment)
admin.site.register(Submission)
admin.site.register(GradeComponent)
admin.site.register(BehaviorRecord)