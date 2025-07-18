# D:\classroom\teachers\views.py

# ==========================================================
# Imports
# ==========================================================
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from django.contrib import messages
from django.db import transaction, IntegrityError
from django.utils import timezone
from datetime import timedelta
from django.http import JsonResponse

# Imports จากแอปอื่นๆ ในโปรเจกต์
from students.models import Student
from accounts.models import Notification # <<< ดึง Notification จาก accounts
from academics.models import (
    Subject, Classroom, Enrollment, Assignment,
    GradeComponent, BehaviorRecord, Submission,
    AttendanceSession, AttendanceRecord
)
from academics.forms import AssignmentForm, GradeComponentForm, BehaviorForm, CoreScoresForm
from .forms import (
    SmartClassroomForm, SubjectUpdateForm, CopyStudentsForm,
    StudentForm, UploadFileForm, AttendanceSessionForm ,ClassroomForm
)
from django.db import models


# ===================================================================
# Views หลัก
# ===================================================================

# ในไฟล์ teachers/views.py

@login_required
def teacher_dashboard_view(request):
    """
    แสดงหน้า Dashboard V3 ที่เน้น Action Widgets
    """
    teacher = request.user

    # --- ดึงข้อมูลสำหรับ Stat Cards และ Widgets ---
    classrooms = Classroom.objects.filter(subject__teacher=teacher)
    total_classrooms = classrooms.count()
    student_pks = Enrollment.objects.filter(classroom__in=classrooms).values_list('student__pk', flat=True).distinct()
    total_students = len(student_pks)

    # ดึงข้อมูลสำหรับ Widgets
    unread_notifications = Notification.objects.filter(user=teacher, is_read=False).order_by('-created_at')[:10]

    now = timezone.now()
    upcoming_assignments = Assignment.objects.filter(
        classroom__in=classrooms,
        due_date__gte=now
    ).order_by('due_date')

    # ===== ส่วนของกลุ่มเสี่ยง (AI) สำหรับ Widget ใหม่ =====
    # ในอนาคต ส่วนนี้จะดึงข้อมูลนักเรียนกลุ่มเสี่ยงจริงๆ
    # ตอนนี้เราจะส่งแค่จำนวนไปก่อน
    risk_students_count = 0
    try:
        from academics.predictor import predict_student_risk
        if total_students > 0:
            students_in_care = Student.objects.filter(pk__in=student_pks)
            for student in students_in_care:
                if 'เสี่ยงสูง' in predict_student_risk(student): risk_students_count += 1
    except (ImportError, Exception):
        risk_students_count = 0
    # ====================================================

    context = {
        'total_subjects': Subject.objects.filter(teacher=teacher).count(),
        'total_classrooms': total_classrooms,
        'total_students': total_students,

        # ส่งข้อมูลสำหรับ Widgets
        'unread_notifications': unread_notifications,
        'upcoming_assignments': upcoming_assignments,
        'risk_students_count': risk_students_count,  # ส่งจำนวนนักเรียนกลุ่มเสี่ยงไป
    }

    return render(request, 'teachers/teacher_dashboard.html', context)
# ===================================================================
# Views จัดการ Subject
# ===================================================================
@login_required
def subject_create_view(request):
    if request.method == 'POST':
        form = SubjectUpdateForm(request.POST, request.FILES)
        if form.is_valid():
            subject = form.save(commit=False);
            subject.teacher = request.user;
            subject.save()
            messages.success(request, f"สร้างวิชา '{subject.name}' เรียบร้อยแล้ว")
            return redirect('teachers:dashboard')
    else:
        form = SubjectUpdateForm()
    context = {'form': form, 'is_create_page': True};
    return render(request, 'academics/subject_form.html', context)


@login_required
def subject_detail_view(request, pk):
    """
    แสดงรายละเอียดของวิชา, รายการห้องเรียนทั้งหมด,
    และจัดการการสร้างห้องเรียนใหม่แบบอัจฉริยะ (เติม ป./ม. อัตโนมัติ)
    """
    subject = get_object_or_404(Subject, pk=pk, teacher=request.user)

    # ▼▼▼ แก้ไข Logic การประมวลผล POST request ทั้งหมดตามนี้ ▼▼▼
    if request.method == 'POST':
        form = ClassroomForm(request.POST)
        if form.is_valid():
            # 1. ดึงชื่อห้องเรียนที่ผู้ใช้กรอก (เช่น "4/1")
            base_class_name = form.cleaned_data['class_name'].strip()

            # 2. กำหนดคำนำหน้า (prefix) ตามระดับชั้นของวิชาปัจจุบัน
            prefix = ""
            if subject.education_level == 'PRIMARY':
                prefix = "ป."
            elif subject.education_level == 'SECONDARY':
                prefix = "ม."

            # 3. รวม prefix กับชื่อห้องเรียน (ถ้ายังไม่มีอยู่แล้ว)
            #    เพื่อป้องกันกรณีผู้ใช้พิมพ์ "ม.4/1" มาเอง
            if prefix and not base_class_name.startswith(prefix):
                final_class_name = f"{prefix}{base_class_name}"
            else:
                final_class_name = base_class_name

            try:
                # 4. บันทึกชื่อที่รวมแล้ว (final_class_name) ลงฐานข้อมูล
                Classroom.objects.create(subject=subject, class_name=final_class_name)
                messages.success(request, f"สร้างห้องเรียน '{final_class_name}' สำเร็จ")
            except IntegrityError:
                messages.error(request, f"ห้องเรียนชื่อ '{final_class_name}' มีอยู่แล้วในวิชานี้")

            return redirect('teachers:subject_detail', pk=subject.pk)
    else:
        # ส่วนนี้ไม่ต้องแก้ไข
        form = ClassroomForm()

    # ส่วนนี้ไม่ต้องแก้ไข
    classrooms_in_subject = subject.classrooms.all().order_by('class_name')

    context = {
        'subject': subject,
        'classrooms': classrooms_in_subject,
        'form': form,
    }
    return render(request, 'teachers/subject_detail.html', context)

@login_required
def subject_update_view(request, pk):
    subject = get_object_or_404(Subject, pk=pk, teacher=request.user)
    if request.method == 'POST':
        # ส่วนนี้ถูกต้องอยู่แล้ว ไม่ต้องแก้ไข
        form = SubjectUpdateForm(request.POST, request.FILES, instance=subject)
        if form.is_valid():
            form.save()  # เครื่องหมาย ; (semicolon) ไม่จำเป็นใน Python ครับ
            messages.success(request, f"อัปเดตวิชา '{subject.name}' เรียบร้อยแล้ว")

            # ▼▼▼ แก้ไขบรรทัดนี้เท่านั้น ▼▼▼
            # เปลี่ยนจาก 'teachers:dashboard' ไปเป็น 'teachers:subject_detail'
            # พร้อมกับส่ง pk ของ subject กลับไปด้วย
            return redirect('teachers:subject_detail', pk=subject.pk)
    else:
        # ส่วนนี้ถูกต้องอยู่แล้ว
        form = SubjectUpdateForm(instance=subject)

    # ส่วนนี้ถูกต้องอยู่แล้ว การส่ง 'subject' ไปใน context นั้นจำเป็น
    # เพื่อให้เราสามารถสร้างลิงก์ "ยกเลิก" ใน template ได้
    context = {'form': form, 'subject': subject}
    return render(request, 'academics/subject_form.html', context)

@login_required
def subject_delete_view(request, pk):
    subject = get_object_or_404(Subject, pk=pk, teacher=request.user)
    if request.method == 'POST':
        subject_name = subject.name;
        subject.delete()
        messages.success(request, f"ลบวิชา '{subject_name}' และข้อมูลทั้งหมดที่เกี่ยวข้องเรียบร้อยแล้ว")
        return redirect('teachers:dashboard')
    context = {'subject': subject};
    return render(request, 'academics/subject_confirm_delete.html', context)


@login_required
def subject_list_view(request):
    """
    แสดงรายการวิชาทั้งหมดของครู และจัดการการสร้างวิชาใหม่
    """
    teacher = request.user

    # ส่วนจัดการการสร้างวิชาใหม่ (ย้ายมาจาก Dashboard)
    if request.method == 'POST':
        form = SmartClassroomForm(request.POST, request.FILES)
        if form.is_valid():
            try:
                subject = form.save(commit=False)
                subject.teacher = teacher
                subject.save()
                messages.success(request, f"สร้างวิชา '{subject.name} ({subject.subject_code})' เรียบร้อยแล้ว")
            except IntegrityError:
                messages.error(request, f"คุณมีวิชาที่มีรหัส '{form.cleaned_data['subject_code']}' อยู่แล้ว")

            # เมื่อสร้างเสร็จ ให้กลับมาที่หน้ารายการวิชานี้อีกครั้ง
            return redirect('teachers:subject_list')
    else:
        form = SmartClassroomForm()

    # ดึงข้อมูลวิชาทั้งหมดของครู
    subjects = Subject.objects.filter(teacher=teacher).prefetch_related('classrooms').order_by('name')

    context = {
        'subjects': subjects,
        'smart_form': form,
    }
    return render(request, 'teachers/subject_list.html', context)

# ===================================================================
# Views จัดการ Classroom และ Student Detail
# ===================================================================
@login_required
def classroom_detail_view(request, pk):
    classroom = get_object_or_404(Classroom, pk=pk, subject__teacher=request.user)
    assignment_form = AssignmentForm();
    student_form = StudentForm()
    upload_form = UploadFileForm(user=request.user, initial={'classroom': classroom})
    copy_students_form = CopyStudentsForm(teacher=request.user, current_classroom_pk=pk)
    if request.method == 'POST':
        if 'create_assignment' in request.POST:
            form = AssignmentForm(request.POST, request.FILES);
            if form.is_valid():
                assignment = form.save(commit=False);
                assignment.classroom = classroom;
                assignment.save()
                messages.success(request, f"สร้างชิ้นงาน '{assignment.title}' สำเร็จ")
            else:
                assignment_form = form
        elif 'add_new_student' in request.POST:
            form = StudentForm(request.POST)
            if form.is_valid():
                student_id = form.cleaned_data['student_id'];
                full_name = form.cleaned_data['full_name']
                try:
                    with transaction.atomic():
                        student, student_created = Student.objects.get_or_create(student_id=student_id,
                                                                                 defaults={'full_name': full_name})
                        if student_created or not student.user:
                            user, user_created = User.objects.get_or_create(username=student_id)
                            if user_created:
                                name_parts = full_name.split(' ', 1);
                                user.first_name = name_parts[0];
                                user.last_name = name_parts[1] if len(name_parts) > 1 else ''
                                user.set_password('qw123456');
                                user.save()
                            student.user = user;
                            student.save()
                        Enrollment.objects.get_or_create(student=student, classroom=classroom)
                        messages.success(request, f"เพิ่มนักเรียน '{full_name}' และสร้างบัญชีผู้ใช้สำเร็จ")
                except IntegrityError:
                    messages.error(request, f"รหัสนักเรียน '{student_id}' มีอยู่ในระบบแล้ว แต่ชื่ออาจไม่ตรงกัน")
            else:
                student_form = form
        return redirect('teachers:classroom_detail', pk=pk)
    students_in_class = classroom.students.all().order_by('student_id')
    assignments = classroom.assignments.all().order_by('-created_at')
    context = {
        'classroom': classroom, 'students': students_in_class, 'assignments': assignments,
        'assignment_form': assignment_form, 'student_form': student_form,
        'upload_form': upload_form, 'copy_students_form': copy_students_form
    }
    return render(request, 'teachers/classroom_detail.html', context)


@login_required
def student_detail_teacher_view(request, classroom_pk, student_pk):
    enrollment = get_object_or_404(Enrollment.objects.select_related('student', 'classroom', 'classroom__subject'),
                                   student__pk=student_pk, classroom__pk=classroom_pk,
                                   classroom__subject__teacher=request.user)
    if request.method == 'POST':
        if 'update_core_scores' in request.POST:
            form = CoreScoresForm(request.POST, instance=enrollment)
            if form.is_valid(): form.save(); enrollment.update_scores(); messages.success(request,
                                                                                          "บันทึกคะแนนสอบและคำนวณผลใหม่เรียบร้อยแล้ว")
        elif 'add_grade_component' in request.POST:
            form = GradeComponentForm(request.POST)
            if form.is_valid(): component = form.save(
                commit=False); component.enrollment = enrollment; component.save(); messages.success(request,
                                                                                                     f"เพิ่มรายการคะแนน '{component.name}' เรียบร้อยแล้ว")
        elif 'delete_grade_component' in request.POST:
            component_id = request.POST.get('component_id')
            component = get_object_or_404(GradeComponent, id=component_id, enrollment=enrollment)
            messages.success(request, f"ลบรายการคะแนน '{component.name}' เรียบร้อยแล้ว");
            component.delete()
        elif 'add_behavior' in request.POST:
            form = BehaviorForm(request.POST)
            if form.is_valid():
                behavior = form.save(commit=False);
                behavior.enrollment = enrollment;
                behavior.save()
                messages.success(request, "บันทึกพฤติกรรมสำเร็จ")
        return redirect('teachers:student_detail', classroom_pk=classroom_pk, student_pk=student_pk)
    core_scores_form = CoreScoresForm(instance=enrollment);
    component_form = GradeComponentForm();
    behavior_form = BehaviorForm()
    grade_components = enrollment.components.all().order_by('name')
    behaviors = enrollment.behaviors.all().order_by('-date_recorded')
    total_behavior_points = behaviors.aggregate(total=models.Sum('points'))['total'] or 0
    context = {
        'enrollment': enrollment, 'student': enrollment.student, 'classroom': enrollment.classroom,
        'core_scores_form': core_scores_form, 'component_form': component_form, 'behavior_form': behavior_form,
        'grade_components': grade_components, 'behaviors': behaviors, 'total_behavior_points': total_behavior_points
    }
    return render(request, 'teachers/student_detail.html', context)

@login_required
def classroom_update_view(request, pk):
    """ แสดงและประมวลผลฟอร์มสำหรับแก้ไขชื่อห้องเรียน """
    classroom = get_object_or_404(Classroom, pk=pk, subject__teacher=request.user)
    if request.method == 'POST':
        form = ClassroomForm(request.POST)
        if form.is_valid():
            classroom.class_name = form.cleaned_data['class_name']
            classroom.save()
            messages.success(request, f"แก้ไขชื่อห้องเรียนเป็น '{classroom.class_name}' เรียบร้อยแล้ว")
            return redirect('teachers:subject_detail', pk=classroom.subject.pk)
    else:
        form = ClassroomForm(initial={'class_name': classroom.class_name})

    context = {
        'form': form,
        'classroom': classroom
    }
    return render(request, 'teachers/classroom_form.html', context)


@login_required
def classroom_delete_view(request, pk):
    """ แสดงหน้ายืนยันและประมวลผลการลบห้องเรียน """
    classroom = get_object_or_404(Classroom, pk=pk, subject__teacher=request.user)
    subject_pk = classroom.subject.pk # เก็บ pk ของวิชาไว้ก่อนลบ

    if request.method == 'POST':
        classroom_name = classroom.class_name
        classroom.delete()
        messages.success(request, f"ลบห้องเรียน '{classroom_name}' และข้อมูลทั้งหมดที่เกี่ยวข้องเรียบร้อยแล้ว")
        return redirect('teachers:subject_detail', pk=subject_pk)

    context = {
        'classroom': classroom
    }
    return render(request, 'teachers/classroom_confirm_delete.html', context)
# ===================================================================
# Views สำหรับระบบเช็คชื่อ (เวอร์ชันกำหนดเวลาเป็นวินาที)
# ===================================================================
@login_required
def manage_attendance_session(request, classroom_pk):
    classroom = get_object_or_404(Classroom, pk=classroom_pk, subject__teacher=request.user)
    active_session = AttendanceSession.objects.filter(classroom=classroom, end_time__gte=timezone.now()).order_by(
        '-start_time').first()

    if request.method == 'POST':
        if 'close_session' in request.POST and active_session:
            active_session.end_time = timezone.now()
            active_session.save()
            messages.info(request, "ปิดระบบเช็คชื่อเรียบร้อยแล้ว")
            return redirect('teachers:manage_attendance', classroom_pk=classroom.pk)

        duration_seconds_str = request.POST.get('duration_seconds')
        if duration_seconds_str:
            if active_session:
                messages.warning(request, "ไม่สามารถสร้างซ้อนได้ กรุณาปิดคาบเรียนปัจจุบันก่อน")
            else:
                try:
                    seconds = int(duration_seconds_str)
                    if seconds <= 0: raise ValueError("Duration must be a positive number.")
                    now = timezone.now()
                    session = AttendanceSession.objects.create(
                        classroom=classroom, created_by=request.user,
                        start_time=now, end_time=now + timedelta(seconds=seconds)
                    )
                    messages.success(request,
                                     f"เปิดระบบเช็คชื่อเป็นเวลา {seconds} วินาทีสำเร็จ! รหัสคือ: {session.code}")
                except (ValueError, TypeError):
                    messages.error(request, "กรุณากรอกระยะเวลาเป็นตัวเลข (วินาที) ที่ถูกต้อง")
            return redirect('teachers:manage_attendance', classroom_pk=classroom.pk)

    context = {
        'classroom': classroom,
        'active_session': active_session,
    }
    return render(request, 'teachers/manage_attendance.html', context)


@login_required
def get_attendance_records_api(request, session_pk):
    session = get_object_or_404(AttendanceSession, pk=session_pk, created_by=request.user)
    records = AttendanceRecord.objects.filter(session=session).select_related('student').order_by('timestamp')

    # แก้ไขบรรทัดนี้ให้ถูกต้อง
    data = [{'full_name': r.student.full_name, 'student_id': r.student.student_id,
             'timestamp': timezone.localtime(r.timestamp).strftime('%H:%M:%S')} for r in records]

    return JsonResponse({'students': data})

@login_required
def risk_students_view(request):
    # สำหรับอนาคต: หน้านี้จะแสดงรายชื่อนักเรียนกลุ่มเสี่ยง
    return render(request, 'teachers/placeholder_page.html', {'title': 'รายชื่อนักเรียนกลุ่มเสี่ยง'})

@login_required
def document_storage_view(request):
    # สำหรับอนาคต: หน้านี้จะเป็นระบบคลังเอกสาร
    return render(request, 'teachers/placeholder_page.html', {'title': 'คลังเอกสาร'})