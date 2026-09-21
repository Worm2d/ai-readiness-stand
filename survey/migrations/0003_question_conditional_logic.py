from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):
    dependencies = [
        ("survey", "0002_seed_data"),
        ("survey", "0002_surveysession_personal_data_consent"),
    ]

    operations = [
        migrations.AddField(
            model_name="question",
            name="parent_question",
            field=models.ForeignKey(
                blank=True,
                help_text=(
                    "Если указан — этот вопрос будет показан только тогда, когда на родительский "
                    "вопрос дан один из вариантов, отмеченных ниже в поле «Показывать при ответах "
                    "родителя»."
                ),
                null=True,
                on_delete=django.db.models.deletion.SET_NULL,
                related_name="dependent_questions",
                to="survey.question",
                verbose_name="Родительский вопрос",
            ),
        ),
        migrations.AddField(
            model_name="question",
            name="show_only_if_parent_answered",
            field=models.ManyToManyField(
                blank=True,
                help_text=(
                    "Варианты ответа родительского вопроса, при выборе КОТОРЫХ (любого из них) этот "
                    "вопрос будет показан. Варианты должны принадлежать выбранному родительскому "
                    "вопросу. Если поле пустое, условие не проверяется."
                ),
                related_name="unlocks_questions",
                to="survey.answeroption",
                verbose_name="Показывать при ответах родителя",
            ),
        ),
    ]
