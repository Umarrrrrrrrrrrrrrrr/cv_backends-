from django.urls import path
from . import views

urlpatterns = [
    # eSewa
    path('esewa/initiate/', views.esewa_initiate),
    path('esewa/verify/', views.esewa_verify),
    # Khalti
    path('khalti/initiate/', views.khalti_initiate),
    path('khalti/verify/', views.khalti_verify),
]
