# ai_classroom/accounts/middleware.py

from django.shortcuts import redirect
from django.urls import reverse
from students.models import Student  # เรายังต้อง import Student เพื่อเช็คโปรไฟล์


class PasswordChangeMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        # ทำงานเฉพาะเมื่อ user ล็อกอินแล้วเท่านั้น
        if not request.user.is_authenticated:
            return self.get_response(request)

        # ถ้าเป็น admin/staff ไม่ต้องบังคับเปลี่ยน
        if request.user.is_staff or request.user.is_superuser:
            return self.get_response(request)

        try:
            # เช็คว่า user มีโปรไฟล์นักเรียนหรือไม่
            student_profile = request.user.student_profile

            # ใช้ namespace ในการ reverse URL
            password_change_url = reverse('accounts:password_change')
            logout_url = reverse('accounts:logout')

            # ถ้ายังไม่ได้เปลี่ยนรหัส และหน้าปัจจุบันไม่ใช่หน้าเปลี่ยนรหัสหรือหน้า logout
            if not student_profile.password_changed and request.path not in [password_change_url, logout_url]:
                # ส่งไปยังหน้าเปลี่ยนรหัสผ่าน
                return redirect(password_change_url)

        except Student.DoesNotExist:
            # ถ้า user ไม่มี student_profile (อาจจะเป็นครูที่ is_staff=False) ก็ไม่ต้องทำอะไร
            pass

        response = self.get_response(request)
        return response