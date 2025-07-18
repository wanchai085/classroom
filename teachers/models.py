from django.db import models
from django.contrib.auth.models import User

class Teacher(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='teacher_profile')
    # สามารถเพิ่ม field อื่นๆ ได้ที่นี่ เช่น department, phone_number
    def __str__(self):
        return self.user.get_full_name() or self.user.username