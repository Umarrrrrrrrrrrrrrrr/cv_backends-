"""
URL configuration for backend project.
"""
from django.contrib import admin
from django.urls import path, include
from authentication import views

urlpatterns = [
    path('admin/', admin.site.urls),
    path('api/auth/', include('authentication.urls')),
    path('api/payments/', include('payments.urls')),
    path('api/jobs/', include('jobs.urls')),
    path('api/cv/', include('cv.urls')),
    # Additional routes to match frontend expectations
    path('api/register/', views.register, name='register-alt'),
    path('api/login/', views.login, name='login-alt'),
    path('api/suggest-password/', views.suggest_password, name='suggest-password-alt'),
    path('api/google-auth/', views.google_auth, name='google-auth-alt'),
    path('api/', include('rest_framework.urls')),
]
