from django.urls import path

from . import views

urlpatterns = [
    path("report/<uuid:session_uuid>/", views.ReportView.as_view(), name="report"),
]
