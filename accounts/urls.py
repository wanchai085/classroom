from django.urls import path
from django.contrib.auth import views as auth_views
from . import views

app_name = 'accounts'

urlpatterns = [
    path('login/', auth_views.LoginView.as_view(template_name='accounts/login.html'), name='login'),
    path('logout/', auth_views.LogoutView.as_view(), name='logout'),
    path('signup/', views.signup_view, name='signup'),
    path('password_change/', views.CustomPasswordChangeView.as_view(), name='password_change'),
    path('notifications/mark-as-read/', views.mark_notification_as_read, name='mark_notification_as_read'),
]