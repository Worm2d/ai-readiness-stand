from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ("risks", "0001_initial"),
        ("services", "0001_initial"),
    ]

    operations = [
        migrations.AddField(
            model_name="risk",
            name="related_service",
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name="related_risks", to="services.service", verbose_name="Услуга, закрывающая риск"),
        ),
    ]
