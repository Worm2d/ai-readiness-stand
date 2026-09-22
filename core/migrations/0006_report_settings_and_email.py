from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("core", "0005_sitesettings_qr_hint_text"),
    ]

    operations = [
        migrations.AddField(
            model_name="sitesettings",
            name="show_score_block",
            field=models.BooleanField(
                default=True,
                help_text=(
                    "Если выключено — на странице отчёта не показывается балл, прогресс-бар и текстовая "
                    "интерпретация уровня. Заголовок «Отчёт» и подпись под ним остаются в любом случае."
                ),
                verbose_name="Показывать блок с баллом и уровнем готовности",
            ),
        ),
        migrations.AddField(
            model_name="sitesettings",
            name="show_question_counter",
            field=models.BooleanField(
                default=True,
                help_text="Если выключено — во время прохождения опроса номер текущего вопроса и их общее количество не показываются.",
                verbose_name="Показывать счётчик «Vопрос X из N» в опросе",
            ),
        ),
        migrations.AddField(
            model_name="sitesettings",
            name="always_recommendation_title",
            field=models.CharField(
                blank=True,
                default="Обратитесь к экспертам",
                help_text="Заголовок отдельного блока рекомендации, который показывается в каждом отчёте вне зависимости от ответов.",
                max_length=255,
                verbose_name="Заголовок обязательной рекомендации",
            ),
        ),
        migrations.AddField(
            model_name="sitesettings",
            name="always_recommendation_text",
            field=models.TextField(
                blank=True,
                default=(
                    "Наши эксперты помогут провести аудит ИИ-контура и выстроить защиту от актуальных угроз. "
                    "Свяжитесь с нами, чтобы обсудить, какие меры нужны именно вашей организации."
                ),
                help_text=(
                    "Если заполнено (и заголовок, и текст) — блок с призывом обратиться в компанию показывается "
                    "в каждом отчёте на корпоративном фоне, независимо от ответов на опрос. Если оставить пустым — "
                    "блок не показывается. Контакты берутся из полей «E-mail компании» и «Сайт компании» ниже."
                ),
                verbose_name="Текст обязательной рекомендации",
            ),
        ),
        migrations.AddField(
            model_name="sitesettings",
            name="always_recommendation_email_label",
            field=models.CharField(
                blank=True,
                default="Напишите нам:",
                max_length=100,
                verbose_name="Подпись перед email в блоке рекомендации",
            ),
        ),
        migrations.AddField(
            model_name="sitesettings",
            name="always_recommendation_website_label",
            field=models.CharField(
                blank=True,
                default="Наш сайт:",
                max_length=100,
                verbose_name="Подпись перед сайтом в блоке рекомендации",
            ),
        ),
        migrations.AddField(
            model_name="sitesettings",
            name="email_subject",
            field=models.CharField(
                blank=True,
                default="Ваш отчёт по готовности к ИИ-угрозам готов",
                max_length=255,
                verbose_name="Тема письма с отчётом",
            ),
        ),
        migrations.AddField(
            model_name="sitesettings",
            name="email_body_template",
            field=models.TextField(
                blank=True,
                default=(
                    "Здравствуйте, {visitor_name}!\n\n"
                    "Ваш персональный отчёт по итогам опроса готов, ознакомиться с ним можно по ссылке:\n"
                    "{report_url}\n\n"
                    "Если вас интересует защита ИИ-контура или другие услуги по информационной безопасности, "
                    "напишите нам на {company_email} — обсудим, как можем помочь именно вашей организации.\n\n"
                    "Наш сайт: {company_website}"
                ),
                help_text=(
                    "Текст письма, которое отправляется на email посетителя после заполнения формы контактов. "
                    "Доступные плейсхолдеры (подставляются автоматически): {visitor_name} — имя посетителя или "
                    "«Уважаемый клиент», если имя не указано; {report_url} — ссылка на персональный отчёт; "
                    "{company_name} — название компании; {company_email} — email компании; {company_website} — "
                    "сайт компании. Если письмо не удалось отправить (не настроен SMTP или ошибка соединения), "
                    "это не блокирует показ отчёта посетителю."
                ),
                verbose_name="Текст письма с отчётом",
            ),
        ),
    ]
