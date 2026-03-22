from django.urls import path, include
from rest_framework.routers import DefaultRouter
from . import views

router = DefaultRouter()
# Register specific prefixes before the catch-all '' route
router.register(r'manage', views.AdminJobViewSet, basename='admin-job')
router.register(r'applications', views.JobApplicationViewSet, basename='job-application')
router.register(r'', views.JobViewSet, basename='job')

urlpatterns = [
    path('', include(router.urls)),
]
