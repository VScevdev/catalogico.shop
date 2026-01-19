from django.contrib import admin
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
        "is_active",
    )
    list_filter = (
        "is_active",
    )
    prepopulated_fields = {"slug": ("name",)}
    ordering = ("name",)

    @admin.register(StoreConfig)
    class StoreConfigAdmin(admin.ModelAdmin):
        def has_add_permission(self, request):
            return not StoreConfig.objects.exists()