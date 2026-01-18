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
from apps.catalog.models import Category

class CategoryForm(forms.ModelForm):
    class Meta:
        model = Category
        fields = ("name", "slug", "is_active")
