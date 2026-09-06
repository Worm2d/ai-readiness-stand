"""Модели опроса: вопросы, варианты ответов, сессии прохождения, ответы."""
import uuid

from django.db import models


class Question(models.Model):
    QUESTION_TYPES = [
        ("info_text", "Информационный блок (без ответа)"),
        ("single_choice", "Один вариант из списка"),
        ("multiple_choice", "Несколько вариантов из списка"),
        ("text_input", "Свободный текст"),
        ("number_input", "Числовой ответ"),
    ]

    order = models.PositiveIntegerField("Порядок показа", default=0)
    question_type = models.CharField("Тип вопроса", max_length=20, choices=QUESTION_TYPES, default="single_choice")
    title = models.TextField("Текст вопроса / блока")
    subtitle = models.TextField("Пояснение (необязательно)", blank=True)
    is_required = models.BooleanField("Обязательный вопрос", default=True)
    is_active = models.BooleanField("Активен", default=True)
    number_min = models.IntegerField("Минимум (для числового ответа)", null=True, blank=True)
    number_max = models.IntegerField("Максимум (для числового ответа)", null=True, blank=True)
    number_step = models.IntegerField("Шаг (для числового ответа)", null=True, blank=True, default=1)

    class Meta:
        verbose_name = "Вопрос"
        verbose_name_plural = "Вопросы опроса"
        ordering = ["order"]

    def __str__(self):
        return f"{self.order}. {self.title[:60]}"

    @property
    def has_options(self):
        return self.question_type in ("single_choice", "multiple_choice")


class AnswerOption(models.Model):
    question = models.ForeignKey(Question, verbose_name="Вопрос", on_delete=models.CASCADE, related_name="options")
    text = models.CharField("Текст варианта", max_length=255)
    order = models.PositiveIntegerField("Порядок", default=0)
    risk_tags = models.ManyToManyField(
        "risks.RiskCategory", verbose_name="Теги категорий риска", blank=True, related_name="answer_options"
    )
    score_weight = models.IntegerField("Вес для скоринга", default=0)

    class Meta:
        verbose_name = "Вариант ответа"
        verbose_name_plural = "Варианты ответов"
        ordering = ["order"]

    def __str__(self):
        return f"{self.text} ({self.question})"


class SurveySession(models.Model):
    uuid = models.UUIDField("UUID сессии", default=uuid.uuid4, editable=False, unique=True, db_index=True)
    started_at = models.DateTimeField("Начата", auto_now_add=True)
    finished_at = models.DateTimeField("Завершена", null=True, blank=True)
    is_completed = models.BooleanField("Завершена", default=False)
    score = models.IntegerField("Итоговый балл (0-100)", null=True, blank=True)
    visitor_name = models.CharField("Имя посетителя", max_length=255, blank=True, null=True)
    visitor_company = models.CharField("Компания", max_length=255, blank=True, null=True)
    visitor_position = models.CharField("Должность", max_length=255, blank=True, null=True)
    visitor_email = models.EmailField("E-mail", blank=True, null=True)
    visitor_phone = models.CharField("Телефон", max_length=50, blank=True, null=True)
    personal_data_consent = models.BooleanField("Согласие на обработку персональных данных", default=False)
    personal_data_consent_at = models.DateTimeField("Время согласия на обработку персональных данных", null=True, blank=True)

    class Meta:
        verbose_name = "Сессия опроса"
        verbose_name_plural = "Сессии опроса"
        ordering = ["-started_at"]

    def __str__(self):
        return f"Сессия {self.uuid} ({self.started_at:%d.%m.%Y %H:%M})"


class Answer(models.Model):
    session = models.ForeignKey(SurveySession, verbose_name="Сессия", on_delete=models.CASCADE, related_name="answers")
    question = models.ForeignKey(Question, verbose_name="Вопрос", on_delete=models.CASCADE, related_name="answers")
    selected_options = models.ManyToManyField(AnswerOption, verbose_name="Выбранные варианты", blank=True, related_name="answers")
    text_value = models.TextField("Текстовый ответ", blank=True, null=True)
    number_value = models.IntegerField("Числовой ответ", blank=True, null=True)
    answered_at = models.DateTimeField("Время ответа", auto_now_add=True)

    class Meta:
        verbose_name = "Ответ"
        verbose_name_plural = "Ответы"
        unique_together = ("session", "question")

    def __str__(self):
        return f"Ответ на «{self.question}» в сессии {self.session.uuid}"
