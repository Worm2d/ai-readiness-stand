from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ("core", "0001_initial"),
    ]

    operations = [
        migrations.AddField(
            model_name="sitesettings",
            name="personal_data_consent_text",
            field=models.TextField(
                default="Я даю согласие на обработку моих персональных данных для подготовки и отправки отчёта.",
                verbose_name="Текст согласия на обработку персональных данных",
            ),
        ),
        migrations.AddField(
            model_name="sitesettings",
            name="personal_data_policy_link_text",
            field=models.CharField(
                default="Политика обработки персональных данных",
                max_length=255,
                verbose_name="Текст ссылки на политику",
            ),
        ),
        migrations.AddField(
            model_name="sitesettings",
            name="personal_data_policy_url",
            field=models.URLField(
                blank=True,
                default="",
                help_text="Необязательная ссылка, которая показывается рядом с согласием.",
                verbose_name="Ссылка на политику обработки персональных данных",
            ),
        ),
        migrations.AddField(
            model_name="sitesettings",
            name="require_personal_data_consent",
            field=models.BooleanField(
                default=True,
                help_text="При включённом сборе контактов посетитель должен подтвердить согласие, чтобы отправить форму.",
                verbose_name="Запрашивать согласие на обработку персональных данных",
            ),
        ),
    ]
