"""Модели реестра рисков, категорий, рекомендаций и интерпретации скоринга."""
from django.db import models
from django.utils.text import slugify


class RiskCategory(models.Model):
    name = models.CharField("Название категории", max_length=100, unique=True)
    slug = models.SlugField("Slug", max_length=120, unique=True, blank=True)
    description = models.TextField("Описание", blank=True)
    color = models.CharField("Цвет маркировки (HEX)", max_length=7, default="#E30613")

    class Meta:
        verbose_name = "Категория риска"
        verbose_name_plural = "Категории рисков"
        ordering = ["name"]

    def __str__(self):
        return self.name

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.name, allow_unicode=True)
        super().save(*args, **kwargs)


class Risk(models.Model):
    SEVERITY_CHOICES = [
        ("low", "Низкий"), ("medium", "Средний"), ("high", "Высокий"), ("critical", "Критический"),
    ]

    title = models.CharField("Название риска", max_length=255)
    description = models.TextField("Описание")
    categories = models.ManyToManyField(RiskCategory, verbose_name="Категории", related_name="risks")
    severity = models.CharField("Критичность", max_length=10, choices=SEVERITY_CHOICES, default="medium")
    public_case_title = models.CharField("Заголовок публичного кейса", max_length=255, blank=True)
    public_case_description = models.TextField("Описание инцидента / статистики", blank=True)
    public_case_source_url = models.URLField("Ссылка на источник", blank=True)
    public_case_region = models.CharField("Регион", max_length=100, default="Россия", blank=True)
    related_service = models.ForeignKey(
        "services.Service", verbose_name="Услуга, закрывающая риск",
        on_delete=models.SET_NULL, null=True, blank=True, related_name="related_risks",
    )
    is_active = models.BooleanField("Активен", default=True)
    order = models.PositiveIntegerField("Порядок / приоритет", default=0)

    class Meta:
        verbose_name = "Риск"
        verbose_name_plural = "Реестр рисков"
        ordering = ["order", "title"]

    def __str__(self):
        return self.title


class Recommendation(models.Model):
    title = models.CharField("Заголовок", max_length=255)
    description = models.TextField("Описание")
    order = models.PositiveIntegerField("Порядок", default=0)
    related_category = models.ForeignKey(
        RiskCategory, verbose_name="Связанная категория",
        on_delete=models.SET_NULL, null=True, blank=True, related_name="recommendations",
    )
    is_active = models.BooleanField("Активна", default=True)

    class Meta:
        verbose_name = "Рекомендация"
        verbose_name_plural = "Рекомендации"
        ordering = ["order", "title"]

    def __str__(self):
        return self.title


class ScoreInterpretation(models.Model):
    min_score = models.PositiveSmallIntegerField("Минимум диапазона")
    max_score = models.PositiveSmallIntegerField("Максимум диапазона")
    title = models.CharField("Заголовок уровня", max_length=255)
    description = models.TextField("Описание уровня")
    color = models.CharField("Цвет (HEX)", max_length=7, default="#E30613")

    class Meta:
        verbose_name = "Интерпретация балла"
        verbose_name_plural = "Интерпретации балла"
        ordering = ["min_score"]

    def __str__(self):
        return f"{self.min_score}-{self.max_score}: {self.title}"

    @classmethod
    def for_score(cls, score):
        return cls.objects.filter(min_score__lte=score, max_score__gte=score).first()
