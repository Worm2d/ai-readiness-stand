"""Общие модели приложения: глобальные настройки стенда (singleton)."""
from django.core.exceptions import ValidationError
from django.db import models


class SiteSettings(models.Model):
    """Глобальные редактируемые настройки лендинга, опроса и отчёта (singleton, pk=1)."""

    collect_personal_data = models.BooleanField(
        "Собирать контакты посетителя",
        default=True,
        help_text="Если включено — перед показом результата будет показана форма (имя, компания, email/телефон).",
    )
    require_personal_data_consent = models.BooleanField(
        "Запрашивать согласие на обработку персональных данных",
        default=True,
        help_text="При включённом сборе контактов посетитель должен подтвердить согласие, чтобы отправить форму.",
    )
    personal_data_consent_text = models.TextField(
        "Текст согласия на обработку персональных данных",
        default="Я даю согласие на обработку моих персональных данных для подготовки и отправки отчёта.",
    )
    personal_data_policy_url = models.URLField(
        "Ссылка на политику обработки персональных данных",
        blank=True,
        default="",
        help_text="Необязательная ссылка, которая показывается рядом с согласием.",
    )
    personal_data_policy_link_text = models.CharField(
        "Текст ссылки на политику",
        max_length=255,
        default="Политика обработки персональных данных",
    )

    landing_title = models.CharField(
        "Заголовок стартовой страницы",
        max_length=255,
        default="А ты готов к эпохе Искусственного Интеллекта?",
    )
    landing_subtitle = models.TextField(
        "Пояснительный текст на стартовой странице",
        default=(
            "Речь идёт о защите информации в эпоху ИИ: защита локальных языковых моделей "
            "внутри организаций, защита от утечек данных через публичные ИИ-сервисы, защита "
            "от атак, сгенерированных или усиленных искусственным интеллектом, а также "
            "применение ИИ в самих средствах защиты информации."
        ),
    )
    button_text = models.CharField("Текст на кнопках старта опроса", max_length=50, default="Нет")
    result_title = models.CharField(
        "Заголовок страницы результата",
        max_length=255,
        default="Вы не готовы, но мы можем Вам помочь",
    )
    company_name = models.CharField("Название компании", max_length=255, default="ICL Системные технологии")
    company_website = models.URLField("Сайт компании", default="https://icl-st.ru/")
    company_email = models.EmailField("E-mail компании", default="office@icl-st.ru")
    primary_color = models.CharField("Основной корпоративный цвет (HEX)", max_length=7, default="#E30613")
    logo = models.ImageField("Логотип", upload_to="branding/", blank=True, null=True)
    footer_text = models.CharField(
        "Текст в подвале страниц",
        max_length=255,
        default="ICL Системные технологии — комплексная защита информации в эпоху ИИ",
    )

    class Meta:
        verbose_name = "Настройки сайта"
        verbose_name_plural = "Настройки сайта"

    def __str__(self):
        return "Глобальные настройки сайта"

    def save(self, *args, **kwargs):
        self.pk = 1
        super().save(*args, **kwargs)

    def delete(self, *args, **kwargs):
        pass

    def clean(self):
        if SiteSettings.objects.exclude(pk=self.pk).exists():
            raise ValidationError("Может существовать только одна запись настроек сайта.")

    @classmethod
    def load(cls):
        obj, _ = cls.objects.get_or_create(pk=1)
        return obj
