from django.urls import path

from . import views

urlpatterns = [
    path("report/<uuid:session_uuid>/", views.ReportView.as_view(), name="report"),
    path("report/<uuid:session_uuid>/pdf/", views.ReportPdfView.as_view(), name="report_pdf"),
]
