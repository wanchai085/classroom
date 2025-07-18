# ai_classroom/accounts/context_processors.py

from .models import Notification  # .models หมายถึง models.py ในแอป accounts เอง

def notifications(request):
    """
    Context processor เพื่อดึงข้อมูลการแจ้งเตือนที่ยังไม่ได้อ่าน
    สำหรับ user ที่ล็อกอินอยู่
    """
    if request.user.is_authenticated:
        # ดึงเฉพาะ 5-10 อันล่าสุดเพื่อประสิทธิภาพ
        unread_notifications = Notification.objects.filter(user=request.user, is_read=False)[:10]
        return {
            'notifications': unread_notifications,
            'notification_count': unread_notifications.count()
        }
    return {} # คืนค่า dict ว่างเปล่าสำหรับ user ที่ไม่ได้ล็อกอิน