"""Views приложения survey: прохождение опроса от старта до результата."""
from django.shortcuts import get_object_or_404, redirect, render
from django.urls import reverse
from django.utils import timezone
from django.views import View

from core.models import SiteSettings

from .forms import ContactForm, build_question_form
from .models import Answer, AnswerOption, Question, SurveySession
from .scoring import calculate_score


class SurveyStartView(View):
    def get(self, request):
        session = SurveySession.objects.create()
        return redirect("survey_question", session_uuid=session.uuid, step=1)


class SurveyQuestionView(View):
    template_name = "survey/question.html"

    def _get_ordered_questions(self):
        return list(Question.objects.filter(is_active=True).order_by("order"))

    def get(self, request, session_uuid, step):
        session = get_object_or_404(SurveySession, uuid=session_uuid)
        questions = self._get_ordered_questions()
        total = len(questions)
        if step < 1 or step > total:
            return redirect("landing")
        question = questions[step - 1]
        form = build_question_form(question)
        return render(request, self.template_name, self._context(session, question, form, step, total))

    def post(self, request, session_uuid, step):
        session = get_object_or_404(SurveySession, uuid=session_uuid)
        questions = self._get_ordered_questions()
        total = len(questions)
        question = questions[step - 1]

        if question.question_type == "info_text":
            return self._go_next(session, step, total)

        form = build_question_form(question, data=request.POST)
        if not form.is_valid():
            return render(request, self.template_name, self._context(session, question, form, step, total))

        self._save_answer(session, question, form)
        return self._go_next(session, step, total)

    def _save_answer(self, session, question, form):
        answer, _ = Answer.objects.get_or_create(session=session, question=question)
        value = form.cleaned_data.get("answer")
        answer.selected_options.clear()
        answer.text_value = None
        answer.number_value = None

        if question.question_type == "single_choice" and value:
            answer.selected_options.add(AnswerOption.objects.get(id=value))
        elif question.question_type == "multiple_choice" and value:
            answer.selected_options.add(*AnswerOption.objects.filter(id__in=value))
        elif question.question_type == "text_input":
            answer.text_value = value
        elif question.question_type == "number_input":
            answer.number_value = value

        answer.save()

    def _go_next(self, session, step, total):
        if step >= total:
            return self._finish_survey(session)
        return redirect("survey_question", session_uuid=session.uuid, step=step + 1)

    def _finish_survey(self, session):
        site_settings = SiteSettings.load()
        if site_settings.collect_personal_data and not session.is_completed:
            return redirect("survey_contacts", session_uuid=session.uuid)
        return self._complete_and_redirect(session)

    def _complete_and_redirect(self, session):
        if not session.is_completed:
            session.score = calculate_score(session)
            session.is_completed = True
            session.finished_at = timezone.now()
            session.save()
        return redirect("survey_result", session_uuid=session.uuid)

    def _context(self, session, question, form, step, total):
        return {
            "session": session, "question": question, "form": form,
            "step": step, "total": total,
            "progress_percent": round(step / total * 100) if total else 0,
            "is_first": step == 1,
        }


class SurveyContactsView(View):
    template_name = "survey/contacts.html"

    def get(self, request, session_uuid):
        session = get_object_or_404(SurveySession, uuid=session_uuid)
        if session.is_completed:
            return redirect("survey_result", session_uuid=session.uuid)
        form = ContactForm()
        return render(request, self.template_name, {"form": form, "session": session})

    def post(self, request, session_uuid):
        session = get_object_or_404(SurveySession, uuid=session_uuid)
        form = ContactForm(request.POST)
        if form.is_valid():
            for field in ["visitor_name", "visitor_company", "visitor_position", "visitor_email", "visitor_phone"]:
                setattr(session, field, form.cleaned_data.get(field))
            session.score = calculate_score(session)
            session.is_completed = True
            session.finished_at = timezone.now()
            session.save()
            return redirect("survey_result", session_uuid=session.uuid)
        return render(request, self.template_name, {"form": form, "session": session})


class SurveyResultView(View):
    template_name = "survey/result.html"

    def get(self, request, session_uuid):
        from risks.scoring_view_helpers import build_report_context
        from survey.qr import make_qr_data_uri

        session = get_object_or_404(SurveySession, uuid=session_uuid)
        if not session.is_completed:
            return redirect("survey_question", session_uuid=session.uuid, step=1)

        context = build_report_context(session)
        report_url = request.build_absolute_uri(reverse("report", args=[session.uuid]))
        context["report_qr"] = make_qr_data_uri(report_url)
        context["report_url"] = report_url
        return render(request, self.template_name, context)
