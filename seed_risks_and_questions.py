"""
Скрипт наполнения базы данных финальными рисками и вопросами опроса
из файла Reestr_riskov_II_final.xlsx.

Запуск (из корня проекта, с активным виртуальным окружением Django):

    python manage.py shell < seed_risks_and_questions.py

или, если скрипт лежит в корне и настроен DJANGO_SETTINGS_MODULE:

    python seed_risks_and_questions.py

Перед запуском:
  1. Примените миграции: python manage.py migrate
  2. Положите файл Reestr_riskov_II_final.xlsx в корень проекта
     (или укажите путь в переменной EXCEL_PATH ниже).
  3. Установите зависимость: pip install openpyxl

Скрипт идемпотентен: повторный запуск полностью пересоздаёт
реестр рисков и опрос (старые записи удаляются).
"""
import os
import sys

EXCEL_PATH = os.path.join(os.path.dirname(os.path.abspath(__file__)), "Reestr_riskov_II_final.xlsx")

if __name__ == "__main__" and not os.environ.get("DJANGO_SETTINGS_MODULE"):
    sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
    os.environ.setdefault("DJANGO_SETTINGS_MODULE", "config.settings")
    import django
    django.setup()

import openpyxl
from django.utils.text import slugify

from risks.models import Risk, RiskCategory, Recommendation
from survey.models import Question, AnswerOption


SEVERITY_MAP = {
    "Критическая": "critical",
    "Высокая": "high",
    "Средняя": "medium",
    "Низкая": "low",
}

CATEGORY_COLORS = {
    "Утечка через публичный ИИ": "#F4A623",
    "Защита локальных моделей": "#2E86AB",
    "Атаки, усиленные ИИ": "#E30613",
    "Безопасность AI-агентов и MCP": "#8E44AD",
    "ИИ в СЗИ и SOC": "#2FA84F",
    "Общее управление и комплаенс": "#6C757D",
}


def read_risks(wb):
    ws = wb["Реестр рисков"]
    risks = []
    for row in ws.iter_rows(min_row=2, values_only=True):
        rid, category, title, tag, importance, engineer_comment, scenario, consequences, mitigation, sources = row
        if not tag:
            continue
        risks.append({
            "category": category,
            "title": title,
            "tag": tag,
            "severity": SEVERITY_MAP[importance.strip()],
            "scenario": scenario or "",
            "consequences": consequences or "",
            "mitigation": mitigation or "",
            "sources": sources or "",
        })
    return risks


def read_questions(wb):
    ws = wb["Вопросы и ответы"]
    questions = []
    current = None
    seen_option_ids = set()
    for row in ws.iter_rows(min_row=2, values_only=True):
        qid, qtext, aid, atext, tags, parent_note = row
        if qid:
            current = {"qid": qid, "text": qtext, "options": []}
            questions.append(current)
        if aid in seen_option_ids:
            aid = f"{aid}-dup{len(seen_option_ids)}"
        seen_option_ids.add(aid)
        tag_list = [t.strip() for t in tags.split(";")] if tags else []
        current["options"].append({"aid": aid, "text": atext, "tags": tag_list})
    return questions


def compute_weight(tags):
    return 5 if not tags else -2 * len(tags)


def seed_risks(risks):
    Risk.objects.all().delete()
    Recommendation.objects.all().delete()
    RiskCategory.objects.all().delete()

    category_objs = {}
    for name, color in CATEGORY_COLORS.items():
        obj, _ = RiskCategory.objects.get_or_create(
            name=name,
            defaults={"slug": slugify(name, allow_unicode=True), "color": color},
        )
        category_objs[name] = obj

    risks_by_tag = {}
    for order, item in enumerate(risks):
        description = item["scenario"]
        if item["consequences"]:
            description = f"{description}\n\nВозможные последствия: {item['consequences']}"

        public_case_description = f"Источники: {item['sources']}" if item["sources"] else ""

        risk = Risk.objects.create(
            tag=item["tag"],
            title=item["title"],
            description=description,
            severity=item["severity"],
            mitigation=item["mitigation"],
            public_case_description=public_case_description,
            public_case_source_url="",
            public_case_region="",
            order=order,
        )
        category = category_objs.get(item["category"])
        if category:
            risk.categories.set([category])
        risks_by_tag[item["tag"]] = risk

    print(f"Загружено рисков: {len(risks)}")
    return risks_by_tag


PARENT_LINKS = [
    ("Q01", ["Q01-A3", "Q01-A4"], ["Q02", "Q03", "Q04"]),
    ("Q08", ["Q08-A2", "Q08-A3", "Q08-A4"], ["Q09", "Q10", "Q11"]),
]


def seed_survey(questions, risks_by_tag):
    Question.objects.all().delete()

    Question.objects.create(
        order=1, question_type="info_text",
        title="Добро пожаловать!",
        subtitle=(
            "Сейчас мы зададим вам несколько вопросов о том, как ваша организация использует и "
            "защищает искусственный интеллект. Это займёт 3–5 минут. В конце вы получите "
            "персональный отчёт с рисками и рекомендациями."
        ),
        is_required=True, is_active=True,
    )

    question_objs = {}
    option_objs = {}
    q_order = 2
    for q in questions:
        question = Question.objects.create(
            order=q_order,
            question_type="single_choice",
            title=q["text"],
            is_required=True,
            is_active=True,
        )
        question_objs[q["qid"]] = question

        for opt_order, opt in enumerate(q["options"]):
            weight = compute_weight(opt["tags"])
            option = AnswerOption.objects.create(
                question=question, text=opt["text"], order=opt_order, score_weight=weight,
            )
            linked_risks = [risks_by_tag[t] for t in opt["tags"] if t in risks_by_tag]
            option.risk_tags.set(linked_risks)
            option_objs[opt["aid"]] = option
        q_order += 1

    Question.objects.create(
        order=q_order, question_type="info_text",
        title="Спасибо за ответы!",
        subtitle=(
            "Формируем ваш персональный отчёт с выявленными рисками и рекомендациями по защите "
            "информации в эпоху ИИ..."
        ),
        is_required=True, is_active=True,
    )

    for parent_qid, trigger_aids, dependent_qids in PARENT_LINKS:
        if parent_qid not in question_objs:
            continue
        parent_question = question_objs[parent_qid]
        trigger_options = [option_objs[aid] for aid in trigger_aids if aid in option_objs]
        for dep_qid in dependent_qids:
            if dep_qid not in question_objs:
                continue
            dep_question = question_objs[dep_qid]
            dep_question.parent_question = parent_question
            dep_question.save()
            dep_question.show_only_if_parent_answered.set(trigger_options)

    print(f"Загружено вопросов: {len(questions)}")


def main():
    if not os.path.exists(EXCEL_PATH):
        print(f"Файл не найден: {EXCEL_PATH}")
        print("Положите Reestr_riskov_II_final.xlsx в корень проекта или измените EXCEL_PATH.")
        sys.exit(1)

    wb = openpyxl.load_workbook(EXCEL_PATH, data_only=True)
    risks = read_risks(wb)
    questions = read_questions(wb)

    risks_by_tag = seed_risks(risks)
    seed_survey(questions, risks_by_tag)

    print("Готово! База данных наполнена финальными рисками и вопросами.")


main()
