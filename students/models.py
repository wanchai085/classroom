from django.db import models
from django.contrib.auth.models import User

class Student(models.Model):
    user = models.OneToOneField(User, on_delete=models.SET_NULL, null=True, blank=True, related_name='student_profile')
    student_id = models.CharField(max_length=20, primary_key=True, verbose_name="รหัสนักเรียน")
    full_name = models.CharField(max_length=200, verbose_name="ชื่อ-นามสกุล")
    password_changed = models.BooleanField(default=False, verbose_name="เปลี่ยนรหัสผ่านครั้งแรกแล้ว")
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.student_id} - {self.full_name}"