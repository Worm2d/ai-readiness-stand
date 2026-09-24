from django.contrib import admin
from django.shortcuts import redirect

from .models import SiteSettings


@admin.register(SiteSettings)
class SiteSettingsAdmin(admin.ModelAdmin):
    fieldsets = (
        (
            "Опрос",
            {
                "fields": (
                    "collect_personal_data",
                    "personal_data_consent_text",
                    "privacy_policy_file",
                    "show_question_counter",
                )
            },
        ),
        (
            "Стартовая страница",
            {"fields": ("landing_title", "landing_subtitle", "button_text", "logo", "primary_color")},
        ),
        (
            "Страница результата",
            {"fields": ("result_title", "qr_hint_text", "show_score_number", "show_score_block")},
        ),
        (
            "Обязательная рекомендация (показывается всегда)",
            {
                "fields": (
                    "always_recommendation_title",
                    "always_recommendation_text",
                    "always_recommendation_email_label",
                    "always_recommendation_website_label",
                )
            },
        ),
        (
            "Письмо с отчётом",
            {"fields": ("email_subject", "email_body_template")},
        ),
        ("Компания", {"fields": ("company_name", "company_website", "company_email", "footer_text")}),
    )

    def has_add_permission(self, request):
        return not SiteSettings.objects.exists()

    def has_delete_permission(self, request, obj=None):
        return False

    def changelist_view(self, request, extra_context=None):
        obj = SiteSettings.load()
        return redirect("admin:core_sitesettings_change", obj.pk)
