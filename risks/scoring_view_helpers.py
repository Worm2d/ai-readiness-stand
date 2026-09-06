"""Общий helper для сборки контекста отчёта (Экран 3, Экран 4, PDF)."""
from core.models import SiteSettings
from services.models import Service

from .models import Recommendation
from survey.scoring import calculate_score, get_score_interpretation, select_relevant_risks


def build_report_context(session):
    site_settings = SiteSettings.load()
    score = session.score if session.score is not None else calculate_score(session)
    interpretation = get_score_interpretation(score)
    risks = select_relevant_risks(session)

    relevant_category_ids = set()
    for risk in risks:
        relevant_category_ids.update(risk.categories.values_list("id", flat=True))

    services_qs = Service.objects.filter(is_active=True).prefetch_related("category")
    services = []
    if relevant_category_ids:
        services = list(
            services_qs.filter(category__id__in=relevant_category_ids).distinct().order_by("order")
        )

    recommendations = Recommendation.objects.filter(is_active=True).order_by("order")

    return {
        "site_settings": site_settings,
        "result_title": site_settings.result_title,
        "primary_color": site_settings.primary_color,
        "session": session,
        "score": score,
        "interpretation": interpretation,
        "risks": risks,
        "recommendations": recommendations,
        "services": services,
    }
