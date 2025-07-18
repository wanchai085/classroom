# ai_classroom/urls.py
from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
from accounts.views import home_redirect_view

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', home_redirect_view, name='home'),
    path('accounts/', include('accounts.urls', namespace='accounts')),
    path('teachers/', include('teachers.urls', namespace='teachers')),
    path('students/', include('students.urls', namespace='students')),
    path('academics/', include('academics.urls', namespace='academics')),
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)