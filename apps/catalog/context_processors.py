from django.conf import settings
from datetime import datetime


def site_settings(request):
    """Contexto de tienda: usa request.store si existe, sino fallback a settings."""
    store = getattr(request, "store", None)
    config = None
    if store:
        try:
            config = store.config
        except Exception:
            pass

    if store:
        is_store_owner = False
        user = getattr(request, "user", None)
        if user and user.is_authenticated and hasattr(user, "store") and user.store_id == store.id:
            is_store_owner = True
        return {
            "SITE_NAME": store.name,
            "STORE_ADDRESS": config.address if config else None,
            "STORE_HOURS": config.hours if config else None,
            "STORE_LOCATION_URL": config.location_url if config else None,
            "STORE_WHATSAPP": config.whatsapp_number if config else None,
            "STORE_INSTAGRAM": f"https://instagram.com/{config.instagram_username}" if config and config.instagram_username else None,
            "DEVELOPER_NAME": getattr(settings, "DEVELOPER_NAME", ""),
            "DEVELOPER_URL": getattr(settings, "DEVELOPER_URL", ""),
            "ROOT_DOMAIN": getattr(settings, "ROOT_DOMAIN", "catalogico.shop"),
            "year": datetime.now().year,
            "current_store": store,
            "is_store_owner": is_store_owner,
        }
    # Landing o sin tienda: valores por defecto
    return {
        "SITE_NAME": getattr(settings, "SITE_NAME", "Catálogo"),
        "STORE_ADDRESS": None,
        "STORE_HOURS": None,
        "STORE_LOCATION_URL": None,
        "STORE_WHATSAPP": None,
        "STORE_INSTAGRAM": None,
        "DEVELOPER_NAME": getattr(settings, "DEVELOPER_NAME", ""),
        "DEVELOPER_URL": getattr(settings, "DEVELOPER_URL", ""),
        "ROOT_DOMAIN": getattr(settings, "ROOT_DOMAIN", "catalogico.shop"),
        "year": datetime.now().year,
        "current_store": None,
        "is_store_owner": False,
    }