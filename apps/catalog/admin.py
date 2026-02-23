from django.contrib import admin
from django.utils.safestring import mark_safe
from django.conf import settings
from .models import Category, Product, ProductMedia, ProductLink, StoreConfig, Branch, FAQ, Tutorial, StoreFeedback
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
    list_display = (
        "name",
        "store",
        "category",
        "price",
        "stock",
        "status",
    )
    list_filter = (
        "store",
        "category",
        "status",
    )
    search_fields = ("name", "description",)
    exclude = ("slug",)
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


# -- FAQ --#
@admin.register(FAQ)
class FAQAdmin(admin.ModelAdmin):
    list_display = ("question_short", "store", "order", "is_active")
    list_filter = ("store", "is_active")
    search_fields = ("question", "answer")
    ordering = ("store", "order")

    def question_short(self, obj):
        return obj.question[:60] + ("..." if len(obj.question) > 60 else "")

    question_short.short_description = "Pregunta"


# -- Tutorial --#
@admin.register(Tutorial)
class TutorialAdmin(admin.ModelAdmin):
    list_display = ("title", "order", "is_active")
    list_filter = ("is_active",)
    search_fields = ("title", "description")
    ordering = ("order",)


# -- StoreFeedback (quejas/propuestas) --#
@admin.register(StoreFeedback)
class StoreFeedbackAdmin(admin.ModelAdmin):
    list_display = ("store", "feedback_type", "author_email", "is_read", "created_at")
    list_filter = ("store", "feedback_type", "is_read")
    search_fields = ("author_name", "author_email", "message")
    ordering = ("-created_at",)
    readonly_fields = ("created_at",)


#-- Branch --#
@admin.register(Branch)
class BranchAdmin(admin.ModelAdmin):
    list_display = ("store", "city", "province", "country", "address")
    list_filter = ("store",)
    ordering = ("store", "id")


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
        ("Ubicación", {"fields": ("country", "province", "city", "address", "hours", "location_url")}),
        ("Botones por defecto", {"fields": ("default_link_whatsapp", "default_link_instagram", "default_link_facebook", "default_link_mercadolibre")}),
        ("Contacto", {"fields": ("whatsapp_number", "instagram_username", "facebook_page", "mercadolibre_store")}),
        ("Mensajes", {"fields": ("whatsapp_message_template", "order_message_template")}),
    )

    def logo_preview(self, obj):
        if obj and obj.logo:
            url = obj.logo.url
            return mark_safe(f'<img src="{url}" alt="Logo" style="max-height: 40px; max-width: 60px; object-fit: contain;">')
        return "—"

    logo_preview.short_description = "Logo"