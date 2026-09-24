"""Общий helper для сборки контекста отчёта (Экран 3, Экран 4, PDF)."""
from core.models import SiteSettings
from services.models import Service

from survey.scoring import calculate_score, get_score_interpretation, select_relevant_risks, collect_triggered_risk_ids


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

    has_triggered_risks = bool(collect_triggered_risk_ids(session))
    risks_heading = (
        "Выявленные риски"
        if has_triggered_risks
        else "Риски не выявлены, но стоит помнить о теневом использовании ИИ:"
    )

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
        "risks_heading": risks_heading,
        "recommendations": recommendations,
        "services": services,
    }
