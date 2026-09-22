"""Шаблонные фильтры приложения core."""
import re

from django import template
from django.utils.html import escape
from django.utils.safestring import mark_safe

register = template.Library()


@register.filter(name="linkify_company")
def linkify_company(text, site_settings):
    """Оборачивает в ссылку на company_website первое найденное в тексте
    вхождение полного названия компании или его короткого варианта "ICL СТ"
    (без учёта регистра, с сохранением исходного регистра найденного текста).
    Используется в футере, где название компании — часть свободного текста,
    а не отдельная переменная."""
    if not text:
        return text

    website = getattr(site_settings, "company_website", "") or ""
    company_name = getattr(site_settings, "company_name", "") or ""
    if not website:
        return text

    safe_text = escape(text)
    candidates = [c for c in {company_name, "ICL СТ"} if c]
    candidates.sort(key=len, reverse=True)

    result = safe_text
    replaced = False
    for phrase in candidates:
        if replaced:
            break
        pattern = re.compile(re.escape(escape(phrase)), re.IGNORECASE)

        def repl(match):
            return (
                f'<a href="{escape(website)}" target="_blank" rel="noopener" '
                f'style="color: inherit; text-decoration: underline;">{match.group(0)}</a>'
            )

        new_result, count = pattern.subn(repl, result, count=1)
        if count:
            result = new_result
            replaced = True

    return mark_safe(result)
