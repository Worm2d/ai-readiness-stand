from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("risks", "0003_seed_data"),
    ]

    operations = [
        migrations.AddField(
            model_name="risk",
            name="tag",
            field=models.SlugField(
                blank=True,
                help_text=(
                    "Уникальный код риска (например, PDN-PROMPT-LEAK), на который ссылаются варианты "
                    "ответов опроса."
                ),
                max_length=64,
                null=True,
                unique=True,
                verbose_name="Тег риска",
            ),
        ),
        migrations.AddField(
            model_name="risk",
            name="mitigation",
            field=models.TextField(blank=True, verbose_name="Рекомендации по митигации"),
        ),
        migrations.AlterField(
            model_name="risk",
            name="categories",
            field=models.ManyToManyField(blank=True, related_name="risks", to="risks.riskcategory", verbose_name="Категории"),
        ),
    ]
