from django.urls import path

from . import views

urlpatterns = [
    path("", views.LandingView.as_view(), name="landing"),
]
