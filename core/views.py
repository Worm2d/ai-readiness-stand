"""Views приложения core: стартовая страница стенда."""
from django.views.generic import TemplateView

from .models import SiteSettings


class LandingView(TemplateView):
    template_name = "core/landing.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["settings"] = SiteSettings.load()
        return context
