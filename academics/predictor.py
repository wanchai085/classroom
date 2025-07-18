# academics/predictor.py
import joblib
import pandas as pd
import os
from django.conf import settings
from django.db.models import Avg, Sum
from academics.models import BehaviorRecord

# โหลดโมเดล AI ตอนที่ Django เริ่มทำงาน
MODEL_PATH = os.path.join(settings.BASE_DIR, 'ai_models', 'student_risk_model.joblib')
MODEL = None
if os.path.exists(MODEL_PATH):
    try:
        MODEL = joblib.load(MODEL_PATH)
        print("AI risk model loaded successfully.")
    except Exception as e:
        print(f"Error loading AI model: {e}")


def predict_student_risk(student):
    """
    ทำนายความเสี่ยงของนักเรียน 1 คน โดยใช้โมเดลที่โหลดไว้
    """
    if MODEL is None:
        return "⚪️ ไม่พบโมเดล"

    try:
        # 1. สร้าง Feature ให้เหมือนกับตอน Train
        avg_total_score = student.enrollments.aggregate(avg=Avg('total_score'))['avg'] or 0
        total_behavior_points = BehaviorRecord.objects.filter(
            enrollment__student=student
        ).aggregate(total=Sum('points'))['total'] or 0

        # 2. เตรียมข้อมูลสำหรับ Input
        # ชื่อคอลัมน์ต้องตรงกับตอน Train เป๊ะๆ
        input_data = pd.DataFrame({
            'avg_score': [avg_total_score],
            'behavior_points': [total_behavior_points]
        })

        # 3. ทำนายผล
        prediction = MODEL.predict(input_data)

        if prediction[0] == 1:
            return "🔴 เสี่ยงสูง"
        else:
            return "🟢 ปลอดภัย"

    except Exception as e:
        print(f"Error during prediction for student {student.student_id}: {e}")
        return "⚪️ ข้อมูลไม่เพียงพอ"