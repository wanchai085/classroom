# students/admin.py
from django.contrib import admin
from .models import Student

@admin.register(Student)
class StudentAdmin(admin.ModelAdmin):
    list_display = ('student_id', 'full_name', 'user', 'created_at', 'password_changed')
    search_fields = ('student_id', 'full_name', 'user__username')
    list_filter = ('password_changed',)