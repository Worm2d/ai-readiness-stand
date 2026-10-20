import sys; sys.stdout = open('contacts.txt', 'w', encoding='utf-8')
from survey.models import SurveySession, Answer

for s in SurveySession.objects.filter(is_completed=True).order_by('started_at'):
    print(f"\n{'='*60}")
    print(f"Имя: {s.visitor_name} | Компания: {s.visitor_company} | Должность: {s.visitor_position}")
    print(f"Email: {s.visitor_email} | Телефон: {s.visitor_phone}")
    print(f"Балл: {s.score} | Дата: {s.started_at.strftime('%d.%m.%Y %H:%M')}")
    print("Ответы:")
    for a in s.answers.select_related('question').prefetch_related('selected_options').order_by('question__order'):
        opts = ', '.join(o.text for o in a.selected_options.all())
        val = opts or a.text_value or str(a.number_value or '')
        print(f"  {a.question.title[:50]}: {val}")
sys.stdout.close()
