# teachers/admin.py
from django.contrib import admin
from .models import Teacher

@admin.register(Teacher)
class TeacherAdmin(admin.ModelAdmin):
    list_display = ('user', 'get_full_name', 'get_username')
    search_fields = ('user__username', 'user__first_name', 'user__last_name')

    @admin.display(description='Full Name')
    def get_full_name(self, obj):
        return obj.user.get_full_name()

    @admin.display(description='Username')
    def get_username(self, obj):
        return obj.user.username