# ai_classroom/students/views.py

from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.utils import timezone

# Import ที่จำเป็น
from .models import Student
from academics.models import Enrollment, Assignment, Submission, AttendanceSession, AttendanceRecord
from academics.forms import SubmissionForm
from .forms import AttendanceForm  # <<< Import ฟอร์มใหม่ของเรา


@login_required
def student_dashboard_view(request):
    try:
        student = request.user.student_profile
    except Student.DoesNotExist:
        messages.error(request, "ไม่พบบัญชีนักเรียนของคุณ")
        return redirect('accounts:logout')

    enrollments = Enrollment.objects.filter(student=student).select_related(
        'classroom__subject__teacher').prefetch_related('components').order_by('classroom__subject__name')

    context = {
        'student': student,
        'enrollments': enrollments,
        'attendance_form': AttendanceForm(),  # ส่งฟอร์มเปล่าไปให้ template เผื่อจะทำ Modal
    }
    return render(request, 'students/student_dashboard.html', context)


@login_required
def student_subject_detail_view(request, enrollment_pk):
    # ... (โค้ดส่วนนี้ถูกต้องอยู่แล้ว ไม่ต้องแก้ไข) ...
    enrollment = get_object_or_404(Enrollment.objects.select_related('student__user', 'classroom__subject__teacher'),
                                   pk=enrollment_pk, student__user=request.user)
    if request.method == 'POST':
        form = SubmissionForm(request.POST, request.FILES)
        if form.is_valid():
            assignment = get_object_or_404(Assignment, id=request.POST.get('assignment_id'),
                                           classroom=enrollment.classroom)
            Submission.objects.update_or_create(
                enrollment=enrollment, assignment=assignment,
                defaults={'attachment': form.cleaned_data['attachment'], 'submitted_at': timezone.now()}
            )
            messages.success(request, f"ส่งงาน '{assignment.title}' เรียบร้อยแล้ว")
            return redirect('students:subject_detail', enrollment_pk=enrollment.pk)
    assignments = Assignment.objects.filter(classroom=enrollment.classroom).order_by('-due_date')
    submissions = Submission.objects.filter(enrollment=enrollment, assignment__in=assignments)
    submission_dict = {sub.assignment.pk: sub for sub in submissions}
    context = {
        'enrollment': enrollment, 'assignments': assignments,
        'submission_dict': submission_dict, 'submission_form': SubmissionForm()
    }
    return render(request, 'students/student_subject_detail.html', context)


# ===================================================================
# View ใหม่สำหรับระบบเช็คชื่อ (เพิ่มเข้ามาท้ายไฟล์)
# ===================================================================
@login_required
def attendance_view(request):
    """
    จัดการการรับรหัสเช็คชื่อจากนักเรียน
    """
    student_profile = get_object_or_404(Student, user=request.user)

    # ควรเป็น POST request เท่านั้น
    if request.method == 'POST':
        form = AttendanceForm(request.POST)
        if form.is_valid():
            code = form.cleaned_data['code'].upper()
            now = timezone.now()
            try:
                # หาคาบเรียนที่ยังไม่หมดอายุ, เริ่มแล้ว และมีรหัสตรงกัน
                session = AttendanceSession.objects.get(
                    code=code,
                    start_time__lte=now,
                    end_time__gte=now
                )

                # ตรวจสอบว่านักเรียนคนนี้อยู่ในห้องเรียนนั้นหรือไม่
                if not Enrollment.objects.filter(student=student_profile, classroom=session.classroom).exists():
                    messages.error(request, f"คุณไม่ได้อยู่ในห้องเรียน '{session.classroom}'")
                else:
                    # สร้างบันทึกการเช็คชื่อ
                    record, created = AttendanceRecord.objects.get_or_create(session=session, student=student_profile)
                    if created:
                        messages.success(request, f"เช็คชื่อเข้าห้องเรียน '{session.classroom}' สำเร็จ!")
                    else:
                        messages.warning(request, "คุณได้เช็คชื่อในคาบเรียนนี้ไปแล้ว")

            except AttendanceSession.DoesNotExist:
                messages.error(request, "รหัสไม่ถูกต้อง หรืออยู่นอกช่วงเวลาที่กำหนด")

    # ไม่ว่าจะสำเร็จหรือล้มเหลว ให้กลับไปหน้า dashboard
    return redirect('students:dashboard')