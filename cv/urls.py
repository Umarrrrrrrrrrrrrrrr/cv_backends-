from django.urls import path
from . import views

urlpatterns = [
    path("grade/", views.CVGradeView.as_view()),
    path("grade-only/", views.CVGradeOnlyView.as_view()),
    path("enhance/", views.CVEnhanceView.as_view()),
]
