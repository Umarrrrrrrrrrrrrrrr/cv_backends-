from django.urls import path
from . import views

urlpatterns = [
    path('config/', views.get_publishable_key),
    path('create-checkout-session/', views.create_checkout_session),
    path('create-payment-intent/', views.create_payment_intent),
    path('webhook/', views.stripe_webhook),
]
