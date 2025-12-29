from django.shortcuts import render, get_object_or_404
from django.db.models import Count, Q
from django.db.models.functions import Lower
from django.core.paginator import Paginator
from urllib.parse import urlencode
from .models import Product, Category
from .constants import SORT_LABELS

# Create your views here.

def catalog_view(request):
    q = request.GET.get("q")
    sort = request.GET.get("sort", "newest")
    selected_categories = request.GET.getlist("category")

    has_filters = bool(
        selected_categories
        or sort not in ("newest", None)
    )

    products = Product.objects.filter(is_active=True)

    if selected_categories:
        products = products.filter(category__slug__in=selected_categories)

    if q:
        products = products.filter(name__icontains=q)

    if sort == "newest":
        products = products.order_by("-created_at")

    sort_map = {
        "newest" : "-created_at",
        "az": Lower("name"),
        "za": Lower("name").desc(),
        "price_asc": "price",
        "price_desc": "-price",
    }

    products = products.order_by(sort_map.get(sort, Lower("name")))

    category_base_qs = Product.objects.filter(is_active=True)
    
    if q:
        category_base_qs = category_base_qs.filter(name__icontains=q)
    
    categories = Category.objects.filter(is_active=True).annotate(
        product_count=Count(
            "products",
            filter=Q(products__in=category_base_qs)
        )
    )

    active_filters = []

    # base params actuales
    base_params = request.GET.copy()

    # --- categorías ---
    for slug in selected_categories:
        params = base_params.copy()   # 👈 ESTO FALTABA

        cats = params.getlist("category")
        cats.remove(slug)

        if cats:
            params.setlist("category", cats)
        else:
            params.pop("category", None)

        active_filters.append({
            "type": "category",
            "label": slug.replace("-", " ").title(),
            "url": "?" + params.urlencode(),
        })

    # --- búsqueda ---
    if q:
        params = base_params.copy()
        params.pop("q", None)

        active_filters.append({
            "type": "search",
            "label": f'Búsqueda: "{q}"',
            "url": "?" + params.urlencode(),
        })

    category_links = []

    for category in categories:
        params = request.GET.copy()
        cats = params.getlist("category")

        if category.slug in cats:
            cats.remove(category.slug)
        else:
            cats.append(category.slug)

        if cats:
            params.setlist("category", cats)
        else:
            params.pop("category", None)

        category_links.append({
            "category": category,
            "url": "?" + params.urlencode(),
            "is_active": category.slug in selected_categories,
        })


    # --- sort ---
    if sort and sort != "newest":
        params = base_params.copy()
        params.pop("sort", None)

        active_filters.append({
            "type": "sort",
            "label": SORT_LABELS.get(sort, sort),
            "url": "?" + params.urlencode(),
        })

    return render(request, "catalog/catalog.html", {
        "products": products,
        "categories": categories,
        "sort": sort,
        "sort_labels": SORT_LABELS,
        "q": q,
        "selected_categories": selected_categories,
        "has_filters": has_filters,
        "active_filters": active_filters,
        "category_links": category_links,
    })


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