# ai_classroom/students/forms.py

from django import forms

class AttendanceForm(forms.Form):
    code = forms.CharField(
        label="รหัสเช็คชื่อ 6 หลัก",
        max_length=10,
        widget=forms.TextInput(attrs={
            'class': 'form-control form-control-lg text-center',
            'placeholder': 'XXXXXX',
            'style': 'letter-spacing: 0.5em; text-transform: uppercase;',
            'autocapitalize': 'characters',
            'autocomplete': 'off'
        })
    )