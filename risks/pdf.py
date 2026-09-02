"""Генерация PDF-версии отчёта (WeasyPrint основной, reportlab fallback)."""
from django.conf import settings
from django.template.loader import render_to_string


def render_report_pdf(context: dict) -> bytes:
    if settings.PDF_ENGINE == "weasyprint":
        try:
            return _render_with_weasyprint(context)
        except Exception:
            return _render_with_reportlab(context)
    return _render_with_reportlab(context)


def _render_with_weasyprint(context: dict) -> bytes:
    from weasyprint import HTML

    html_string = render_to_string("report/report_pdf.html", context)
    return HTML(string=html_string, base_url=settings.SITE_BASE_URL).write_pdf()


def _render_with_reportlab(context: dict) -> bytes:
    from io import BytesIO

    from reportlab.lib import colors
    from reportlab.lib.enums import TA_LEFT
    from reportlab.lib.pagesizes import A4
    from reportlab.lib.styles import ParagraphStyle, getSampleStyleSheet
    from reportlab.lib.units import mm
    from reportlab.platypus import Paragraph, SimpleDocTemplate, Spacer, Table, TableStyle

    buffer = BytesIO()
    doc = SimpleDocTemplate(buffer, pagesize=A4, leftMargin=18*mm, rightMargin=18*mm, topMargin=16*mm, bottomMargin=16*mm)
    styles = getSampleStyleSheet()
    primary_color = colors.HexColor(context.get("primary_color", "#E30613"))

    title_style = ParagraphStyle("TitleRed", parent=styles["Title"], textColor=primary_color, alignment=TA_LEFT)
    h2_style = ParagraphStyle("H2Red", parent=styles["Heading2"], textColor=primary_color, spaceBefore=14)
    body_style = styles["BodyText"]
    small_style = ParagraphStyle("Small", parent=styles["BodyText"], fontSize=8, textColor=colors.grey)

    story = []
    settings_obj = context["site_settings"]
    session = context["session"]

    story.append(Paragraph(settings_obj.company_name, small_style))
    story.append(Paragraph(context.get("result_title", "Персональный отчёт"), title_style))
    story.append(Spacer(1, 6))

    greeting = f"Здравствуйте, {session.visitor_name}!" if session.visitor_name else "Здравствуйте!"
    story.append(Paragraph(greeting, body_style))
    story.append(Spacer(1, 10))

    score = context.get("score")
    interpretation = context.get("interpretation")
    if score is not None:
        story.append(Paragraph(f"Уровень зрелости ИБ в контексте ИИ: <b>{score}/100</b>", h2_style))
        if interpretation:
            story.append(Paragraph(f"<b>{interpretation.title}</b>", body_style))
            story.append(Paragraph(interpretation.description, body_style))
        story.append(Spacer(1, 8))

    story.append(Paragraph("Выявленные риски", h2_style))
    for risk in context.get("risks", []):
        cats = ", ".join(c.name for c in risk.categories.all())
        story.append(Paragraph(f"<b>{risk.title}</b> ({risk.get_severity_display()}, {cats})", body_style))
        story.append(Paragraph(risk.description, body_style))
        if risk.public_case_description:
            story.append(Paragraph(f"<i>Кейс: {risk.public_case_description}</i>", small_style))
        story.append(Spacer(1, 6))

    story.append(Paragraph("Рекомендации", h2_style))
    for rec in context.get("recommendations", []):
        story.append(Paragraph(f"• <b>{rec.title}</b> — {rec.description}", body_style))
    story.append(Spacer(1, 8))

    story.append(Paragraph("Услуги ICL Системные технологии", h2_style))
    data = [["Услуга", "Описание", "Ссылка"]]
    for service in context.get("services", []):
        data.append([service.title, service.short_description, service.url])
    if len(data) > 1:
        table = Table(data, colWidths=[110, 260, 100])
        table.setStyle(TableStyle([
            ("BACKGROUND", (0, 0), (-1, 0), primary_color),
            ("TEXTCOLOR", (0, 0), (-1, 0), colors.white),
            ("FONTSIZE", (0, 0), (-1, -1), 8),
            ("GRID", (0, 0), (-1, -1), 0.5, colors.lightgrey),
            ("VALIGN", (0, 0), (-1, -1), "TOP"),
        ]))
        story.append(table)

    story.append(Spacer(1, 14))
    story.append(Paragraph(f"{settings_obj.company_name} · {settings_obj.company_website} · {settings_obj.company_email}", small_style))

    doc.build(story)
    return buffer.getvalue()
