"""Context processor, добавляющий SiteSettings во все шаблоны."""
from .models import SiteSettings


def site_settings(request):
    return {"site_settings": SiteSettings.load()}
