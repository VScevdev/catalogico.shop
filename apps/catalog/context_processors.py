from django.conf import settings
from datetime import datetime
import urllib.parse

from apps.core.models import DeveloperConfig
from apps.catalog import cart as cart_helpers


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
        if user and user.is_authenticated and store.owner_id == user.pk:
            is_store_owner = True
        # Colores y logo por tienda (fallback a valores por defecto)
        c = config
        branches = list(store.branches.all()) if config else []
        dev_url = getattr(settings, "DEVELOPER_URL", "")
        dm_url = dev_url
        try:
            dev_cfg = DeveloperConfig.objects.first()
        except Exception:
            dev_cfg = None
        if dev_cfg and dev_url:
            username = dev_url.rstrip("/").rsplit("/", 1)[-1]
            if username and dev_cfg.instagram_message_template:
                encoded = urllib.parse.quote(dev_cfg.instagram_message_template)
                dm_url = f"https://ig.me/m/{username}?text={encoded}"
        return {
            "SITE_NAME": store.name,
            "STORE_ADDRESS": config.address if config else None,
            "STORE_HOURS": config.hours if config else None,
            "STORE_COUNTRY": config.country if config else None,
            "STORE_PROVINCE": config.province if config else None,
            "STORE_CITY": config.city if config else None,
            "STORE_BRANCHES": branches,
            "STORE_LOCATION_URL": config.location_url if config else None,
            "STORE_WHATSAPP": config.whatsapp_number if config else None,
            "STORE_INSTAGRAM": f"https://instagram.com/{config.instagram_username}" if config and config.instagram_username else None,
            "DEVELOPER_NAME": getattr(settings, "DEVELOPER_NAME", ""),
            "DEVELOPER_URL": dev_url,
            "DEVELOPER_DM_URL": dm_url,
            "ROOT_DOMAIN": getattr(settings, "ROOT_DOMAIN", "catalogico.shop"),
            "year": datetime.now().year,
            "current_store": store,
            "is_store_owner": is_store_owner,
            # Colores modo claro
            "STORE_COLOR_BG": c.color_bg if c and c.color_bg else "#ffffff",
            "STORE_COLOR_SURFACE": c.color_surface if c and c.color_surface else "#f8f8f8",
            "STORE_COLOR_SURFACE_SECONDARY": c.color_surface_secondary if c and c.color_surface_secondary else "#f0f0f0",
            "STORE_COLOR_TEXT": c.color_text if c and c.color_text else "#111111",
            "STORE_COLOR_PRIMARY": c.color_primary if c and c.color_primary else "#3483fa",
            "STORE_COLOR_PRIMARY_HOVER": c.color_primary_hover if c and c.color_primary_hover else "#468cf6",
            "STORE_COLOR_BORDER": c.color_border if c and c.color_border else "#e0e0e0",
            "STORE_COLOR_MUTED": c.color_muted if c and c.color_muted else "#6b6b6b",
            # Colores modo oscuro
            "STORE_COLOR_BG_DARK": c.color_bg_dark if c and c.color_bg_dark else "#121212",
            "STORE_COLOR_SURFACE_DARK": c.color_surface_dark if c and c.color_surface_dark else "#1e1e1e",
            "STORE_COLOR_SURFACE_SECONDARY_DARK": c.color_surface_secondary_dark if c and c.color_surface_secondary_dark else "#2a2a2a",
            "STORE_COLOR_TEXT_DARK": c.color_text_dark if c and c.color_text_dark else "#f5f5f5",
            "STORE_COLOR_PRIMARY_DARK": c.color_primary_dark if c and c.color_primary_dark else "#3483fa",
            "STORE_COLOR_PRIMARY_HOVER_DARK": c.color_primary_hover_dark if c and c.color_primary_hover_dark else "#468cf6",
            "STORE_COLOR_BORDER_DARK": c.color_border_dark if c and c.color_border_dark else "#333333",
            "STORE_COLOR_MUTED_DARK": c.color_muted_dark if c and c.color_muted_dark else "#aaaaaa",
            "STORE_LOGO_URL": c.logo.url if c and c.logo else None,
            "cart_count": cart_helpers.cart_count_for_store(request.session, store.id),
        }
    # Landing o sin tienda: valores por defecto (no exponer colores/logo)
    dev_url = getattr(settings, "DEVELOPER_URL", "")
    dm_url = dev_url
    try:
        dev_cfg = DeveloperConfig.objects.first()
    except Exception:
        dev_cfg = None
    if dev_cfg and dev_url:
        username = dev_url.rstrip("/").rsplit("/", 1)[-1]
        if username and dev_cfg.instagram_message_template:
            encoded = urllib.parse.quote(dev_cfg.instagram_message_template)
            dm_url = f"https://ig.me/m/{username}?text={encoded}"

    return {
        "SITE_NAME": getattr(settings, "SITE_NAME", "Catálogo"),
        "STORE_LOGO_URL": None,
        "STORE_ADDRESS": None,
        "STORE_HOURS": None,
        "STORE_BRANCHES": [],
        "STORE_LOCATION_URL": None,
        "STORE_WHATSAPP": None,
        "STORE_INSTAGRAM": None,
        "DEVELOPER_NAME": getattr(settings, "DEVELOPER_NAME", ""),
        "DEVELOPER_URL": dev_url,
        "DEVELOPER_DM_URL": dm_url,
        "ROOT_DOMAIN": getattr(settings, "ROOT_DOMAIN", "catalogico.shop"),
        "year": datetime.now().year,
        "current_store": None,
        "is_store_owner": False,
        "cart_count": 0,
    }