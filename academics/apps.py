# ai_classroom/academics/apps.py

from django.apps import AppConfig

class AcademicsConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'academics'

    def ready(self):
        # Import signals ที่นี่เพื่อให้ Django รู้จัก
        import academics.signals

