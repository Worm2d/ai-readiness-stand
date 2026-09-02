"""Data migration: наполняет опрос вопросами и вариантами ответов (раздел 5.1 ТЗ).

ВАЖНО про разметку тегов (исправленная версия):
- Тег (`risk_tags`) ставится ТОЛЬКО на варианты, которые реально сигнализируют
  о конкретном риске в этой категории — как правило, один тег на вариант.
- "Хорошие"/безопасные варианты ответа НЕ тегируются вообще (или тегируются
  очень редко), чтобы не размывать выборку — иначе фильтр по тегам начинает
  возвращать почти весь реестр рисков независимо от ответов.
- score_weight отражает вклад в общий балл "зрелость ИБ в контексте ИИ" (0-100)
  и не обязан совпадать с наличием/отсутствием тега.
"""
from django.db import migrations


def seed_data(apps, schema_editor):
    Question = apps.get_model("survey", "Question")
    AnswerOption = apps.get_model("survey", "AnswerOption")
    RiskCategory = apps.get_model("risks", "RiskCategory")

    cats = {c.name: c for c in RiskCategory.objects.all()}
    PROTECT_AI = cats.get("Защита ИИ")
    PROTECT_FROM_AI = cats.get("Защита от ИИ")
    LEAKS = cats.get("Утечки через публичный ИИ")
    AI_IN_DEFENSE = cats.get("ИИ в защите")

    def add_question(order, qtype, title, subtitle="", required=True, active=True,
                      number_min=None, number_max=None, number_step=None, options=None):
        q = Question.objects.create(
            order=order, question_type=qtype, title=title, subtitle=subtitle,
            is_required=required, is_active=active,
            number_min=number_min, number_max=number_max, number_step=number_step,
        )
        if options:
            for opt_order, (text, tags, weight) in enumerate(options):
                opt = AnswerOption.objects.create(question=q, text=text, order=opt_order, score_weight=weight)
                if tags:
                    opt.risk_tags.set([t for t in tags if t])
        return q

    add_question(
        1, "info_text",
        "Добро пожаловать!",
        "Сейчас мы зададим вам несколько вопросов о том, как ваша организация использует и "
        "защищает искусственный интеллект. Это займёт 3–5 минут. В конце вы получите "
        "персональный отчёт с рисками и рекомендациями.",
    )

    add_question(
        2, "single_choice",
        "Использует ли ваша организация искусственный интеллект (ChatGPT, локальные LLM, ML-модели) в работе?",
        options=[
            ("Да, регулярно", [], 10),
            ("Да, эпизодически", [LEAKS], 5),
            ("Планируем начать", [], 0),
            ("Нет и не планируем", [], -5),
        ],
    )

    add_question(
        3, "multiple_choice",
        "Какие ИИ-инструменты используются?",
        subtitle="Можно выбрать несколько вариантов.",
        required=False,
        options=[
            ("Публичные чат-боты (ChatGPT, Gemini, DeepSeek и т.п.)", [LEAKS], -5),
            ("Локальные (on-premise) языковые модели", [PROTECT_AI], 5),
            ("ML-модели в бизнес-процессах (скоринг, аналитика)", [AI_IN_DEFENSE], 5),
            ("ИИ-модули в СЗИ (антифрод, UEBA)", [AI_IN_DEFENSE], 10),
            ("Не знаю", [LEAKS], -5),
            ("Другое", [], 0),
        ],
    )

    add_question(
        4, "single_choice",
        "Контролируете ли вы, какую информацию сотрудники вводят в публичные ИИ-сервисы?",
        options=[
            ("Да, есть DLP и политики", [], 15),
            ("Есть политика, но без технического контроля", [LEAKS], 5),
            ("Не контролируем", [LEAKS], -15),
            ("Запрещаем использование, но не проверяем", [LEAKS], -5),
        ],
    )

    add_question(
        5, "single_choice",
        "Мог ли сотрудник случайно передать конфиденциальные данные (код, персональные данные, коммерческую тайну) в публичный ИИ-сервис?",
        options=[
            ("Уверены, что нет", [], 10),
            ("Возможно", [LEAKS], -5),
            ("Да, был такой случай", [LEAKS], -15),
            ("Не знаем", [LEAKS], -10),
        ],
    )

    add_question(
        6, "single_choice",
        "Используете ли вы локальные (развёрнутые внутри компании) языковые модели?",
        options=[
            ("Да, для большинства задач", [PROTECT_AI], 10),
            ("Да, для отдельных задач", [PROTECT_AI], 5),
            ("Нет, но планируем", [], 0),
            ("Нет и не планируем", [], 0),
        ],
    )

    add_question(
        7, "single_choice",
        "Проверяли ли вы локальные ИИ-модели на устойчивость к атакам типа prompt injection / jailbreak?",
        options=[
            ("Да", [], 15),
            ("Нет", [PROTECT_AI], -10),
            ("Не знали, что это нужно делать", [PROTECT_AI], -15),
            ("Планируем", [], 0),
        ],
    )

    add_question(
        8, "single_choice",
        "Есть ли в компании политика/регламент по использованию ИИ сотрудниками?",
        options=[
            ("Да, утверждена и соблюдается", [], 15),
            ("Да, но формально", [LEAKS], 0),
            ("Разрабатывается", [], -5),
            ("Нет", [LEAKS], -15),
        ],
    )

    add_question(
        9, "single_choice",
        "Сталкивалась ли ваша компания с фишингом или социальной инженерией, где подозреваете использование ИИ (дипфейки, идеально написанные письма и т.п.)?",
        options=[
            ("Да, неоднократно", [PROTECT_FROM_AI], -15),
            ("Да, один раз", [PROTECT_FROM_AI], -10),
            ("Нет, но допускаем такую возможность", [PROTECT_FROM_AI], 0),
            ("Нет и уверены, что не сталкивались", [], 10),
        ],
    )

    add_question(
        10, "single_choice",
        "Используете ли вы ИИ/ML в средствах защиты информации (SIEM, антифрод, поведенческая аналитика)?",
        options=[
            ("Да, активно применяем", [AI_IN_DEFENSE], 15),
            ("Есть отдельные модули", [AI_IN_DEFENSE], 10),
            ("Нет, но рассматриваем", [], 0),
            ("Нет и не планируем", [AI_IN_DEFENSE], -5),
        ],
    )

    add_question(
        11, "single_choice",
        "Как оцениваете зрелость команды ИБ в вопросах, связанных с ИИ-угрозами?",
        subtitle="Оцените по шкале от 1 (низкая) до 5 (высокая).",
        options=[
            ("1 — очень низкая", [AI_IN_DEFENSE], -15),
            ("2 — низкая", [AI_IN_DEFENSE], -5),
            ("3 — средняя", [], 5),
            ("4 — выше среднего", [], 10),
            ("5 — высокая", [], 15),
        ],
    )

    add_question(
        12, "number_input",
        "Сколько сотрудников в компании имеют доступ к публичным ИИ-сервисам без ограничений?",
        subtitle="Укажите примерное число.",
        required=False, number_min=0, number_max=100000, number_step=1,
    )

    add_question(
        13, "single_choice",
        "Проводите ли обучение сотрудников по безопасному использованию ИИ?",
        options=[
            ("Да, регулярно", [], 15),
            ("Да, разово при найме", [], 5),
            ("Нет, но планируем", [LEAKS], -5),
            ("Нет", [LEAKS, PROTECT_FROM_AI], -15),
        ],
    )

    add_question(
        14, "multiple_choice",
        "Что вас беспокоит больше?",
        required=False,
        options=[
            ("Утечки данных через ИИ", [LEAKS], 0),
            ("Атаки с использованием ИИ", [PROTECT_FROM_AI], 0),
            ("Некорректные решения ИИ", [AI_IN_DEFENSE], 0),
            ("Отсутствие контроля", [PROTECT_AI], 0),
            ("Ничего не беспокоит", [], 5),
        ],
    )

    add_question(
        15, "info_text",
        "Спасибо за ответы!",
        "Формируем ваш персональный отчёт с выявленными рисками и рекомендациями по защите информации в эпоху ИИ...",
    )


def unseed_data(apps, schema_editor):
    Question = apps.get_model("survey", "Question")
    Question.objects.all().delete()


class Migration(migrations.Migration):

    dependencies = [
        ("survey", "0001_initial"),
        ("risks", "0003_seed_data"),
    ]

    operations = [migrations.RunPython(seed_data, unseed_data)]
