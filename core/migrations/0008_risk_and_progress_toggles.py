from django.db import migrations, models


def update_default_email_template(apps, schema_editor):
    """Если у существующей записи SiteSettings текст письма совпадает со старым
    дефолтом (с жёсткой запятой перед {visitor_name}), обновляем его на новый формат,
    где запятая — часть подстановки, а не шаблона. Это чинит артефакт "Здравствуйте, !"
    при отсутствии имени посетителя. Если текст был изменён администратором вручную — не трогаем его."""
    SiteSettings = apps.get_model("core", "SiteSettings")
    old_default = (
        "Здравствуйте, {visitor_name}!\n\n"
        "Ваш персональный отчёт по итогам опроса готов, ознакомиться с ним можно по ссылке:\n"
        "{report_url}\n\n"
        "Если вас интересует защита ИИ-контура или другие услуги по информационной безопасности, "
        "напишите нам на {company_email} — обсудим, как можем помочь именно вашей организации.\n\n"
        "Наш сайт: {company_website}"
    )
    new_default = (
        "Здравствуйте{visitor_name}!\n\n"
        "Ваш персональный отчёт по итогам опроса готов, ознакомиться с ним можно по ссылке:\n"
        "{report_url}\n\n"
        "Если вас интересует защита ИИ-контура или другие услуги по информационной безопасности, "
        "напишите нам на {company_email} — обсудим, как можем помочь именно вашей организации.\n\n"
        "Наш сайт: {company_website}"
    )
    SiteSettings.objects.filter(email_body_template=old_default).update(email_body_template=new_default)


def noop_reverse(apps, schema_editor):
    pass


class Migration(migrations.Migration):

    dependencies = [
        ("core", "0007_sitesettings_show_score_number"),
    ]

    operations = [
        migrations.AddField(
            model_name="sitesettings",
            name="show_risk_categories",
            field=models.BooleanField(
                default=True,
                help_text=(
                    "Если выключено — у каждого выявленного риска в отчёте не показываются цветные бейджи "
                    "категорий (например, «Утечка через публичный ИИ», «Защита локальных моделей»). "
                    "Бейдж уровня критичности (низкий/средний/высокий/критический) показывается в любом случае."
                ),
                verbose_name="Показывать цветные бейджи категорий риска",
            ),
        ),
        migrations.AddField(
            model_name="sitesettings",
            name="show_risk_case",
            field=models.BooleanField(
                default=True,
                help_text=(
                    "Если выключено — у выявленных рисков в отчёте не показывается блок с описанием публичного "
                    "инцидента/статистики и ссылкой на источник. Название, описание и уровень критичности риска "
                    "остаются в любом случае."
                ),
                verbose_name="Показывать источники (кейсы/статистику) у рисков",
            ),
        ),
        migrations.AddField(
            model_name="sitesettings",
            name="show_question_progress_bar",
            field=models.BooleanField(
                default=True,
                help_text=(
                    "Если выключено — во время прохождения опроса не показывается визуальная полоса прогресса. "
                    "Управляется независимо от счётчика «Вопрос X из N» выше — можно оставить один из двух элементов."
                ),
                verbose_name="Показывать прогресс-бар в опросе",
            ),
        ),
        migrations.AlterField(
            model_name="sitesettings",
            name="email_body_template",
            field=models.TextField(
                blank=True,
                default=(
                    "Здравствуйте{visitor_name}!\n\n"
                    "Ваш персональный отчёт по итогам опроса готов, ознакомиться с ним можно по ссылке:\n"
                    "{report_url}\n\n"
                    "Если вас интересует защита ИИ-контура или другие услуги по информационной безопасности, "
                    "напишите нам на {company_email} — обсудим, как можем помочь именно вашей организации.\n\n"
                    "Наш сайт: {company_website}"
                ),
                help_text=(
                    "Текст письма, которое отправляется на email посетителя после заполнения формы контактов. "
                    "Доступные плейсхолдеры (подставляются автоматически): {visitor_name} — если имя посетителя "
                    "указано, подставится «, Имя» (с затепятой и пробелом перед именем), иначе — пустая строка, поэтому "
                    "плейсхолдер нужно писать сразу после слова «здравствуйте» без своей запятой, например "
                    "«здравствуйте{visitor_name}!» даёт «здравствуйте, Иван!» или «здравствуйте!», если имя не указано; "
                    "{report_url} — ссылка на персональный отчёт; {company_name} — название компании; "
                    "{company_email} — email компании; {company_website} — сайт компании. Если письмо не удалось "
                    "отправить (не настроен SMTP или ошибка соединения), это не блокирует показ отчёта посетителю."
                ),
                verbose_name="Текст письма с отчётом",
            ),
        ),
        migrations.RunPython(update_default_email_template, noop_reverse),
    ]
