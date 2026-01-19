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
from apps.catalog.models import Category, Product

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
            "is_active",
        ]

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