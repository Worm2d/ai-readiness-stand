from django.contrib import admin

from .models import Answer, AnswerOption, Question, SurveySession


class AnswerOptionInline(admin.TabularInline):
    model = AnswerOption
    extra = 1
    fields = ("text", "order", "risk_tags", "score_weight")
    filter_horizontal = ("risk_tags",)


@admin.register(Question)
class QuestionAdmin(admin.ModelAdmin):
    list_display = ("order", "title", "question_type", "parent_question", "is_required", "is_active")
    list_filter = ("question_type", "is_active", "is_required")
    search_fields = ("title", "subtitle")
    ordering = ("order",)
    inlines = [AnswerOptionInline]
    autocomplete_fields = ("parent_question",)
    filter_horizontal = ("show_only_if_parent_answered",)

    fieldsets = (
        (None, {
            "fields": ("order", "question_type", "title", "subtitle", "is_required", "is_active"),
        }),
        ("Числовой ответ", {
            "fields": ("number_min", "number_max", "number_step"),
            "classes": ("collapse",),
        }),
        ("Условная логика показа", {
            "fields": ("parent_question", "show_only_if_parent_answered"),
            "description": (
                "Заполните, если этот вопрос должен появляться только после определённого ответа "
                "на другой (родительский) вопрос. Оставьте пустым, чтобы вопрос показывался всегда. "
                "В поле «Показывать при ответах родителя» доступны только варианты ответа выбранного "
                "родительского вопроса — сохраните вопрос после выбора родителя, если список вариантов "
                "пуст, затем откройте вопрос повторно."
            ),
        }),
    )

    def get_form(self, request, obj=None, **kwargs):
        form = super().get_form(request, obj, **kwargs)
        if obj is not None and "show_only_if_parent_answered" in form.base_fields:
            field = form.base_fields["show_only_if_parent_answered"]
            if obj.parent_question_id:
                field.queryset = field.queryset.filter(question_id=obj.parent_question_id)
            else:
                field.queryset = field.queryset.none()
        return form


class AnswerInline(admin.TabularInline):
    model = Answer
    extra = 0
    can_delete = False
    fields = ("question", "text_value", "number_value", "answered_at")
    readonly_fields = ("question", "text_value", "number_value", "answered_at")
    show_change_link = False


@admin.register(SurveySession)
class SurveySessionAdmin(admin.ModelAdmin):
    list_display = (
        "uuid", "started_at", "is_completed", "score",
        "visitor_name", "visitor_company", "personal_data_consent",
    )
    list_filter = ("is_completed", "personal_data_consent")
    search_fields = ("uuid", "visitor_name", "visitor_company", "visitor_email", "visitor_phone")
    readonly_fields = [f.name for f in SurveySession._meta.fields]
    inlines = [AnswerInline]

    def has_add_permission(self, request):
        return False
