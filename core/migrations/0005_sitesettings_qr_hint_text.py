from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("core", "0004_merge_0002_seed_data_0003_privacy_policy_file"),
    ]

    operations = [
        migrations.AddField(
            model_name="sitesettings",
            name="qr_hint_text",
            field=models.CharField(
                default="Отсканируйте, чтобы открыть отчёт на телефоне",
                help_text="Показывается под QR-кодом на странице результата опроса.",
                max_length=255,
                verbose_name="Текст подсказки под QR-кодом отчёта",
            ),
        ),
    ]
