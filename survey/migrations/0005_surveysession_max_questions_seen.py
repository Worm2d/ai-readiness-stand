from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("survey", "0004_answeroption_risk_tags_risk"),
    ]

    operations = [
        migrations.AddField(
            model_name="surveysession",
            name="max_questions_seen",
            field=models.PositiveIntegerField(
                default=0,
                help_text=(
                    'Служебное поле: не даёт счётчику "Вопрос X из N" уменьшаться при повторном '
                    "ответе на условный вопрос."
                ),
                verbose_name="Максимум показанных вопросов",
            ),
        ),
    ]
