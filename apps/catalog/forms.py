from django import forms
from .models import ProductLink, Category

class ProductLinkInlineForm(forms.ModelForm):
    class Meta:
        model = ProductLink
        fields = "__all__"

    def clean(self):
        cleaned = super().clean()

        link_type = cleaned.get("link_type")
        url = cleaned.get("url")
        text = cleaned.get("button_text")

        if link_type == "external":
            if not url:
                self.add_error("url", "Obligatorio para links externos.")
            if not text:
                self.add_error("button_text", "Obligatorio para links externos.")
        else:
            cleaned["url"] = ""
            cleaned["button_text"] = ""

        return cleaned

from django import forms
import urllib.parse

from apps.catalog.models import Category, Product, StoreConfig, Branch
from apps.catalog.widgets import StoreConfigLogoInput


class StoreConfigForm(forms.ModelForm):
    """Formulario de apariencia de la tienda (colores y logo)."""

    class Meta:
        model = StoreConfig
        fields = [
            "logo",
            "color_bg",
            "color_surface",
            "color_surface_secondary",
            "color_text",
            "color_primary", "color_primary_hover",
            "color_border", "color_muted",
            "color_bg_dark", "color_surface_dark", "color_surface_secondary_dark", "color_text_dark",
            "color_primary_dark", "color_primary_hover_dark",
            "color_border_dark", "color_muted_dark",
        ]
        widgets = {
            "logo": StoreConfigLogoInput(),
            "color_bg": forms.TextInput(attrs={"type": "color", "class": "store-config-color"}),
            "color_surface": forms.TextInput(attrs={"type": "color", "class": "store-config-color"}),
            "color_surface_secondary": forms.TextInput(attrs={"type": "color", "class": "store-config-color"}),
            "color_text": forms.TextInput(attrs={"type": "color", "class": "store-config-color"}),
            "color_primary": forms.TextInput(attrs={"type": "color", "class": "store-config-color"}),
            "color_primary_hover": forms.TextInput(attrs={"type": "color", "class": "store-config-color"}),
            "color_border": forms.TextInput(attrs={"type": "color", "class": "store-config-color"}),
            "color_muted": forms.TextInput(attrs={"type": "color", "class": "store-config-color"}),
            "color_bg_dark": forms.TextInput(attrs={"type": "color", "class": "store-config-color"}),
            "color_surface_dark": forms.TextInput(attrs={"type": "color", "class": "store-config-color"}),
            "color_surface_secondary_dark": forms.TextInput(attrs={"type": "color", "class": "store-config-color"}),
            "color_text_dark": forms.TextInput(attrs={"type": "color", "class": "store-config-color"}),
            "color_primary_dark": forms.TextInput(attrs={"type": "color", "class": "store-config-color"}),
            "color_primary_hover_dark": forms.TextInput(attrs={"type": "color", "class": "store-config-color"}),
            "color_border_dark": forms.TextInput(attrs={"type": "color", "class": "store-config-color"}),
            "color_muted_dark": forms.TextInput(attrs={"type": "color", "class": "store-config-color"}),
        }


class StoreInfoContactForm(forms.ModelForm):
    """Formulario de información y contacto de la tienda."""

    class Meta:
        model = StoreConfig
        fields = [
            "country",
            "province",
            "city",
            "address",
            "hours",
            "location_url",
            "whatsapp_number",
            "instagram_username",
            "facebook_page",
            "mercadolibre_store",
            "default_link_whatsapp",
            "default_link_instagram",
            "default_link_facebook",
            "default_link_mercadolibre",
        ]
        widgets = {
            "default_link_whatsapp": forms.CheckboxInput(),
            "default_link_instagram": forms.CheckboxInput(),
            "default_link_facebook": forms.CheckboxInput(),
            "default_link_mercadolibre": forms.CheckboxInput(),
        }


class StoreCustomMessagesForm(forms.ModelForm):
    """Formulario solo para mensajes personalizados (producto y carrito)."""

    class Meta:
        model = StoreConfig
        fields = ["whatsapp_message_template", "order_message_template"]
        widgets = {
            "whatsapp_message_template": forms.Textarea(attrs={"rows": 4}),
            "order_message_template": forms.Textarea(attrs={"rows": 4}),
        }

    def clean(self):
        cleaned = super().clean()
        location_url = cleaned.get("location_url") or ""
        address = cleaned.get("address") or ""
        city = cleaned.get("city") or ""
        province = cleaned.get("province") or ""
        country = cleaned.get("country") or ""

        if not location_url:
            parts = [p for p in [address, city, province, country] if p]
            if parts:
                query = ", ".join(parts)
                encoded = urllib.parse.quote_plus(query)
                cleaned["location_url"] = f"https://www.google.com/maps/search/?api=1&query={encoded}"

        return cleaned


class BranchForm(forms.ModelForm):
    class Meta:
        model = Branch
        fields = ("country", "province", "city", "address", "hours", "location_url")

    def clean(self):
        cleaned = super().clean()
        location_url = cleaned.get("location_url") or ""
        address = cleaned.get("address") or ""
        city = cleaned.get("city") or ""
        province = cleaned.get("province") or ""
        country = cleaned.get("country") or ""

        if not location_url:
            parts = [p for p in [address, city, province, country] if p]
            if parts:
                query = ", ".join(parts)
                encoded = urllib.parse.quote_plus(query)
                cleaned["location_url"] = f"https://www.google.com/maps/search/?api=1&query={encoded}"

        return cleaned


class CategoryForm(forms.ModelForm):
    class Meta:
        model = Category
        fields = ("name", "is_active")

class ProductForm(forms.ModelForm):
    class Meta:
        model = Product
        fields = [
            "name",
            "category",
            "description",
            "price",
        ]

    def __init__(self, *args, store=None, **kwargs):
        super().__init__(*args, **kwargs)
        if store:
            self.fields["category"].queryset = Category.objects.filter(store=store)
        elif self.instance and self.instance.store_id:
            self.fields["category"].queryset = Category.objects.filter(store=self.instance.store)

    def clean(self):
        cleaned = super().clean()

        product = self.instance
        publishing = product.status == Product.Status.PUBLISHED

        if publishing:
            errors = {}

            if not cleaned.get("name"):
                errors["name"] = "El nombre es obligatorio."

            if not cleaned.get("price"):
                errors["price"] = "El precio es obligatorio."

            if not cleaned.get("category"):
                errors["category"] = "La categoría es obligatoria."

            if product.pk and not product.media.filter(
                media_type="image"
            ).exists():
                raise forms.ValidationError(
                    "El producto debe tener al menos una imagen."
                )

            if errors:
                raise forms.ValidationError(errors)

        return cleaned