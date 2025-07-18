# ai_classroom/academics/signals.py

from django.db.models.signals import post_save, post_delete
from django.dispatch import receiver
from django.urls import reverse
from .models import GradeComponent
from django.contrib.auth.models import User

# แก้ไข import ให้ถูกต้องตามตำแหน่งใหม่
from .models import GradeComponent, Enrollment, Assignment, Submission
from accounts.models import Notification # Notification อยู่ในแอป accounts

# ===== 1. Signal สำหรับอัปเดตคะแนนรวมเมื่อ GradeComponent เปลี่ยนแปลง =====
@receiver([post_save, post_delete], sender=GradeComponent)
def update_enrollment_on_component_change(sender, instance, **kwargs):
    instance.enrollment.update_scores()

# ===== 2. Signal สำหรับเชื่อมคะแนน Submission ไปยัง GradeComponent อัตโนมัติ =====
@receiver(post_save, sender=Submission)
def create_or_update_grade_component_from_submission(sender, instance, created, **kwargs):
    # ทำงานเฉพาะเมื่อมีการให้คะแนนแล้วเท่านั้น
    if instance.grade is not None:
        GradeComponent.objects.update_or_create(
            enrollment=instance.enrollment,
            name=f"ชิ้นงาน: {instance.assignment.title}",
            defaults={'score': instance.grade}
        )
    # ถ้ามีการลบคะแนน (grade is None) แต่ component ยังอยู่, อาจจะต้องลบทิ้งด้วย
    elif not created and instance.grade is None:
        GradeComponent.objects.filter(
            enrollment=instance.enrollment,
            name=f"ชิ้นงาน: {instance.assignment.title}"
        ).delete()


# ===== 3. Signals สำหรับระบบแจ้งเตือน (Notification) =====
@receiver(post_save, sender=Assignment)
def create_assignment_notification(sender, instance, created, **kwargs):
    if created:
        enrollments = instance.classroom.enrollments.select_related('student__user').all()
        for enrollment in enrollments:
            if enrollment.student.user:
                message = f"งานใหม่: '{instance.title}' ในวิชา '{instance.classroom.subject.name}'"
                # แก้ไข reverse ให้ใช้ namespace
                link = reverse('students:subject_detail', kwargs={'enrollment_pk': enrollment.pk})
                Notification.objects.create(user=enrollment.student.user, message=message, link=link)


@receiver(post_save, sender=Submission)
def create_submission_and_grading_notification(sender, instance, created, **kwargs):
    teacher = instance.assignment.classroom.subject.teacher
    student_user = instance.student.user

    # แจ้งเตือนครูเมื่อมีการส่งงานครั้งแรก
    if created:
        message = f"'{instance.student.full_name}' ได้ส่งงาน '{instance.assignment.title}'"
        # แก้ไข reverse ให้ใช้ namespace
        link = reverse('academics:assignment_detail', kwargs={'pk': instance.assignment.pk})
        Notification.objects.create(user=teacher, message=message, link=link)

    # แจ้งเตือนนักเรียนเมื่อครูตรวจงาน (เมื่อมีการใส่คะแนนหรือคอมเมนต์)
    # ใช้ instance.tracker.has_changed('grade') จะดีกว่า แต่เพื่อความง่าย ใช้แบบนี้ไปก่อน
    if not created and student_user:
        # เช็คว่าเพิ่งมีการให้คะแนนหรือไม่ (จากเดิมเป็น None)
        message = f"ครูตรวจงาน '{instance.assignment.title}' ของคุณแล้ว"
        # แก้ไข reverse ให้ใช้ namespace
        link = reverse('students:subject_detail', kwargs={'enrollment_pk': instance.enrollment.pk})
        Notification.objects.create(user=student_user, message=message, link=link)



@receiver([post_save, post_delete], sender=GradeComponent)
def update_enrollment_on_component_change(sender, instance, **kwargs):
    """
    ทำงานทุกครั้งที่ GradeComponent ถูกสร้าง, อัปเดต, หรือลบ
    เพื่อให้แน่ใจว่า Enrollment จะคำนวณคะแนนรวมใหม่เสมอ
    """
    # การเรียก .save() ที่นี่ จะไป trigger เมธอด save ที่เรา override ไว้ใน Enrollment model
    instance.enrollment.save()