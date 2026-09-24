from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("core", "0006_report_settings_and_email"),
    ]

    operations = [
        migrations.AddField(
            model_name="sitesettings",
            name="show_score_number",
            field=models.BooleanField(
                default=True,
                help_text=(
                    "Если выключено — на странице отчёта не показывается число «N/100» и прогресс-бар. "
                    "Текстовая интерпретация уровня (заголовок и описание) управляется отдельным переключателем ниже."
                ),
                verbose_name="Показывать числовой балл и прогресс-бар",
            ),
        ),
        migrations.AlterField(
            model_name="sitesettings",
            name="show_score_block",
            field=models.BooleanField(
                default=True,
                help_text=(
                    "Если выключено — не показывается текстовая интерпретация уровня готовности (например, "
                    "«Критический уровень готовности», «Требует внимания», «Хороший уровень») и её описание. "
                    "Числовой балл и прогресс-бар управляются отдельным переключателем выше. Заголовок «Отчёт» "
                    "и подпись под ним остаются в любом случае."
                ),
                verbose_name="Показывать текстовую интерпретацию уровня",
            ),
        ),
    ]
