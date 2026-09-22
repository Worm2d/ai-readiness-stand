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

    def _get_all_questions(self):
        """Полный список активных вопросов в порядке показа. Это ФИКСИРОВАНный
        список: именно по нему считается "step" в URL и общий "total" в счётчике
        прогресса, независимо от того, видны ли конкретной сессии условные вопросы."""
        return list(
            Question.objects.filter(is_active=True)
            .order_by("order")
            .prefetch_related("show_only_if_parent_answered")
        )

    def _get_visible_questions(self, session, all_questions=None):
        """Подмножество all_questions, которые нужно реально показать ИМЕННО
        этой сессии, с учётом условной логики (parent_question /
        show_only_if_parent_answered)."""
        all_questions = all_questions if all_questions is not None else self._get_all_questions()
        return [q for q in all_questions if q.is_visible_for_session(session)]

    def _resolve_step_to_question(self, all_questions, visible_questions, step):
        """Находит вопрос для данного step. step всегда — позиция в ПОЛНОМ
        списке активных вопросов (all_questions), но если вопрос под этим
        step скрыт условной логикой для сессии, мы идём вперёд/назад по
        all_questions до первого видимого вопроса — так реализуются "перескоки"."""
        if step < 1 or step > len(all_questions):
            return None, None

        visible_ids = {q.pk for q in visible_questions}
        index = step - 1

        if all_questions[index].pk in visible_ids:
            return all_questions[index], step

        for i in range(index, len(all_questions)):
            if all_questions[i].pk in visible_ids:
                return all_questions[i], i + 1

        for i in range(index, -1, -1):
            if all_questions[i].pk in visible_ids:
                return all_questions[i], i + 1

        return None, None

    def get(self, request, session_uuid, step):
        session = get_object_or_404(SurveySession, uuid=session_uuid)
        all_questions = self._get_all_questions()
        total = len(all_questions)
        visible_questions = self._get_visible_questions(session, all_questions)

        question, resolved_step = self._resolve_step_to_question(all_questions, visible_questions, step)
        if question is None:
            return redirect("landing")
        if resolved_step != step:
            return redirect("survey_question", session_uuid=session.uuid, step=resolved_step)

        form = build_question_form(question)
        return render(request, self.template_name, self._context(session, question, form, resolved_step, total))

    def post(self, request, session_uuid, step):
        session = get_object_or_404(SurveySession, uuid=session_uuid)
        all_questions = self._get_all_questions()
        total = len(all_questions)
        visible_questions = self._get_visible_questions(session, all_questions)

        question, resolved_step = self._resolve_step_to_question(all_questions, visible_questions, step)
        if question is None:
            return redirect("landing")

        if question.question_type == "info_text":
            return self._go_next(session, all_questions, resolved_step, total)

        form = build_question_form(question, data=request.POST)
        if not form.is_valid():
            return render(request, self.template_name, self._context(session, question, form, resolved_step, total))

        self._save_answer(session, question, form)

        # После сохранения ответа состав видимых вопросов может измениться
        # (открылись/закрылись зависимые вопросы), но total и нумерация step
        # всегда считаются по полному списку all_questions — поэтому "Вопрос X
        # из N" стабилен, а переходы просто перескакивают скрытые вопросы.
        return self._go_next(session, all_questions, resolved_step, total)

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

    def _go_next(self, session, all_questions, step, total):
        """Ищет следующий видимый вопрос начиная со step+1 по полному списку
        all_questions (пересчитанному без кэша видимости — after-save состояние
        уже отражает только что сохранённый ответ)."""
        for next_step in range(step + 1, total + 1):
            candidate = all_questions[next_step - 1]
            if candidate.is_visible_for_session(session):
                return redirect("survey_question", session_uuid=session.uuid, step=next_step)
        return self._finish_survey(session)

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
