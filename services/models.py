"""Модель услуг компании ICL Системные технологии, показываемых в отчёте."""
from django.db import models


class Service(models.Model):
    title = models.CharField("Название услуги", max_length=255)
    short_description = models.CharField("Краткое описание", max_length=500)
    full_description = models.TextField("Полное описание", blank=True)
    url = models.URLField("Ссылка на страницу услуги", default="https://icl-st.ru/")
    category = models.ManyToManyField(
        "risks.RiskCategory", verbose_name="Связанные категории рисков",
        related_name="services", blank=True,
    )
    order = models.PositiveIntegerField("Порядок", default=0)
    is_active = models.BooleanField("Активна", default=True)
    icon = models.ImageField("Иконка/изображение", upload_to="services/", blank=True, null=True)

    class Meta:
        verbose_name = "Услуга"
        verbose_name_plural = "Услуги"
        ordering = ["order", "title"]

    def __str__(self):
        return self.title
