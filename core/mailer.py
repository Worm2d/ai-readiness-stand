"""Отправка письма с отчётом на почту посетителя.

Отправка должна быть максимально "тихой": если SMTP не настроен, недоступен
или письмо по любой причине не отправилось — это не должно ломать основной
сценарий (показ отчёта пользователю). Все ошибки логируются и подавляются.
"""
import logging

from django.core.mail import send_mail

from .models import SiteSettings

logger = logging.getLogger(__name__)


def _render_email_body(template, session, report_url, site_settings):
    visitor_name = (session.visitor_name or "").strip() or "Уважаемый клиент"
    try:
        return template.format(
            visitor_name=visitor_name,
            report_url=report_url,
            company_name=site_settings.company_name,
            company_email=site_settings.company_email,
            company_website=site_settings.company_website,
        )
    except (KeyError, IndexError, ValueError):
        # Если в шаблоне опечатка в имени плейсхолдера — не роняем отправку,
        # используем текст как есть (без подстановки), лучше отправить
        # неидеальное письмо, чем не отправить вовсе.
        logger.warning("Некорректный плейсхолдер в email_body_template, письмо отправлено без подстановки.")
        return template


def send_report_email(session, report_url):
    """Отправляет письмо с отчётом на session.visitor_email, если оно указано.
    Любая ошибка (нет SMTP-настроек, сбой соединения, некорректный адрес и т.п.)
    перехватывается и логируется, но никогда не прерывает выполнение запроса."""
    if not session.visitor_email:
        return False

    try:
        site_settings = SiteSettings.load()
        subject = (site_settings.email_subject or "").strip() or "Ваш отчёт готов"
        body = _render_email_body(site_settings.email_body_template or "", session, report_url, site_settings)

        send_mail(
            subject=subject,
            message=body,
            from_email=None,
            recipient_list=[session.visitor_email],
            fail_silently=False,
        )
        return True
    except Exception:
        logger.exception("Не удалось отправить письмо с отчётом на %s", session.visitor_email)
        return False
