from django.contrib import admin
from django.utils.safestring import mark_safe
from django.conf import settings
from .models import Category, Product, ProductMedia, ProductLink, StoreConfig
from .forms import ProductLinkInlineForm

# Register your models here.


#-- Imagen --#
class ProductMediaInline(admin.TabularInline):
    model = ProductMedia
    extra = 0
    ordering = ("order",)


#-- Link --#
class ProductLinkInline(admin.TabularInline):
    model = ProductLink
    form = ProductLinkInlineForm
    extra = 1

#-- Producto --#
@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    list_display = ("name", "price", "is_active")
    list_filter = ("is_active", "category")
    search_fields = ("name",)
    exclude = ("slug",)

    list_display = (
        "name",
        "store",
        "category",
        "price",
        "is_active",
    )
    list_filter = (
        "store",
        "category",
        "is_active",
    )
    search_fields = (
        "name",
        "description",
    )
    inlines = [
        ProductMediaInline,
        ProductLinkInline,
    ]
    ordering = ("name",)


#-- Categoría --#
@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = (
        "name",
        "slug",
        "store",
        "is_active",
    )
    list_filter = (
        "store",
        "is_active",
    )
    prepopulated_fields = {"slug": ("name",)}
    ordering = ("name",)


#-- StoreConfig --#
@admin.register(StoreConfig)
class StoreConfigAdmin(admin.ModelAdmin):
    list_display = ("store", "logo_preview", "address", "whatsapp_number", "instagram_username")
    list_filter = ("store",)
    search_fields = ("store__name",)
    fieldsets = (
        (None, {"fields": ("store",)}),
        ("Logo", {"fields": ("logo",)}),
        ("Modo claro", {
            "fields": (
                "color_bg", "color_surface", "color_surface_secondary", "color_text",
                "color_primary", "color_primary_hover",
                "color_border", "color_muted",
            ),
        }),
        ("Modo oscuro", {
            "fields": (
                "color_bg_dark", "color_surface_dark", "color_surface_secondary_dark", "color_text_dark",
                "color_primary_dark", "color_primary_hover_dark",
                "color_border_dark", "color_muted_dark",
            ),
        }),
        ("Ubicación", {"fields": ("address", "hours", "location_url")}),
        ("Contacto", {"fields": ("whatsapp_number", "instagram_username", "facebook_page", "mercadolibre_store")}),
        ("WhatsApp", {"fields": ("whatsapp_message_template",)}),
    )

    def logo_preview(self, obj):
        if obj and obj.logo:
            url = obj.logo.url
            return mark_safe(f'<img src="{url}" alt="Logo" style="max-height: 40px; max-width: 60px; object-fit: contain;">')
        return "—"

    logo_preview.short_description = "Logo"