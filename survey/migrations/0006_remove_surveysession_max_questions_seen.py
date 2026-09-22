from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ("survey", "0005_surveysession_max_questions_seen"),
    ]

    operations = [
        migrations.RemoveField(
            model_name="surveysession",
            name="max_questions_seen",
        ),
    ]
