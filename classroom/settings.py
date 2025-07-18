# classroom/settings.py

import os
from pathlib import Path
import dj_database_url
from dotenv import load_dotenv

# Build paths inside the project like this: BASE_DIR / 'subdir'.
BASE_DIR = Path(__file__).resolve().parent.parent

# โหลดค่าจากไฟล์ .env สำหรับการพัฒนาบนเครื่อง (ถ้ามี)
load_dotenv(os.path.join(BASE_DIR, ".env"))


# === การตั้งค่าสำหรับความปลอดภัยและการใช้งานจริง (Production) ===

# ดึงค่า SECRET_KEY จาก Environment Variable เพื่อความปลอดภัย
# ถ้าหาไม่เจอตอนพัฒนา ให้ใช้ค่าชั่วคราวไปก่อน (แต่จะแสดงคำเตือน)
SECRET_KEY = os.environ.get('SECRET_KEY', 'django-insecure-temporary-key-for-development')

# DEBUG จะเป็น True ก็ต่อเมื่อมี DEBUG=True ใน Environment เท่านั้น
# บน Render จะไม่มีตัวแปรนี้ ทำให้ค่าเริ่มต้นเป็น False โดยอัตโนมัติ
DEBUG = os.environ.get('DEBUG', 'False').lower() == 'true'

# ตั้งค่า ALLOWED_HOSTS ให้รองรับ Render และ localhost
ALLOWED_HOSTS = []
RENDER_EXTERNAL_HOSTNAME = os.environ.get('RENDER_EXTERNAL_HOSTNAME')
if RENDER_EXTERNAL_HOSTNAME:
    ALLOWED_HOSTS.append(RENDER_EXTERNAL_HOSTNAME)


# === Application definition ===

INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'whitenoise.runserver_nostatic',  # เพิ่มสำหรับ Whitenoise
    'django.contrib.staticfiles',
    'rest_framework',
    'accounts.apps.AccountsConfig',
    'teachers.apps.TeachersConfig',
    'students.apps.StudentsConfig',
    'academics.apps.AcademicsConfig',
]

MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'whitenoise.middleware.WhiteNoiseMiddleware',  # <<< เพิ่ม Whitenoise ที่นี่
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
    'accounts.middleware.PasswordChangeMiddleware',
]

ROOT_URLCONF = 'classroom.urls'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [BASE_DIR / 'templates'],
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.debug',
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
                'accounts.context_processors.notifications',
            ],
        },
    },
]

WSGI_APPLICATION = 'classroom.wsgi.application'


# === การตั้งค่าฐานข้อมูล (สำคัญที่สุด) ===

DATABASES = {
    'default': dj_database_url.config(
        # ใช้ DATABASE_URL จาก Environment ของ Render
        # ถ้าหาไม่เจอ (ตอนพัฒนาบนเครื่อง) ให้กลับไปใช้ sqlite3 แทน
        default='sqlite:///' + str(BASE_DIR / 'db.sqlite3'),
        conn_max_age=600 # ทำให้การเชื่อมต่อเสถียรขึ้น
    )
}


# === Password validation ===
AUTH_PASSWORD_VALIDATORS = [
    {'NAME': 'django.contrib.auth.password_validation.UserAttributeSimilarityValidator',},
    {'NAME': 'django.contrib.auth.password_validation.MinimumLengthValidator',},
    {'NAME': 'django.contrib.auth.password_validation.CommonPasswordValidator',},
    {'NAME': 'django.contrib.auth.password_validation.NumericPasswordValidator',},
]


# === Internationalization ===
LANGUAGE_CODE = 'en-us'
TIME_ZONE = 'Asia/Bangkok'
USE_I18N = True
USE_TZ = True


# === Static files (CSS, JavaScript, Images) ===
STATIC_URL = 'static/'
STATIC_ROOT = BASE_DIR / 'staticfiles' # ที่สำหรับ collectstatic
STATICFILES_STORAGE = 'whitenoise.storage.CompressedManifestStaticFilesStorage' # ทำให้ Whitenoise ทำงานได้เต็มประสิทธิภาพ

# === Media files (User uploaded files) ===
MEDIA_URL = '/media/'
MEDIA_ROOT = BASE_DIR / 'media'


# === Default primary key field type ===
DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'


# === Login/Logout Redirects ===
LOGIN_REDIRECT_URL = '/'
LOGIN_URL = 'accounts:login'
LOGOUT_REDIRECT_URL = 'accounts:login'