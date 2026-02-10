from django.contrib import admin
from django.urls import reverse
from django.utils.html import format_html
from .models import Store, DeveloperConfig


@admin.register(Store)
class StoreAdmin(admin.ModelAdmin):
    list_display = ("name", "slug", "owner", "apariencia_link", "is_active", "created_at")
    list_filter = ("is_active",)
    search_fields = ("name", "slug")

    def apariencia_link(self, obj):
        try:
            config = obj.config
            url = reverse("admin:catalog_storeconfig_change", args=[config.pk])
            return format_html('<a href="{}">Editar apariencia</a>', url)
        except Exception:
            return "—"

    apariencia_link.short_description = "Apariencia"


@admin.register(DeveloperConfig)
class DeveloperConfigAdmin(admin.ModelAdmin):
    list_display = ("id",)
