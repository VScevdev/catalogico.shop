from django.contrib import admin
from .models import Category, Product, ProductImage, ProductLink, StoreConfig
from .forms import ProductLinkInlineForm

# Register your models here.


#-- Imagen --#
class ProductImageInline(admin.TabularInline):
    model = ProductImage
    extra = 1
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
        "category",
        "price",
        "is_active",
    )
    list_filter = (
        "category",
        "is_active",
    )
    search_fields = (
        "name",
        "description",
    )
    inlines = [
        ProductImageInline,
        ProductLinkInline,
    ]
    ordering = ("name",)


#-- Categoría --#
@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    exclude = ("slug",)
    
    list_display = (
        "name",
        "is_active",
        "order",
    )
    list_filter = (
        "is_active",
    )
    ordering = ("order", "name")

    @admin.register(StoreConfig)
    class StoreConfigAdmin(admin.ModelAdmin):
        def has_add_permission(self, request):
            return not StoreConfig.objects.exists()