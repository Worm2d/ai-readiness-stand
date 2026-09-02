from django.contrib import admin

from .models import Service


@admin.register(Service)
class ServiceAdmin(admin.ModelAdmin):
    list_display = ("title", "url", "is_active", "order")
    list_filter = ("is_active", "category")
    search_fields = ("title", "short_description")
    filter_horizontal = ("category",)
    ordering = ("order",)
