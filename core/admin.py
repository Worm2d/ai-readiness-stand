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
                    "require_personal_data_consent",
                    "personal_data_consent_text",
                    "personal_data_policy_url",
                    "personal_data_policy_link_text",
                )
            },
        ),
        (
            "Стартовая страница",
            {"fields": ("landing_title", "landing_subtitle", "button_text", "logo", "primary_color")},
        ),
        ("Страница результата", {"fields": ("result_title",)}),
        ("Компания", {"fields": ("company_name", "company_website", "company_email", "footer_text")}),
    )

    def has_add_permission(self, request):
        return not SiteSettings.objects.exists()

    def has_delete_permission(self, request, obj=None):
        return False

    def changelist_view(self, request, extra_context=None):
        obj = SiteSettings.load()
        return redirect("admin:core_sitesettings_change", obj.pk)
