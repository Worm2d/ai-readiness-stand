from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True
    dependencies = [("risks", "0001_initial")]

    operations = [
        migrations.CreateModel(
            name="Service",
            fields=[
                ("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
                ("title", models.CharField(max_length=255, verbose_name="Название услуги")),
                ("short_description", models.CharField(max_length=500, verbose_name="Краткое описание")),
                ("full_description", models.TextField(blank=True, verbose_name="Полное описание")),
                ("url", models.URLField(default="https://icl-st.ru/", verbose_name="Ссылка на страницу услуги")),
                ("order", models.PositiveIntegerField(default=0, verbose_name="Порядок")),
                ("is_active", models.BooleanField(default=True, verbose_name="Активна")),
                ("icon", models.ImageField(blank=True, null=True, upload_to="services/", verbose_name="Иконка/изображение")),
                ("category", models.ManyToManyField(blank=True, related_name="services", to="risks.riskcategory", verbose_name="Связанные категории рисков")),
            ],
            options={
                "verbose_name": "Услуга",
                "verbose_name_plural": "Услуги",
                "ordering": ["order", "title"],
            },
        ),
    ]
