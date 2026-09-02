"""Views приложения risks: Экран 4 (постоянная страница отчёта) и PDF."""
from django.http import HttpResponse
from django.shortcuts import get_object_or_404, render
from django.urls import reverse
from django.views import View

from survey.models import SurveySession
from survey.qr import make_qr_data_uri

from .pdf import render_report_pdf
from .scoring_view_helpers import build_report_context


class ReportView(View):
    template_name = "report/report.html"

    def get(self, request, session_uuid):
        session = get_object_or_404(SurveySession, uuid=session_uuid, is_completed=True)
        context = build_report_context(session)

        website_url = context["site_settings"].company_website
        mailto_url = f"mailto:{context['site_settings'].company_email}"

        context["website_qr"] = make_qr_data_uri(website_url)
        context["mailto_qr"] = make_qr_data_uri(mailto_url)
        context["pdf_url"] = reverse("report_pdf", args=[session.uuid])
        return render(request, self.template_name, context)


class ReportPdfView(View):
    def get(self, request, session_uuid):
        session = get_object_or_404(SurveySession, uuid=session_uuid, is_completed=True)
        context = build_report_context(session)

        pdf_bytes = render_report_pdf(context)
        response = HttpResponse(pdf_bytes, content_type="application/pdf")
        filename = f"otchet-gotovnost-k-ii-{session.uuid}.pdf"
        response["Content-Disposition"] = f'inline; filename="{filename}"'
        return response
