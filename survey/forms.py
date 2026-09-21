"""Формы для динамического опроса и сбора контактов посетителя."""
from django import forms

from .models import Question


class ContactForm(forms.Form):
    visitor_name = forms.CharField(label="Имя", max_length=255, required=False)
    visitor_company = forms.CharField(label="Компания", max_length=255, required=False)
    visitor_position = forms.CharField(label="Должность", max_length=255, required=False)
    visitor_email = forms.EmailField(label="E-mail", required=True)
    visitor_phone = forms.CharField(label="Телефон", max_length=50, required=False)


def build_question_form(question: Question, data=None):
    required = question.is_required

    class DynamicQuestionForm(forms.Form):
        pass

    if question.question_type == "single_choice":
        choices = [(str(opt.id), opt.text) for opt in question.options.all().order_by("order")]
        DynamicQuestionForm.base_fields["answer"] = forms.ChoiceField(
            choices=choices, required=required, widget=forms.RadioSelect, label=question.title
        )
    elif question.question_type == "multiple_choice":
        choices = [(str(opt.id), opt.text) for opt in question.options.all().order_by("order")]
        DynamicQuestionForm.base_fields["answer"] = forms.MultipleChoiceField(
            choices=choices, required=required, widget=forms.CheckboxSelectMultiple, label=question.title
        )
    elif question.question_type == "text_input":
        DynamicQuestionForm.base_fields["answer"] = forms.CharField(
            required=required, widget=forms.Textarea(attrs={"rows": 4}), label=question.title
        )
    elif question.question_type == "number_input":
        field_kwargs = {"required": required, "label": question.title}
        if question.number_min is not None:
            field_kwargs["min_value"] = question.number_min
        if question.number_max is not None:
            field_kwargs["max_value"] = question.number_max
        DynamicQuestionForm.base_fields["answer"] = forms.IntegerField(**field_kwargs)

    return DynamicQuestionForm(data)
