# ai_classroom/students/serializers.py

from rest_framework import serializers
from .models import Student  # .models หมายถึง models.py ในแอป students เอง

class StudentSerializer(serializers.ModelSerializer):
    class Meta:
        model = Student
        # แก้ไข: ในโมเดลของคุณไม่มี field ชื่อ 'student_class'
        # เราจะเลือก field ที่มีอยู่จริงแทน
        fields = ['student_id', 'full_name', 'created_at']