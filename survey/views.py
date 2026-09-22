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

    def _get_visible_questions(self, session):
        """Возвращает вопросы, которые нужно показать ИМЕННО этой сессии,
        с учётом условной логики (parent_question / show_only_if_parent_answered).
        Порядок вопроса в этом списке определяет его "step" в навигации."""
        all_questions = list(
            Question.objects.filter(is_active=True)
            .order_by("order")
            .prefetch_related("show_only_if_parent_answered")
        )
        visible = []
        for question in all_questions:
            if question.is_visible_for_session(session):
                visible.append(question)
        return visible

    def _get_display_total(self, session, computed_total):
        """Счётчик "Вопрос X из N" не должен уменьшаться в рамках одной сессии:
        как только условный вопрос стал виден (пользователь ответил родительскому вопросу
        соответствующим образом), N увеличивается и больше не падает обратно,
        даже если пользователь вернётся и поменяет ответ на родительский вопрос."""
        previous_max = session.max_questions_seen or 0
        new_max = max(previous_max, computed_total)
        if new_max != previous_max:
            session.max_questions_seen = new_max
            session.save(update_fields=["max_questions_seen"])
        return new_max

    def get(self, request, session_uuid, step):
        session = get_object_or_404(SurveySession, uuid=session_uuid)
        questions = self._get_visible_questions(session)
        computed_total = len(questions)
        total = self._get_display_total(session, computed_total)
        if step < 1 or step > computed_total:
            return redirect("landing")
        question = questions[step - 1]
        form = build_question_form(question)
        return render(request, self.template_name, self._context(session, question, form, step, total))

    def post(self, request, session_uuid, step):
        session = get_object_or_404(SurveySession, uuid=session_uuid)
        questions = self._get_visible_questions(session)
        computed_total = len(questions)
        question = questions[step - 1]

        if question.question_type == "info_text":
            self._get_display_total(session, computed_total)
            return self._go_next(session, step, computed_total)

        form = build_question_form(question, data=request.POST)
        if not form.is_valid():
            total = self._get_display_total(session, computed_total)
            return render(request, self.template_name, self._context(session, question, form, step, total))

        self._save_answer(session, question, form)

        # После сохранения ответа состав видимых вопросов может измениться
        # (открылись/закрылись зависимые вопросы) — пересчитываем список и
        # ищем новую позицию текущего вопроса, чтобы step оставался консистентным.
        updated_questions = self._get_visible_questions(session)
        updated_total = len(updated_questions)
        self._get_display_total(session, updated_total)
        updated_step = self._resolve_step(updated_questions, question, step, updated_total)
        return self._go_next(session, updated_step, updated_total)

    def _resolve_step(self, questions, current_question, fallback_step, total):
        for index, q in enumerate(questions, start=1):
            if q.pk == current_question.pk:
                return index
        return min(fallback_step, total) if total else fallback_step

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
            "session": session,
            "question": question,
            "form": form,
            "step": step,
            "total": total,
            "progress_percent": round(step / total * 100) if total else 0,
            "is_first": step == 1,
        }


class SurveyContactsView(View):
    template_name = "survey/contacts.html"

    def get(self, request, session_uuid):
        session = get_object_or_404(SurveySession, uuid=session_uuid)
        if session.is_completed:
            return redirect("survey_result", session_uuid=session.uuid)
        site_settings = SiteSettings.load()
        form = ContactForm()
        return render(
            request,
            self.template_name,
            {"form": form, "session": session, "site_settings": site_settings},
        )

    def post(self, request, session_uuid):
        session = get_object_or_404(SurveySession, uuid=session_uuid)
        if session.is_completed:
            return redirect("survey_result", session_uuid=session.uuid)

        site_settings = SiteSettings.load()
        form = ContactForm(request.POST)
        if form.is_valid():
            for field in ["visitor_name", "visitor_company", "visitor_position", "visitor_email", "visitor_phone"]:
                setattr(session, field, form.cleaned_data.get(field))
            # Отправка формы «Получить отчёт» сама означает согласие на обработку ПД
            # (текст согласия и ссылка на политику показаны прямо над кнопкой отправки).
            session.personal_data_consent = True
            session.personal_data_consent_at = timezone.now()
            session.score = calculate_score(session)
            session.is_completed = True
            session.finished_at = timezone.now()
            session.save()
            return redirect("survey_result", session_uuid=session.uuid)

        return render(
            request,
            self.template_name,
            {"form": form, "session": session, "site_settings": site_settings},
        )


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
