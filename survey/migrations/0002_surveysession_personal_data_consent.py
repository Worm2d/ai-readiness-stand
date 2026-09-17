from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ("survey", "0001_initial"),
    ]

    operations = [
        migrations.AddField(
            model_name="surveysession",
            name="personal_data_consent",
            field=models.BooleanField(default=False, verbose_name="Согласие на обработку персональных данных"),
        ),
        migrations.AddField(
            model_name="surveysession",
            name="personal_data_consent_at",
            field=models.DateTimeField(
                blank=True,
                null=True,
                verbose_name="Время согласия на обработку персональных данных",
            ),
        ),
    ]
