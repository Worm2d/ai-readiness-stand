import uuid

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    initial = True
    dependencies = [("risks", "0001_initial")]

    operations = [
        migrations.CreateModel(
            name="Question",
            fields=[
                ("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
                ("order", models.PositiveIntegerField(default=0, verbose_name="Порядок показа")),
                ("question_type", models.CharField(choices=[("info_text", "Информационный блок (без ответа)"), ("single_choice", "Один вариант из списка"), ("multiple_choice", "Несколько вариантов из списка"), ("text_input", "Свободный текст"), ("number_input", "Числовой ответ")], default="single_choice", max_length=20, verbose_name="Тип вопроса")),
                ("title", models.TextField(verbose_name="Текст вопроса / блока")),
                ("subtitle", models.TextField(blank=True, verbose_name="Пояснение (необязательно)")),
                ("is_required", models.BooleanField(default=True, verbose_name="Обязательный вопрос")),
                ("is_active", models.BooleanField(default=True, verbose_name="Активен")),
                ("number_min", models.IntegerField(blank=True, null=True, verbose_name="Минимум (для числового ответа)")),
                ("number_max", models.IntegerField(blank=True, null=True, verbose_name="Максимум (для числового ответа)")),
                ("number_step", models.IntegerField(blank=True, default=1, null=True, verbose_name="Шаг (для числового ответа)")),
            ],
            options={
                "verbose_name": "Вопрос",
                "verbose_name_plural": "Вопросы опроса",
                "ordering": ["order"],
            },
        ),
        migrations.CreateModel(
            name="SurveySession",
            fields=[
                ("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
                ("uuid", models.UUIDField(default=uuid.uuid4, editable=False, unique=True, verbose_name="UUID сессии")),
                ("started_at", models.DateTimeField(auto_now_add=True, verbose_name="Начата")),
                ("finished_at", models.DateTimeField(blank=True, null=True, verbose_name="Завершена")),
                ("is_completed", models.BooleanField(default=False, verbose_name="Завершена")),
                ("score", models.IntegerField(blank=True, null=True, verbose_name="Итоговый балл (0-100)")),
                ("visitor_name", models.CharField(blank=True, max_length=255, null=True, verbose_name="Имя посетителя")),
                ("visitor_company", models.CharField(blank=True, max_length=255, null=True, verbose_name="Компания")),
                ("visitor_position", models.CharField(blank=True, max_length=255, null=True, verbose_name="Должность")),
                ("visitor_email", models.EmailField(blank=True, max_length=254, null=True, verbose_name="E-mail")),
                ("visitor_phone", models.CharField(blank=True, max_length=50, null=True, verbose_name="Телефон")),
            ],
            options={
                "verbose_name": "Сессия опроса",
                "verbose_name_plural": "Сессии опроса",
                "ordering": ["-started_at"],
            },
        ),
        migrations.CreateModel(
            name="AnswerOption",
            fields=[
                ("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
                ("text", models.CharField(max_length=255, verbose_name="Текст варианта")),
                ("order", models.PositiveIntegerField(default=0, verbose_name="Порядок")),
                ("score_weight", models.IntegerField(default=0, verbose_name="Вес для скоринга")),
                ("question", models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name="options", to="survey.question", verbose_name="Вопрос")),
                ("risk_tags", models.ManyToManyField(blank=True, related_name="answer_options", to="risks.riskcategory", verbose_name="Теги категорий риска")),
            ],
            options={
                "verbose_name": "Вариант ответа",
                "verbose_name_plural": "Варианты ответов",
                "ordering": ["order"],
            },
        ),
        migrations.CreateModel(
            name="Answer",
            fields=[
                ("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
                ("text_value", models.TextField(blank=True, null=True, verbose_name="Текстовый ответ")),
                ("number_value", models.IntegerField(blank=True, null=True, verbose_name="Числовой ответ")),
                ("answered_at", models.DateTimeField(auto_now_add=True, verbose_name="Время ответа")),
                ("question", models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name="answers", to="survey.question", verbose_name="Вопрос")),
                ("session", models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name="answers", to="survey.surveysession", verbose_name="Сессия")),
                ("selected_options", models.ManyToManyField(blank=True, related_name="answers", to="survey.answeroption", verbose_name="Выбранные варианты")),
            ],
            options={
                "verbose_name": "Ответ",
                "verbose_name_plural": "Ответы",
                "unique_together": {("session", "question")},
            },
        ),
    ]
