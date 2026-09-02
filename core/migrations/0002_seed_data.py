"""Data migration: создаёт запись SiteSettings по умолчанию (singleton)."""
from django.db import migrations


def seed_data(apps, schema_editor):
    SiteSettings = apps.get_model("core", "SiteSettings")
    SiteSettings.objects.get_or_create(pk=1)


def unseed_data(apps, schema_editor):
    pass


class Migration(migrations.Migration):

    dependencies = [("core", "0001_initial")]

    operations = [migrations.RunPython(seed_data, unseed_data)]
