from django import forms
from academics.models import Subject, Classroom
from students.models import Student
from academics.models import AttendanceSession


class SmartClassroomForm(forms.ModelForm):
    # เปลี่ยนให้เป็น ModelForm เพื่อความง่าย
    class Meta:
        model = Subject
        fields = ['name', 'subject_code', 'education_level', 'image']
        labels = {
            'name': 'ชื่อวิชา',
            'subject_code': 'รหัสวิชา (บังคับ)',
            'education_level': 'ระดับชั้น',
            'image': 'รูปภาพประจำวิชา (ไม่บังคับ)',
        }
        widgets = {
            'name': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'เช่น ภาษาไทยพื้นฐาน'}),
            'subject_code': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'เช่น ท21101'}),
            'education_level': forms.Select(attrs={'class': 'form-select'}),
            'image': forms.FileInput(attrs={'class': 'form-control'}),
        }


class SubjectUpdateForm(forms.ModelForm):
    class Meta:
        model = Subject

        # 1. เพิ่ม 'subject_code' และ 'education_level' เข้าไปในรายการ fields
        fields = ['name', 'subject_code', 'education_level', 'image']

        # 2. เพิ่ม labels สำหรับ field ใหม่
        labels = {
            'name': 'ชื่อวิชา',
            'subject_code': 'รหัสวิชา',
            'education_level': 'ระดับชั้น',
            'image': 'เปลี่ยนรูปภาพประจำวิชา'
        }

        # 3. เพิ่ม widgets สำหรับ field ใหม่ เพื่อให้มี class ของ Bootstrap
        widgets = {
            'name': forms.TextInput(attrs={'class': 'form-control'}),
            'subject_code': forms.TextInput(attrs={'class': 'form-control'}),
            'education_level': forms.Select(attrs={'class': 'form-select'}),
            'image': forms.FileInput(attrs={'class': 'form-control'})
        }
class StudentForm(forms.ModelForm):
    class Meta:
        model = Student
        fields = ['student_id', 'full_name']
        labels = {'student_id': 'รหัสนักเรียน', 'full_name': 'ชื่อ-นามสกุล'}
        widgets = {'student_id': forms.TextInput(attrs={'class': 'form-control'}), 'full_name': forms.TextInput(attrs={'class': 'form-control'})}

class UploadFileForm(forms.Form):
    classroom = forms.ModelChoiceField(queryset=Classroom.objects.none(), label="เลือกห้องเรียนที่จะนำเข้า", widget=forms.Select(attrs={'class': 'form-select'}))
    file = forms.FileField(label="เลือกไฟล์", widget=forms.FileInput(attrs={'class': 'form-control'}))
    def __init__(self, user, *args, **kwargs):
        super().__init__(*args, **kwargs)
        if user and hasattr(user, 'is_authenticated') and user.is_authenticated:
            self.fields['classroom'].queryset = Classroom.objects.filter(subject__teacher=user)

class CopyStudentsForm(forms.Form):
    from_classroom = forms.ModelChoiceField(queryset=Classroom.objects.none(), label="คัดลอกจากห้องเรียน", empty_label="--- เลือกห้องเรียนต้นทาง ---", widget=forms.Select(attrs={'class': 'form-select'}))
    def __init__(self, teacher, current_classroom_pk, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['from_classroom'].queryset = Classroom.objects.filter(subject__teacher=teacher).exclude(pk=current_classroom_pk).select_related('subject').order_by('subject__name', 'class_name')

class AttendanceSessionForm(forms.ModelForm):
    class Meta:
        model = AttendanceSession
        fields = ['start_time', 'end_time']
        widgets = {
            'start_time': forms.DateTimeInput(attrs={'class': 'form-control', 'type': 'datetime-local'}, format='%Y-%m-%dT%H:%M'),
            'end_time': forms.DateTimeInput(attrs={'class': 'form-control', 'type': 'datetime-local'}, format='%Y-%m-%dT%H:%M'),
        }
        labels = {'start_time': 'เวลาเปิดให้เช็คชื่อ', 'end_time': 'เวลาปิดการเช็คชื่อ'}

    def clean(self):
        cleaned_data = super().clean()
        start = cleaned_data.get("start_time")
        end = cleaned_data.get("end_time")
        if start and end and end <= start:
            raise forms.ValidationError("เวลาสิ้นสุดต้องอยู่หลังเวลาเริ่มต้น")
        return cleaned_data

class ClassroomForm(forms.Form):
    class_name = forms.CharField(
        label="ชื่อห้องเรียนใหม่",
        max_length=100,
        # ▼▼▼ แก้ไข placeholder ที่นี่เพื่อให้คำแนะนำกับผู้ใช้ ▼▼▼
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'เช่น 4/1 (ไม่ต้องใส่ ป. หรือ ม.)'
        })
    )
