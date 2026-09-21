"""Views приложения risks: Экран 4 (постоянная страница отчёта)."""
from django.shortcuts import get_object_or_404, render
from django.views import View

from survey.models import SurveySession
from survey.qr import make_qr_data_uri

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
        return render(request, self.template_name, context)
