from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("survey", "0003_question_conditional_logic"),
        ("risks", "0004_risk_tag_mitigation"),
    ]

    operations = [
        migrations.RemoveField(
            model_name="answeroption",
            name="risk_tags",
        ),
        migrations.AddField(
            model_name="answeroption",
            name="risk_tags",
            field=models.ManyToManyField(
                blank=True,
                related_name="answer_options",
                to="risks.risk",
                verbose_name="Риски, срабатывающие при этом ответе",
            ),
        ),
    ]
