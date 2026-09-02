"""Data migration: наполняет базу услугами компании ICL Системные технологии."""
from django.db import migrations

SERVICES = [
    ("Комплексный аудит информационной безопасности",
     "Оценка текущего состояния защищённости инфраструктуры, включая риски, связанные с использованием ИИ.",
     "https://icl-st.ru/", ["Утечки через публичный ИИ", "Защита ИИ", "Защита от ИИ", "ИИ в защите"]),
    ("Приведение к соответствию требований регуляторов (ФЗ-152, ФСТЭК)",
     "Помощь в приведении процессов обработки данных, в том числе с использованием ИИ-сервисов, в соответствие требованиям российского законодательства.",
     "https://icl-st.ru/", ["Утечки через публичный ИИ"]),
    ("Проектирование и внедрение решений СЗИ",
     "Разработка и внедрение комплексных систем защиты информации с учётом специфики ИИ-угроз.",
     "https://icl-st.ru/", ["Защита от ИИ", "Защита ИИ"]),
    ("Центр мониторинга и реагирования (SOC)",
     "Круглосуточный мониторинг инфраструктуры, включая детектирование атак с использованием ИИ и аномалий в работе ИИ-модулей.",
     "https://icl-st.ru/", ["ИИ в защите", "Защита от ИИ"]),
    ("Защита технологических систем (АСУ ТП)",
     "Специализированная защита промышленных систем управления от современных угроз, включая атаки с применением ИИ.",
     "https://icl-st.ru/", ["Защита от ИИ"]),
    ("Консалтинг по информационной безопасности",
     "Экспертная поддержка при разработке политик безопасности, включая регламенты использования ИИ сотрудниками.",
     "https://icl-st.ru/", ["Утечки через публичный ИИ", "Защита ИИ"]),
    ("Мультивендорная поддержка продуктов и систем (EDR, SIEM, антифрод)",
     "Поддержка и развитие систем защиты ведущих вендоров, включая решения с ИИ/ML-модулями (Kaspersky KATA/KEDR/MLAD и др.).",
     "https://icl-st.ru/", ["ИИ в защите"]),
]


def seed_data(apps, schema_editor):
    Service = apps.get_model("services", "Service")
    RiskCategory = apps.get_model("risks", "RiskCategory")

    for order, (title, short_desc, url, cat_names) in enumerate(SERVICES):
        service, _ = Service.objects.get_or_create(
            title=title,
            defaults={"short_description": short_desc, "url": url, "order": order},
        )
        categories = RiskCategory.objects.filter(name__in=cat_names)
        service.category.set(categories)


def unseed_data(apps, schema_editor):
    Service = apps.get_model("services", "Service")
    Service.objects.all().delete()


class Migration(migrations.Migration):

    dependencies = [
        ("services", "0001_initial"),
        ("risks", "0003_seed_data"),
    ]

    operations = [migrations.RunPython(seed_data, unseed_data)]
