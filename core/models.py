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
    personal_data_consent_text = models.TextField(
        "Текст согласия на обработку персональных данных",
        default="Я даю согласие на обработку моих персональных данных для подготовки и отправки отчёта.",
        help_text="Служебное поле. Используется как запасной текст согласия, если потребуется вернуть отдельное окно.",
    )
    privacy_policy_file = models.FileField(
        "Файл политики конфиденциальности",
        upload_to="policy/",
        blank=True,
        null=True,
        help_text=(
            "PDF или другой документ с политикой обработки персональных данных. Ссылка на скачивание "
            "этого файла показывается в форме сбора контактов рядом с текстом согласия."
        ),
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
    qr_hint_text = models.CharField(
        "Текст подсказки под QR-кодом отчёта",
        max_length=255,
        default="Отсканируйте, чтобы открыть отчёт на телефоне",
        help_text="Показывается под QR-кодом на странице результата опроса.",
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
