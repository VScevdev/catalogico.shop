from django.conf import settings
from datetime import datetime

def site_settings(request):
    return {
        "SITE_NAME": getattr(settings, "SITE_NAME", "Catálogo"),
        "year": datetime.now().year,
    }