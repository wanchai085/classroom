# academics/management/commands/train_risk_model.py

import pandas as pd
import joblib
import os
from django.core.management.base import BaseCommand
from django.db.models import Avg, Sum
from sklearn.model_selection import train_test_split
from sklearn.ensemble import RandomForestClassifier
from sklearn.metrics import classification_report
from django.conf import settings

# Import models ที่จำเป็น
from students.models import Student
from academics.models import Enrollment, BehaviorRecord


class Command(BaseCommand):
    help = 'Train a model to predict student risk based on academic and behavioral data'

    def handle(self, *args, **kwargs):
        self.stdout.write(self.style.HTTP_INFO("===== Starting Student Risk Model Training ====="))

        # 1. ดึงข้อมูลนักเรียนทั้งหมดที่มีการลงทะเบียนเรียน
        students = Student.objects.filter(enrollments__isnull=False).distinct()

        if students.count() < 10:  # ควรมีข้อมูลจำนวนหนึ่งเพื่อให้โมเดลเรียนรู้ได้
            self.stdout.write(self.style.ERROR(
                "Not enough student data to train a meaningful model. At least 10 students with enrollments are recommended."))
            return

        # 2. สร้าง Feature สำหรับนักเรียนแต่ละคน
        student_data = []
        self.stdout.write(self.style.HTTP_INFO("--- Feature Engineering ---"))
        for student in students:
            # Feature 1: คะแนนเฉลี่ยรวม
            avg_total_score = student.enrollments.aggregate(avg=Avg('total_score'))['avg'] or 0

            # Feature 2: คะแนนพฤติกรรมรวม (อาจจะติดลบได้)
            total_behavior_points = BehaviorRecord.objects.filter(
                enrollment__student=student
            ).aggregate(total=Sum('points'))['total'] or 0

            # Feature 3: จำนวนครั้งที่ขาดเรียน (ถ้ามีระบบเช็คชื่อ)
            # absent_count = AttendanceRecord.objects.filter(student=student, status='ABSENT').count()

            # 3. กำหนด Label (เป้าหมายที่จะทำนาย) - นี่คือกฎที่เราตั้งขึ้นเอง
            # "เสี่ยง" (1) คือ นักเรียนที่คะแนนเฉลี่ยน้อยกว่า 60 หรือ มีคะแนนพฤติกรรมติดลบ
            is_at_risk = 1 if (avg_total_score < 60 or total_behavior_points < 0) else 0

            student_data.append({
                'student_id': student.student_id,
                'avg_score': avg_total_score,
                'behavior_points': total_behavior_points,
                'is_at_risk': is_at_risk  # <--- นี่คือคำตอบที่โมเดลต้องเรียนรู้
            })

        df = pd.DataFrame(student_data)
        self.stdout.write(self.style.SUCCESS(f"Prepared data for {len(df)} students."))

        # ตรวจสอบว่ามีทั้งกลุ่มเสี่ยงและไม่เสี่ยง
        if len(df['is_at_risk'].unique()) < 2:
            self.stdout.write(
                self.style.ERROR("Training data must contain both at-risk (1) and not-at-risk (0) samples."))
            return

        # 4. เตรียมข้อมูลสำหรับ Train/Test
        features = ['avg_score', 'behavior_points']
        X = df[features]
        y = df['is_at_risk']

        X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.3, random_state=42, stratify=y)

        # 5. ฝึกสอนโมเดล
        self.stdout.write(self.style.HTTP_INFO("--- Training RandomForestClassifier Model ---"))
        model = RandomForestClassifier(n_estimators=100, random_state=42, class_weight='balanced')
        model.fit(X_train, y_train)

        # 6. ประเมินผลและบันทึกโมเดล
        self.stdout.write(self.style.HTTP_INFO("--- Model Evaluation ---"))
        y_pred = model.predict(X_test)
        self.stdout.write(classification_report(y_test, y_pred, zero_division=0))

        model_dir = os.path.join(settings.BASE_DIR, 'ai_models')
        os.makedirs(model_dir, exist_ok=True)
        model_path = os.path.join(model_dir, 'student_risk_model.joblib')
        joblib.dump(model, model_path)

        self.stdout.write(self.style.SUCCESS(f"Model successfully trained and saved to '{model_path}'"))