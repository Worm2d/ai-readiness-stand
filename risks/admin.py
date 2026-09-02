from django.contrib import admin

from .models import Recommendation, Risk, RiskCategory, ScoreInterpretation


@admin.register(RiskCategory)
class RiskCategoryAdmin(admin.ModelAdmin):
    list_display = ("name", "slug", "color")
    search_fields = ("name",)
    prepopulated_fields = {"slug": ("name",)}


@admin.register(Risk)
class RiskAdmin(admin.ModelAdmin):
    list_display = ("title", "severity", "categories_list", "is_active", "order")
    list_filter = ("severity", "is_active", "categories")
    search_fields = ("title", "description", "public_case_title")
    filter_horizontal = ("categories",)
    ordering = ("order", "title")
    fieldsets = (
        (None, {"fields": ("title", "description", "categories", "severity", "is_active", "order")}),
        ("Публичный кейс", {"fields": ("public_case_title", "public_case_description", "public_case_source_url", "public_case_region")}),
        ("Связь с услугами", {"fields": ("related_service",)}),
    )

    @admin.display(description="Категории")
    def categories_list(self, obj):
        return ", ".join(c.name for c in obj.categories.all())


@admin.register(Recommendation)
class RecommendationAdmin(admin.ModelAdmin):
    list_display = ("title", "related_category", "is_active", "order")
    list_filter = ("is_active", "related_category")
    search_fields = ("title", "description")
    ordering = ("order",)


@admin.register(ScoreInterpretation)
class ScoreInterpretationAdmin(admin.ModelAdmin):
    list_display = ("title", "min_score", "max_score", "color")
    ordering = ("min_score",)
