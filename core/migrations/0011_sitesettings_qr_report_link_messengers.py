from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("core", "0010_alter_sitesettings_always_recommendation_text_and_more"),
    ]

    operations = [
        migrations.AddField(
            model_name="sitesettings",
            name="show_qr_codes",
            field=models.BooleanField(
                default=False,
                help_text=(
                    "Если включено — на странице результата опроса показываются QR-коды со ссылкой на отчёт "
                    "(сверху и снизу страницы). По умолчанию выключено."
                ),
                verbose_name="Показывать QR-коды на странице результата",
            ),
        ),
        migrations.AddField(
            model_name="sitesettings",
            name="show_report_link",
            field=models.BooleanField(
                default=True,
                help_text=(
                    "Если выключено — в конце страницы результата не показывается текстовая ссылка на "
                    "персональный отчёт."
                ),
                verbose_name="Показывать надпись «Ссылка на этот отчёт»",
            ),
        ),
        migrations.AddField(
            model_name="sitesettings",
            name="telegram_url",
            field=models.URLField(
                blank=True,
                default="",
                help_text=(
                    "Например, https://t.me/your_channel. Если поле пустое — кнопка Telegram в конце отчёта "
                    "не показывается."
                ),
                verbose_name="Ссылка на Telegram",
            ),
        ),
        migrations.AddField(
            model_name="sitesettings",
            name="max_url",
            field=models.URLField(
                blank=True,
                default="",
                help_text="Ссылка на канал или страницу в мессенджере MAX. Если поле пустое — кнопка MAX в конце отчёта не показывается.",
                verbose_name="Ссылка на MAX",
            ),
        ),
    ]
