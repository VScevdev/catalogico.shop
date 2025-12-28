from django.shortcuts import render, get_object_or_404
from .models import Product, Category

# Create your views here.

def catalog_view(request):
    products = Product.objects.filter(is_active=True)
    categories = Category.objects.filter(
        is_active=True
    ).prefetch_related(
        "products__images"
    )

    context = {
        "categories": categories,
        "products": products,
    }
    return render(request, "catalog/catalog.html", context)


def product_detail_view(request, slug):
    product = get_object_or_404(
        Product,
        slug=slug,
        is_active=True
    )

    context = {
        "product": product,
    }
    return render(request, "catalog/product_detail.html", context)