from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True
    dependencies = []

    operations = [
        migrations.CreateModel(
            name="RiskCategory",
            fields=[
                ("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
                ("name", models.CharField(max_length=100, unique=True, verbose_name="Название категории")),
                ("slug", models.SlugField(blank=True, max_length=120, unique=True, verbose_name="Slug")),
                ("description", models.TextField(blank=True, verbose_name="Описание")),
                ("color", models.CharField(default="#E30613", max_length=7, verbose_name="Цвет маркировки (HEX)")),
            ],
            options={
                "verbose_name": "Категория риска",
                "verbose_name_plural": "Категории рисков",
                "ordering": ["name"],
            },
        ),
        migrations.CreateModel(
            name="ScoreInterpretation",
            fields=[
                ("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
                ("min_score", models.PositiveSmallIntegerField(verbose_name="Минимум диапазона")),
                ("max_score", models.PositiveSmallIntegerField(verbose_name="Максимум диапазона")),
                ("title", models.CharField(max_length=255, verbose_name="Заголовок уровня")),
                ("description", models.TextField(verbose_name="Описание уровня")),
                ("color", models.CharField(default="#E30613", max_length=7, verbose_name="Цвет (HEX)")),
            ],
            options={
                "verbose_name": "Интерпретация балла",
                "verbose_name_plural": "Интерпретации балла",
                "ordering": ["min_score"],
            },
        ),
        migrations.CreateModel(
            name="Risk",
            fields=[
                ("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
                ("title", models.CharField(max_length=255, verbose_name="Название риска")),
                ("description", models.TextField(verbose_name="Описание")),
                ("severity", models.CharField(choices=[("low", "Низкий"), ("medium", "Средний"), ("high", "Высокий"), ("critical", "Критический")], default="medium", max_length=10, verbose_name="Критичность")),
                ("public_case_title", models.CharField(blank=True, max_length=255, verbose_name="Заголовок публичного кейса")),
                ("public_case_description", models.TextField(blank=True, verbose_name="Описание инцидента / статистики")),
                ("public_case_source_url", models.URLField(blank=True, verbose_name="Ссылка на источник")),
                ("public_case_region", models.CharField(blank=True, default="Россия", max_length=100, verbose_name="Регион")),
                ("is_active", models.BooleanField(default=True, verbose_name="Активен")),
                ("order", models.PositiveIntegerField(default=0, verbose_name="Порядок / приоритет")),
                ("categories", models.ManyToManyField(related_name="risks", to="risks.riskcategory", verbose_name="Категории")),
            ],
            options={
                "verbose_name": "Риск",
                "verbose_name_plural": "Реестр рисков",
                "ordering": ["order", "title"],
            },
        ),
        migrations.CreateModel(
            name="Recommendation",
            fields=[
                ("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
                ("title", models.CharField(max_length=255, verbose_name="Заголовок")),
                ("description", models.TextField(verbose_name="Описание")),
                ("order", models.PositiveIntegerField(default=0, verbose_name="Порядок")),
                ("is_active", models.BooleanField(default=True, verbose_name="Активна")),
                ("related_category", models.ForeignKey(blank=True, null=True, on_delete=models.SET_NULL, related_name="recommendations", to="risks.riskcategory", verbose_name="Связанная категория")),
            ],
            options={
                "verbose_name": "Рекомендация",
                "verbose_name_plural": "Рекомендации",
                "ordering": ["order", "title"],
            },
        ),
    ]
