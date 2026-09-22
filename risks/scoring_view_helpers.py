"""Общий helper для сборки контекста отчёта (Экран 3, Экран 4, PDF)."""
from core.models import SiteSettings
from services.models import Service

from survey.scoring import calculate_score, get_score_interpretation, select_relevant_risks


def _collect_mitigation_recommendations(risks):
    """Собирает рекомендации по митигации из risk.mitigation для переданных рисков,
    исключая дубли (одна и та же рекомендация может закрывать несколько рисков —
    в отчёте она должна быть показана один раз) и сохраняя порядок первого появления."""
    seen = set()
    recommendations = []
    for risk in risks:
        text = (risk.mitigation or "").strip()
        if not text or text in seen:
            continue
        seen.add(text)
        recommendations.append({"risk_title": risk.title, "text": text})
    return recommendations


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

    recommendations = _collect_mitigation_recommendations(risks)

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
