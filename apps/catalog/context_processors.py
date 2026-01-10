from django.conf import settings
from datetime import datetime

def site_settings(request):
    return {
        "SITE_NAME": getattr(settings, "SITE_NAME", "Catálogo"),
        "STORE_ADDRESS": getattr(settings, "STORE_ADDRESS", None),
        "STORE_HOURS": getattr(settings, "STORE_HOURS", None),
        "STORE_LOCATION_URL": getattr(settings, "STORE_LOCATION_URL", None),
        "STORE_WHATSAPP": getattr(settings, "STORE_WHATSAPP", None),
        "STORE_INSTAGRAM": getattr(settings, "STORE_INSTAGRAM", None),
        "DEVELOPER_NAME": getattr(settings, "DEVELOPER_NAME", ""),
        "DEVELOPER_URL": getattr(settings, "DEVELOPER_URL", ""),
        "year": datetime.now().year,
    }