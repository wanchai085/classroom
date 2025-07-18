from django.db import models
from django.contrib.auth.models import User

class UserProfile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='profile')
    ROLE_CHOICES = (('student', 'นักเรียน'), ('teacher', 'คุณครู'))
    role = models.CharField(max_length=10, choices=ROLE_CHOICES, verbose_name="บทบาท")
    def __str__(self): return f'{self.user.username} - {self.get_role_display()}'

class Notification(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='notifications')
    message = models.TextField()
    is_read = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    link = models.CharField(max_length=255, blank=True, null=True)
    class Meta: ordering = ['-created_at']
    def __str__(self): return f"Notification for {self.user.username}"