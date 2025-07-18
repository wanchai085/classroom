from django.shortcuts import render, redirect
from django.contrib.auth import login
from django.contrib.auth.decorators import login_required
from django.contrib.auth.views import PasswordChangeView
from django.contrib import messages
from django.urls import reverse_lazy
from .forms import CustomUserCreationForm
from .models import Notification
from students.models import Student
from teachers.models import Teacher

@login_required
def home_redirect_view(request):
    if hasattr(request.user, 'student_profile'):
        return redirect('students:dashboard')
    elif hasattr(request.user, 'teacher_profile') or request.user.is_superuser:
        return redirect('teachers:dashboard')
    else:
        # กรณีเป็น user ธรรมดาที่ยังไม่มี role
        return redirect('accounts:login')

def signup_view(request):
    if request.user.is_authenticated:
        return redirect('home')
    if request.method == 'POST':
        form = CustomUserCreationForm(request.POST)
        if form.is_valid():
            user = form.save()
            # สมมติว่าคนที่สมัครจากหน้านี้เป็นครู
            Teacher.objects.create(user=user)
            login(request, user)
            messages.success(request, "สมัครสมาชิกสำหรับครูสำเร็จ! ยินดีต้อนรับ")
            return redirect('home')
    else:
        form = CustomUserCreationForm()
    return render(request, 'accounts/signup.html', {'form': form})

class CustomPasswordChangeView(PasswordChangeView):
    template_name = 'accounts/password_change.html'
    success_url = reverse_lazy('home')
    def form_valid(self, form):
        response = super().form_valid(form)
        try:
            student_profile = self.request.user.student_profile
            if not student_profile.password_changed:
                student_profile.password_changed = True
                student_profile.save(update_fields=['password_changed'])
            messages.success(self.request, "เปลี่ยนรหัสผ่านสำเร็จ!")
        except Student.DoesNotExist:
            messages.success(self.request, "เปลี่ยนรหัสผ่านสำเร็จ!")
        return response

@login_required
def mark_notification_as_read(request):
    notif_id = request.GET.get('notif_id')
    redirect_url = request.GET.get('next', '/')
    if notif_id:
        notification = Notification.objects.filter(id=notif_id, user=request.user).first()
        if notification:
            notification.is_read = True
            notification.save(update_fields=['is_read'])
            if notification.link:
                redirect_url = notification.link
    return redirect(redirect_url)