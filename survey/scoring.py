"""Логика скоринга и подбора релевантных рисков для отчёта (раздел 4 ТЗ)."""
from risks.models import Risk, ScoreInterpretation

MIN_RISKS_IN_REPORT = 5


def collect_selected_tags(session):
    tag_ids = set()
    for answer in session.answers.select_related("question").prefetch_related("selected_options__risk_tags"):
        for option in answer.selected_options.all():
            tag_ids.update(option.risk_tags.values_list("id", flat=True))
    return tag_ids


def calculate_score(session):
    from survey.models import Question

    total_weight = 0
    for answer in session.answers.prefetch_related("selected_options"):
        for option in answer.selected_options.all():
            total_weight += option.score_weight

    min_possible, max_possible = 0, 0
    for question in Question.objects.filter(is_active=True, question_type__in=["single_choice", "multiple_choice"]):
        weights = list(question.options.values_list("score_weight", flat=True))
        if not weights:
            continue
        if question.question_type == "single_choice":
            min_possible += min(weights)
            max_possible += max(weights)
        else:
            positive = [w for w in weights if w > 0]
            negative = [w for w in weights if w < 0]
            max_possible += sum(positive)
            min_possible += sum(negative)

    if max_possible == min_possible:
        return 50

    normalized = (total_weight - min_possible) / (max_possible - min_possible) * 100
    return max(0, min(100, round(normalized)))


def get_score_interpretation(score):
    return ScoreInterpretation.for_score(score)


def select_relevant_risks(session):
    tag_ids = collect_selected_tags(session)
    risks_qs = Risk.objects.filter(is_active=True).prefetch_related("categories", "related_service")

    if tag_ids:
        relevant = list(risks_qs.filter(categories__id__in=tag_ids).distinct().order_by("order", "-id"))
    else:
        relevant = []

    if len(relevant) < MIN_RISKS_IN_REPORT:
        severity_order = {"critical": 0, "high": 1, "medium": 2, "low": 3}
        fallback = sorted(
            risks_qs.exclude(id__in=[r.id for r in relevant]),
            key=lambda r: (severity_order.get(r.severity, 4), r.order),
        )
        needed = MIN_RISKS_IN_REPORT - len(relevant)
        relevant.extend(fallback[:needed])

    return relevant
