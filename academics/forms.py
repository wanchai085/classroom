# ai_classroom/academics/forms.py

from django import forms
from .models import Assignment, Submission, GradeComponent, Enrollment, BehaviorRecord

class AssignmentForm(forms.ModelForm):
    class Meta:
        model = Assignment
        fields = ['title', 'description', 'attachment', 'max_score', 'due_date']
        widgets = {
            'title': forms.TextInput(attrs={'class': 'form-control'}),
            'description': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
            'attachment': forms.FileInput(attrs={'class': 'form-control'}),
            'max_score': forms.NumberInput(attrs={'class': 'form-control'}),
            'due_date': forms.DateTimeInput(attrs={'class': 'form-control', 'type': 'datetime-local'}),
        }

class SubmissionForm(forms.ModelForm):
    class Meta:
        model = Submission
        fields = ['attachment']
        widgets = {'attachment': forms.FileInput(attrs={'class': 'form-control', 'required': True})} # ควรบังคับส่งไฟล์

class GradeComponentForm(forms.ModelForm):
    class Meta:
        model = GradeComponent
        fields = ['name', 'score']
        widgets = {
            'name': forms.TextInput(attrs={'class': 'form-control'}),
            'score': forms.NumberInput(attrs={'class': 'form-control'}),
        }

class CoreScoresForm(forms.ModelForm):
    class Meta:
        model = Enrollment
        fields = ['midterm_score', 'final_score']
        labels = {
            'midterm_score': 'คะแนนสอบกลางภาค',
            'final_score': 'คะแนนสอบปลายภาค',
        }
        widgets = {
            'midterm_score': forms.NumberInput(attrs={'class': 'form-control', 'placeholder': 'กรอกคะแนนกลางภาค'}),
            'final_score': forms.NumberInput(attrs={'class': 'form-control', 'placeholder': 'กรอกคะแนนปลายภาค'}),
        }

class BehaviorForm(forms.ModelForm):
    class Meta:
        model = BehaviorRecord
        fields = ['behavior_type', 'points', 'record_text']
        widgets = {
            'behavior_type': forms.Select(attrs={'class': 'form-select'}),
            'points': forms.NumberInput(attrs={'class': 'form-control'}),
            'record_text': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
        }