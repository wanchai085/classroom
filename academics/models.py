# ai_classroom/academics/models.py

from django.db import models
from django.contrib.auth.models import User
from django.utils import timezone
from decimal import Decimal
import random
import string
from datetime import timedelta  # <<< เพิ่ม import timedelta

# Import โมเดล Student เข้ามาเพื่อใช้ใน property ของ Classroom
from students.models import Student


def generate_random_code(length=6):
    """ฟังก์ชันสำหรับสร้างรหัสสุ่ม"""
    return ''.join(random.choices(string.ascii_uppercase + string.digits, k=length))


# ... (Subject, Classroom, Enrollment, GradeComponent, Assignment, Submission, BehaviorRecord models เหมือนเดิม) ...
class Subject(models.Model):
    LEVEL_CHOICES = [
        ('PRIMARY', 'ประถมศึกษา'),
        ('SECONDARY', 'มัธยมศึกษา'),
    ]

    teacher = models.ForeignKey(User, on_delete=models.CASCADE, related_name='subjects_taught', verbose_name="คุณครู")
    name = models.CharField(max_length=100, verbose_name="ชื่อวิชา")

    # ===== แก้ไข Field นี้ =====
    # 1. ทำให้ "รหัสวิชา" เป็น Field ที่บังคับกรอก และไม่ซ้ำกันสำหรับครูคนหนึ่งๆ
    subject_code = models.CharField(max_length=20, verbose_name="รหัสวิชา")

    education_level = models.CharField(max_length=10, choices=LEVEL_CHOICES, verbose_name="ระดับชั้น")
    image = models.ImageField(upload_to='subject_images/', blank=True, null=True, verbose_name="รูปภาพประจำวิชา")
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        # ===== แก้ไข unique_together =====
        # 2. เปลี่ยนให้คู่ของ (รหัสวิชา, ครู) เป็นสิ่งที่ไม่ซ้ำกัน
        unique_together = ('subject_code', 'teacher')
        verbose_name = "วิชา"
        verbose_name_plural = "วิชา"

    def __str__(self):
        return f"{self.name} ({self.subject_code})"

class Classroom(models.Model):
    subject = models.ForeignKey(Subject, on_delete=models.CASCADE, related_name='classrooms', verbose_name="วิชา")
    class_name = models.CharField(max_length=100, verbose_name="ชื่อห้องเรียน")

    class Meta: unique_together = ('subject',
                                   'class_name'); verbose_name = "ห้องเรียน"; verbose_name_plural = "ห้องเรียน"

    def __str__(self): return f"{self.subject.name} - {self.class_name}"

    @property
    def students(self): return Student.objects.filter(enrollments__classroom=self)


class Enrollment(models.Model):
    student = models.ForeignKey('students.Student', on_delete=models.CASCADE, related_name='enrollments')
    classroom = models.ForeignKey('academics.Classroom', on_delete=models.CASCADE, related_name='enrollments')
    midterm_score = models.DecimalField(max_digits=5, decimal_places=2, null=True, blank=True,
                                        verbose_name="คะแนนกลางภาค")
    final_score = models.DecimalField(max_digits=5, decimal_places=2, null=True, blank=True,
                                      verbose_name="คะแนนปลายภาค")
    total_score = models.DecimalField(max_digits=5, decimal_places=2, default=0.00, verbose_name="คะแนนรวม")
    final_grade = models.DecimalField(max_digits=2, decimal_places=1, null=True, blank=True, verbose_name="เกรดสุดท้าย")
    date_enrolled = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ('student', 'classroom'); verbose_name = "การลงทะเบียน"; verbose_name_plural = "การลงทะเบียน"

    def __str__(self):
        return f"{self.student.full_name} in {self.classroom.class_name}"

    def update_scores(self):
        component_scores = self.components.aggregate(total=models.Sum('score'))['total'] or Decimal('0.00')
        midterm = self.midterm_score or Decimal('0.00');
        final = self.final_score or Decimal('0.00')
        self.total_score = component_scores + midterm + final
        score = self.total_score
        if score >= 80:
            self.final_grade = Decimal('4.0')
        elif score >= 75:
            self.final_grade = Decimal('3.5')
        elif score >= 70:
            self.final_grade = Decimal('3.0')
        elif score >= 65:
            self.final_grade = Decimal('2.5')
        elif score >= 60:
            self.final_grade = Decimal('2.0')
        elif score >= 55:
            self.final_grade = Decimal('1.5')
        elif score >= 50:
            self.final_grade = Decimal('1.0')
        else:
            self.final_grade = Decimal('0.0')
        self.save(update_fields=['total_score', 'final_grade'])


class GradeComponent(models.Model):
    enrollment = models.ForeignKey(Enrollment, on_delete=models.CASCADE, related_name='components')
    name = models.CharField(max_length=100, verbose_name="ชื่อองค์ประกอบคะแนน")
    score = models.DecimalField(max_digits=5, decimal_places=2, verbose_name="คะแนนที่ได้")

    def __str__(self): return f"{self.name} for {self.enrollment.student.full_name}"


class Assignment(models.Model):
    classroom = models.ForeignKey(Classroom, on_delete=models.CASCADE, related_name='assignments',
                                  verbose_name="ห้องเรียน")
    title = models.CharField(max_length=200, verbose_name="ชื่อชิ้นงาน")
    description = models.TextField(blank=True, null=True, verbose_name="รายละเอียด")
    attachment = models.FileField(upload_to='assignments/%Y/%m/%d/', blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    due_date = models.DateTimeField()
    max_score = models.DecimalField(max_digits=5, decimal_places=2, null=True, blank=True, verbose_name="คะแนนเต็ม")

    def __str__(self): return self.title


class Submission(models.Model):
    enrollment = models.ForeignKey(Enrollment, on_delete=models.CASCADE, related_name='submissions')
    assignment = models.ForeignKey(Assignment, on_delete=models.CASCADE, related_name='submissions')
    submitted_at = models.DateTimeField(default=timezone.now)
    attachment = models.FileField(upload_to='submissions/%Y/%m/%d/')
    grade = models.DecimalField(max_digits=5, decimal_places=2, null=True, blank=True)
    feedback = models.TextField(blank=True, null=True, verbose_name="คอมเมนต์/ผลตอบกลับ")

    class Meta: unique_together = ('enrollment', 'assignment')

    @property
    def student(self): return self.enrollment.student

    @property
    def is_late(self): return self.submitted_at > self.assignment.due_date


class BehaviorRecord(models.Model):
    BEHAVIOR_CHOICES = [('POSITIVE', 'พฤติกรรมเชิงบวก'), ('NEGATIVE', 'พฤติกรรมเชิงลบ'), ]
    enrollment = models.ForeignKey(Enrollment, on_delete=models.CASCADE, related_name='behaviors')
    behavior_type = models.CharField(max_length=10, choices=BEHAVIOR_CHOICES)
    points = models.IntegerField();
    record_text = models.TextField(verbose_name="รายละเอียดพฤติกรรม")
    date_recorded = models.DateTimeField(auto_now_add=True)

    @property
    def student(self): return self.enrollment.student

    def __str__(self): return f"Behavior for {self.student.full_name} in {self.enrollment.classroom}"


# ===================================================================
# โมเดลสำหรับระบบเช็คชื่อ (ฉบับครูกำหนดเวลาเอง)
# ===================================================================
class AttendanceSession(models.Model):
    classroom = models.ForeignKey(Classroom, on_delete=models.CASCADE, related_name='attendance_sessions')
    created_by = models.ForeignKey(User, on_delete=models.CASCADE)
    code = models.CharField(max_length=10, default=generate_random_code, unique=True, editable=False)

    # เปลี่ยนจาก expires_at เป็น start_time และ end_time
    start_time = models.DateTimeField(verbose_name="เวลาเริ่มต้น")
    end_time = models.DateTimeField(verbose_name="เวลาสิ้นสุด")

    created_at = models.DateTimeField(auto_now_add=True)

    @property
    def is_active(self):
        """ตรวจสอบว่า Session นี้ยังอยู่ในช่วงเวลาที่สามารถเช็คชื่อได้หรือไม่"""
        now = timezone.now()
        return self.start_time <= now <= self.end_time

    def __str__(self):
        return f"Session for {self.classroom} ({self.start_time.strftime('%H:%M')} - {self.end_time.strftime('%H:%M')})"


class AttendanceRecord(models.Model):
    session = models.ForeignKey(AttendanceSession, on_delete=models.CASCADE, related_name='records')
    student = models.ForeignKey('students.Student', on_delete=models.CASCADE, related_name='attendances')
    timestamp = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ('session', 'student')

    def __str__(self):
        return f"{self.student.full_name} attended {self.session.classroom}"