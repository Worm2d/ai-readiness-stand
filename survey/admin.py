from django.contrib import admin

from .models import Answer, AnswerOption, Question, SurveySession


class AnswerOptionInline(admin.TabularInline):
    model = AnswerOption
    extra = 1
    filter_horizontal = ("risk_tags",)
    fields = ("text", "order", "risk_tags", "score_weight")


@admin.register(Question)
class QuestionAdmin(admin.ModelAdmin):
    list_display = ("order", "title_short", "question_type", "is_required", "is_active")
    list_filter = ("question_type", "is_required", "is_active")
    search_fields = ("title",)
    ordering = ("order",)
    inlines = [AnswerOptionInline]
    fieldsets = (
        (None, {"fields": ("order", "question_type", "title", "subtitle", "is_required", "is_active")}),
        ("Параметры числового ответа", {"fields": ("number_min", "number_max", "number_step"), "classes": ("collapse",)}),
    )

    @admin.display(description="Вопрос")
    def title_short(self, obj):
        return obj.title[:80]


class AnswerInline(admin.TabularInline):
    model = Answer
    extra = 0
    readonly_fields = ("question", "selected_options", "text_value", "number_value", "answered_at")
    can_delete = False
    filter_horizontal = ("selected_options",)


@admin.register(SurveySession)
class SurveySessionAdmin(admin.ModelAdmin):
    list_display = ("uuid", "started_at", "is_completed", "score", "visitor_name", "visitor_company")
    list_filter = ("is_completed",)
    search_fields = ("uuid", "visitor_name", "visitor_company", "visitor_email")
    readonly_fields = ("uuid", "started_at", "finished_at")
    inlines = [AnswerInline]
    ordering = ("-started_at",)
