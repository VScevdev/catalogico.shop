from django.shortcuts import render, get_object_or_404, redirect
from django.templatetags.static import static
from django.contrib import messages
from django.conf import settings
from django.urls import reverse
from django.http import HttpResponse, HttpResponseNotAllowed
from django.contrib.auth.decorators import login_required
from apps.accounts.decorators import owner_required
from django.db.models import Count, Q
from django.db.models.functions import Lower
from django.core.paginator import Paginator
from django.core.files.storage import default_storage
from urllib.parse import urlencode
from .models import Product, Category, ProductMedia, ProductLink, StoreConfig, Branch
from .forms import CategoryForm, ProductForm, StoreConfigForm, StoreInfoContactForm, BranchForm
from .constants import SORT_LABELS

import sys

# Create your views here.

def _landing_context(request):
    """Contexto para la vista landing (selector de tiendas)."""
    from django.conf import settings as django_settings
    from apps.core.models import Store
    stores = list(Store.objects.filter(is_active=True).order_by("name"))
    root = getattr(django_settings, "ROOT_DOMAIN", "catalogico.shop")
    port = ""
    host = request.get_host()
    if ":" in host:
        port = ":" + host.split(":")[-1]
    for s in stores:
        s.landing_url = f"{request.scheme}://{s.slug}.{root}{port}/"
    return {"stores": stores}


def catalog_view(request):
    if not getattr(request, "store", None):
        return render(request, "catalog/landing.html", _landing_context(request))

    request.session["catalog_return_url"] = request.get_full_path()
    store = request.store

    q = request.GET.get("q")
    sort = request.GET.get("sort", "newest")
    selected_categories = request.GET.getlist("category")

    has_filters = bool(
        selected_categories
        or sort not in ("newest", None)
    )

    products = Product.objects.filter(store=store, status=Product.Status.PUBLISHED)

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

    # --- PAGINACIÓN ---
    paginator = Paginator(products, 12)  # 10 productos por página
    page_number = request.GET.get("page")
    page_obj = paginator.get_page(page_number)

    category_base_qs = Product.objects.filter(store=store, status=Product.Status.PUBLISHED)
    
    if q:
        category_base_qs = category_base_qs.filter(name__icontains=q)
    
    categories = Category.objects.filter(store=store, is_active=True).annotate(
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
        "products": page_obj,
        "page_obj": page_obj,
        "paginator": paginator,
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
    store = getattr(request, "store", None)
    if not store:
        return render(request, "catalog/landing.html", _landing_context(request))

    product = get_object_or_404(
        Product,
        store=store,
        slug=slug,
        status=Product.Status.PUBLISHED,
    )

    context = {
        "product": product,
        "media_items": product.media.filter(is_active=True).order_by("order", "id"),
        "links": product.links.all().order_by("order", "id"),
        "has_links": product.links.exists(),
        "catalog_url": reverse("catalog:catalog"), #FallBack
    }
    return render(request, "catalog/product_detail.html", context)

def privacy_view(request):
    return render(request, "extra/privacy.html")


def landing_view(request):
    """Vista para dominio raíz (catalogico.shop) - selector de tiendas."""
    return render(request, "catalog/landing.html", _landing_context(request))

@login_required
@owner_required
def category_list_view(request):
    categories = Category.objects.filter(store=request.store)
    return render(request, "owner/category/category_list.html", {
        "categories": categories
    })

@login_required
@owner_required
def category_create_view(request):
    if request.method == "POST":
        form = CategoryForm(request.POST)
        if form.is_valid():
            cat = form.save(commit=False)
            cat.store = request.store
            cat.save()
            return redirect("catalog:category_list")
    else:
        form = CategoryForm()

    return render(request, "owner/category/category_form.html", {
        "form": form,
        "title": "Nueva categoría"
    })

@login_required
@owner_required
def category_update_view(request, pk):
    category = get_object_or_404(Category, pk=pk, store=request.store)

    if request.method == "POST":
        form = CategoryForm(request.POST, instance=category)
        if form.is_valid():
            form.save()
            return redirect("catalog:category_list")
    else:
        form = CategoryForm(instance=category)

    return render(request, "owner/category/category_form.html", {
        "form": form,
        "title": "Editar categoría"
    })

@login_required
@owner_required
def category_delete_view(request, pk):
    category = get_object_or_404(Category, pk=pk, store=request.store)

    if request.method == "POST":
        category.delete()
        return redirect("catalog:category_list")

    return render(request, "owner/category/category_confirm_delete.html", {
        "category": category
    })

@login_required
@owner_required
def product_list_view(request):
    store = request.store
    q = request.GET.get("q")
    sort = request.GET.get("sort", "newest")
    selected_categories = request.GET.getlist("category")

    sort_map = {
        "newest": "-created_at",
        "az": Lower("name"),
        "za": Lower("name").desc(),
        "price_asc": "price",
        "price_desc": "-price",
    }

    products = Product.objects.filter(store=store).select_related("category")

    # Filtrado por categoría: ignorar valores vacíos (\"todas\")
    category_slugs = [slug for slug in selected_categories if slug]
    if category_slugs:
        products = products.filter(category__slug__in=category_slugs)

    if q:
        products = products.filter(name__icontains=q)

    products = products.order_by(sort_map.get(sort, "-created_at"))

    category_base_qs = Product.objects.filter(store=store)
    if q:
        category_base_qs = category_base_qs.filter(name__icontains=q)
    categories = Category.objects.filter(store=store, is_active=True).annotate(
        product_count=Count("products", filter=Q(products__in=category_base_qs))
    )

    return render(request, "owner/product/product_list.html", {
        "products": products,
        "categories": categories,
        "sort": sort,
        "sort_labels": SORT_LABELS,
        "q": q,
        "selected_categories": selected_categories,
    })

def _create_default_product_links(product):
    """Crea ProductLinks según los defaults de StoreConfig."""
    try:
        config = product.store.config
    except Exception:
        return
    types_and_flags = [
        ("whatsapp", config.default_link_whatsapp),
        ("instagram", config.default_link_instagram),
        ("facebook", config.default_link_facebook),
        ("mercadolibre", config.default_link_mercadolibre),
    ]
    for i, (link_type, enabled) in enumerate(types_and_flags):
        if enabled:
            ProductLink.objects.get_or_create(
                product=product,
                link_type=link_type,
                defaults={"order": i},
            )


@login_required
@owner_required
def product_create_view(request):
    product = Product.objects.create(
        store=request.store,
        status=Product.Status.DRAFT
    )
    _create_default_product_links(product)
    return redirect("catalog:product_update", pk=product.pk)

def _sync_product_links(product, link_types):
    """Sincroniza ProductLinks: crea los marcados, elimina los no marcados."""
    existing = {l.link_type: l for l in product.links.filter(link_type__in=["whatsapp", "instagram", "facebook", "mercadolibre"])}
    for i, lt in enumerate(["whatsapp", "instagram", "facebook", "mercadolibre"]):
        if lt in link_types:
            if lt not in existing:
                ProductLink.objects.create(product=product, link_type=lt, order=i)
        else:
            if lt in existing:
                existing[lt].delete()


@login_required
@owner_required
def product_update_view(request, pk):
    product = get_object_or_404(Product, pk=pk, store=request.store)

    if request.method == "POST":
        form = ProductForm(request.POST, instance=product, store=request.store)
        if form.is_valid():
            product = form.save(commit=False)
            product.save()
            link_types = request.POST.getlist("link_types")
            _sync_product_links(product, link_types)
            return redirect("catalog:product_list")
    else:
        form = ProductForm(instance=product, store=request.store)

    is_new = (
        product.status == Product.Status.DRAFT
        and not product.slug
    )

    existing_link_types = set(product.links.values_list("link_type", flat=True))
    return render(request, "owner/product/product_form.html", {
        "form": form,
        "product": product,
        "is_new": is_new,
        "existing_link_types": existing_link_types,
        "title": "Crear producto" if product.status == Product.Status.DRAFT else "Editar producto",
        "existing_media": [
            {
                "id": media.id,
                "file_url": media.image.url if media.media_type == ProductMedia.IMAGE and media.image else (media.video.url if media.media_type == ProductMedia.VIDEO and media.video else ""),
                "file_name": media.image.name if media.media_type == ProductMedia.IMAGE and media.image else (media.video.name if media.media_type == ProductMedia.VIDEO and media.video else ""),
                "media_type": media.media_type,
            } for media in product.media.filter(is_active=True).order_by('order', 'id')]
    })

@login_required
@owner_required
def product_publish_view(request, pk):
    product = get_object_or_404(
        Product,
        pk=pk,
        store=request.store,
        status=Product.Status.DRAFT,
    )

    if request.method != "POST":
        return HttpResponseNotAllowed(["POST"])

    product.status = Product.Status.PUBLISHED
    product.save()

    return redirect("catalog:product_list")

@login_required
@owner_required
def product_draft_view(request, pk):
    product = get_object_or_404(
        Product,
        pk=pk,
        store=request.store,
        status=Product.Status.PUBLISHED,
    )

    if request.method != "POST":
        return HttpResponseNotAllowed(["POST"])

    product.status = Product.Status.DRAFT
    product.save()

    return redirect("catalog:product_list")

@login_required
@owner_required
def product_delete_view(request, pk):
    product = get_object_or_404(Product, pk=pk, store=request.store)

    if request.method == "POST":
        product.delete()
        return redirect("catalog:product_list")

    return render(request, "owner/product/product_confirm_delete.html", {
        "product": product
    })

@login_required
@owner_required
def product_media_upload_view(request, product_id):

    print("=== MEDIA UPLOAD VIEW HIT ===", file=sys.stderr)
    print("METHOD:", request.method, file=sys.stderr)
    print("PATH:", request.path, file=sys.stderr)
    print("FILES:", request.FILES, file=sys.stderr)
    print("STORAGE CLASS:", default_storage.__class__, file=sys.stderr)
    print("MEDIA ROOT:", settings.MEDIA_ROOT, file=sys.stderr)

    # Permitimos subir media tanto en borrador como en publicado.
    # Antes filtraba por DRAFT y eso provocaba 404 al editar productos ya existentes/publicados.
    product = get_object_or_404(Product, pk=product_id, store=request.store)

    order_start = product.media.count()

    for index, file in enumerate(request.FILES.getlist("files")):
        print("FILE NAME:", file.name, file=sys.stderr)
        print("FILE SIZE:", file.size, file=sys.stderr)
        print("CONTENT TYPE:", file.content_type, file=sys.stderr)
        media_type = (
            ProductMedia.VIDEO
            if file.content_type.startswith("video")
            else ProductMedia.IMAGE
        )

        media = ProductMedia(
            product=product,
            media_type=media_type,
            order=order_start + index
        )

        if media_type == ProductMedia.IMAGE:
            media.image = file
        else:
            media.video = file

        # media.full_clean()
        media.save()
        print(
            "SAVED MEDIA:",
            media.id,
            media.product_id,
            media.image.name if media.image else None,
            file=sys.stderr
        )

    return HttpResponse(status=204)

@login_required
@owner_required
def product_create_draft_view(request):
    product = Product.objects.create(
        store=request.store,
        status=Product.Status.DRAFT
    )
    return redirect("catalog:product_update", pk=product.pk)

@login_required
@owner_required
def config_panel_view(request):
    """Panel principal de configuración con apartados."""
    return render(request, "owner/config_panel.html")


@login_required
@owner_required
def store_config_view(request):
    """Vista para que el owner edite la apariencia de su tienda."""
    config, _ = StoreConfig.objects.get_or_create(store=request.store)
    if request.method == "POST":
        form = StoreConfigForm(request.POST, request.FILES, instance=config)
        if form.is_valid():
            form.save()
            messages.success(request, "La configuración de apariencia se guardó correctamente.")
            return redirect("catalog:store_config_appearance")
    else:
        form = StoreConfigForm(instance=config)
    logo_url = config.logo.url if config.logo else static("images/favicon.png")
    return render(request, "owner/store_config.html", {
        "form": form,
        "logo_url": logo_url,
    })


@login_required
@owner_required
def store_info_contact_view(request):
    """Vista para información y contacto."""
    config, _ = StoreConfig.objects.get_or_create(store=request.store)
    if request.method == "POST":
        form = StoreInfoContactForm(request.POST, instance=config)
        if form.is_valid():
            form.save()
            messages.success(request, "La información y contacto se guardaron correctamente.")
            return redirect("catalog:store_config_info_contact")
    else:
        form = StoreInfoContactForm(instance=config)
    return render(request, "owner/store_info_contact.html", {"form": form, "config": config})


@login_required
@owner_required
def branch_list_view(request):
    """Listado de sucursales."""
    branches = Branch.objects.filter(store=request.store).order_by("id")
    return render(request, "owner/branch/branch_list.html", {"branches": branches})


@login_required
@owner_required
def branch_create_view(request):
    if request.method == "POST":
        form = BranchForm(request.POST)
        if form.is_valid():
            branch = form.save(commit=False)
            branch.store = request.store
            branch.save()
            messages.success(request, "Sucursal creada.")
            return redirect("catalog:branch_list")
    else:
        form = BranchForm()
    return render(request, "owner/branch/branch_form.html", {"form": form, "title": "Nueva sucursal"})


@login_required
@owner_required
def branch_update_view(request, pk):
    branch = get_object_or_404(Branch, pk=pk, store=request.store)
    if request.method == "POST":
        form = BranchForm(request.POST, instance=branch)
        if form.is_valid():
            form.save()
            messages.success(request, "Sucursal actualizada.")
            return redirect("catalog:branch_list")
    else:
        form = BranchForm(instance=branch)
    return render(request, "owner/branch/branch_form.html", {"form": form, "branch": branch, "title": "Editar sucursal"})


@login_required
@owner_required
def branch_delete_view(request, pk):
    branch = get_object_or_404(Branch, pk=pk, store=request.store)
    if request.method == "POST":
        branch.delete()
        messages.success(request, "Sucursal eliminada.")
        return redirect("catalog:branch_list")
    return render(request, "owner/branch/branch_confirm_delete.html", {"branch": branch})


@login_required
@owner_required
def product_cancel_view(request, pk):
    product = get_object_or_404(
        Product,
        pk=pk,
        store=request.store,
        status=Product.Status.DRAFT,
    )
    if request.method != "POST":
        return HttpResponseNotAllowed(["POST"])
    product.delete()
    return redirect("catalog:product_list")


def branches_public_view(request):
    """Vista pública de sucursales para los clientes."""
    store = getattr(request, "store", None)
    if not store:
        return render(request, "catalog/landing.html", _landing_context(request))
    branches = Branch.objects.filter(store=store).order_by("id")
    return render(request, "catalog/branches_public.html", {"branches": branches})