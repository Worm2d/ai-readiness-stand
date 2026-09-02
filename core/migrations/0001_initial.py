from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True
    dependencies = []

    operations = [
        migrations.CreateModel(
            name="SiteSettings",
            fields=[
                ("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
                ("collect_personal_data", models.BooleanField(default=True, verbose_name="Собирать контакты посетителя")),
                ("landing_title", models.CharField(default="А ты готов к эпохе Искусственного Интеллекта?", max_length=255, verbose_name="Заголовок стартовой страницы")),
                ("landing_subtitle", models.TextField(default="Речь идёт о защите информации в эпоху ИИ: защита локальных языковых моделей внутри организаций, защита от утечек данных через публичные ИИ-сервисы, защита от атак, сгенерированных или усиленных искусственным интеллектом, а также применение ИИ в самих средствах защиты информации.", verbose_name="Пояснительный текст на стартовой странице")),
                ("button_text", models.CharField(default="Нет", max_length=50, verbose_name="Текст на кнопках старта опроса")),
                ("result_title", models.CharField(default="Вы не готовы, но мы можем Вам помочь", max_length=255, verbose_name="Заголовок страницы результата")),
                ("company_name", models.CharField(default="ICL Системные технологии", max_length=255, verbose_name="Название компании")),
                ("company_website", models.URLField(default="https://icl-st.ru/", verbose_name="Сайт компании")),
                ("company_email", models.EmailField(default="office@icl-st.ru", max_length=254, verbose_name="E-mail компании")),
                ("primary_color", models.CharField(default="#E30613", max_length=7, verbose_name="Основной корпоративный цвет (HEX)")),
                ("logo", models.ImageField(blank=True, null=True, upload_to="branding/", verbose_name="Логотип")),
                ("footer_text", models.CharField(default="ICL Системные технологии — комплексная защита информации в эпоху ИИ", max_length=255, verbose_name="Текст в подвале страниц")),
            ],
            options={
                "verbose_name": "Настройки сайта",
                "verbose_name_plural": "Настройки сайта",
            },
        ),
    ]
