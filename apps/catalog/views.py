from django.shortcuts import render, get_object_or_404, redirect
from django.templatetags.static import static
from django.contrib import messages
from django.conf import settings
from django.urls import reverse
from django.http import HttpResponse, HttpResponseNotAllowed, JsonResponse
from django.contrib.auth.decorators import login_required
from apps.accounts.decorators import owner_required
from django.db import IntegrityError
from django.db.models import Count, Max, Q
from django.db.models.functions import Lower
from django.core.paginator import Paginator
from django.core.files.storage import default_storage
from urllib.parse import urlencode, quote
from .models import Product, Category, ProductMedia, ProductLink, StoreConfig, Branch, FAQ, Tutorial, StoreFeedback
from .forms import CategoryForm, ProductForm, StoreConfigForm, StoreInfoContactForm, StoreCustomMessagesForm, BranchForm, StoreFeedbackForm, FAQForm
from .constants import SORT_LABELS
from . import cart as cart_helpers

import json
import sys
import uuid

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
        "catalog_full_path": request.get_full_path(),
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

    max_cart_quantity = 99
    if product.stock is not None and product.stock > 0:
        max_cart_quantity = min(99, product.stock)
    media_items = product.media.filter(is_active=True).order_by("order", "id")
    media_items_json = [
        {
            "url": m.image.url if m.media_type == ProductMedia.IMAGE else (m.video.url if m.media_type == ProductMedia.VIDEO else ""),
            "media_type": m.media_type,
        }
        for m in media_items
    ]
    context = {
        "product": product,
        "media_items": media_items,
        "media_items_json": media_items_json,
        "links": product.links.all().order_by("order", "id"),
        "has_links": product.links.exists(),
        "catalog_url": reverse("catalog:catalog"),
        "max_cart_quantity": max_cart_quantity,
    }
    return render(request, "catalog/product_detail.html", context)

def privacy_view(request):
    return render(request, "extra/privacy.html")


def faq_public_view(request):
    """Página pública de preguntas frecuentes de la tienda."""
    store = getattr(request, "store", None)
    if not store:
        return redirect("catalog:catalog")
    faqs = FAQ.objects.filter(store=store, is_active=True).order_by("order")
    return render(request, "catalog/faq.html", {"faqs": faqs})


def complaint_form_view(request):
    """Formulario público para enviar queja o propuesta."""
    store = getattr(request, "store", None)
    if not store:
        return redirect("catalog:catalog")
    if request.method == "POST":
        form = StoreFeedbackForm(request.POST)
        if form.is_valid():
            feedback = form.save(commit=False)
            feedback.store = store
            feedback.save()
            messages.success(request, "Tu mensaje fue enviado correctamente. Gracias.")
            return redirect("catalog:complaint_form")
    else:
        form = StoreFeedbackForm()
    return render(request, "catalog/complaint_form.html", {"form": form})


def _safe_redirect_url(request, next_url):
    """Solo permite redirigir al mismo host (evitar open redirect)."""
    if not next_url or not next_url.strip():
        return None
    from urllib.parse import urlparse
    try:
        parsed = urlparse(next_url)
        if parsed.netloc and parsed.netloc != request.get_host().split(":")[0]:
            return None
        if parsed.scheme and parsed.scheme not in ("http", "https", ""):
            return None
        path = (parsed.path or "/").lstrip("/")
        if path.startswith("//") or "\\" in path:
            return None
        return next_url
    except Exception:
        return None


DEFAULT_ORDER_MESSAGE_TEMPLATE = "Hola! Mi pedido:\n{{ items }}\nTotal: {{ total }}"


def _build_order_message(config, cart_items_with_quantity, total_display):
    """Construye el mensaje del pedido reemplazando {{ items }} y {{ total }}."""
    template = (getattr(config, "order_message_template", None) or "").strip()
    if not template:
        template = DEFAULT_ORDER_MESSAGE_TEMPLATE
    lines = []
    for product, qty in cart_items_with_quantity:
        name = product.name or "Producto"
        if product.price is not None and product.price > 0:
            lines.append(f"- {name} x {qty}")
        else:
            lines.append(f"- {name} x {qty} (consultar precio)")
    items_text = "\n".join(lines) if lines else "-"
    msg = template.replace("{{ items }}", items_text).replace("{{ total }}", total_display)
    return msg


def cart_detail_view(request):
    """Página del carrito: ítems, total, botones WhatsApp e Instagram (mismo mensaje)."""
    store = getattr(request, "store", None)
    if not store:
        return render(request, "catalog/landing.html", _landing_context(request))

    raw_cart = cart_helpers.get_cart_for_store(request.session, store.id)
    product_ids = list(raw_cart.keys())
    if not product_ids:
        return render(request, "catalog/cart.html", {
            "cart_items": [],
            "cart_total": None,
            "cart_total_display": "0",
            "whatsapp_url": None,
            "instagram_url": None,
        })

    products = list(
        Product.objects.filter(
            store=store,
            id__in=product_ids,
            status=Product.Status.PUBLISHED,
        ).select_related("store").prefetch_related("media")
    )
    valid_ids = {p.id for p in products}
    # Limpiar sesión de ítems que ya no existen o no están publicados
    cleaned_cart = {pid: raw_cart[pid] for pid in valid_ids if pid in raw_cart}
    if len(cleaned_cart) != len(raw_cart):
        cart_helpers.set_cart_for_store(request.session, store.id, cleaned_cart)
        messages.info(request, "Un producto ya no está disponible y fue quitado del carrito.")

    # Ajustar cantidades al stock disponible (si el producto controla stock)
    product_by_id = {p.id: p for p in products}
    cart_modified = False
    for pid, qty in list(cleaned_cart.items()):
        product = product_by_id.get(pid)
        if product and product.stock is not None and qty > product.stock:
            cleaned_cart[pid] = product.stock
            cart_modified = True
    if cart_modified:
        cart_helpers.set_cart_for_store(request.session, store.id, cleaned_cart)
        messages.info(request, "El stock de algún producto bajó; se actualizó la cantidad en tu carrito.")

    # Construir lista de dicts (product, qty, subtotal_display) en orden de product_ids
    cart_items_with_quantity = []
    total = 0
    for pid in product_ids:
        if pid not in valid_ids:
            continue
        qty = cleaned_cart.get(pid, 0)
        if qty <= 0:
            continue
        product = product_by_id.get(pid)
        if not product:
            continue
        if product.price is not None and product.price > 0:
            subtotal = float(product.price) * qty
            total += subtotal
            subtotal_display = f"{subtotal:,.2f}".replace(",", "X").replace(".", ",").replace("X", ".")
        else:
            subtotal_display = "—"
        cart_items_with_quantity.append({
            "product": product,
            "qty": qty,
            "subtotal_display": subtotal_display,
        })
    total_display = f"${total:,.2f}".replace(",", "X").replace(".", ",").replace("X", ".") if total else "Consultar"
    try:
        config = store.config
    except Exception:
        config = None
    order_message = _build_order_message(config, [(item["product"], item["qty"]) for item in cart_items_with_quantity], total_display) if config else ""
    whatsapp_url = None
    instagram_url = None
    if config and order_message:
        encoded = quote(order_message)
        if config.whatsapp_number:
            whatsapp_url = f"https://wa.me/{config.whatsapp_number}?text={encoded}"
        if config.instagram_username:
            instagram_url = f"https://ig.me/m/{config.instagram_username}?text={encoded}"

    return render(request, "catalog/cart.html", {
        "cart_items": cart_items_with_quantity,
        "cart_total": total,
        "cart_total_display": total_display,
        "whatsapp_url": whatsapp_url,
        "instagram_url": instagram_url,
    })


def cart_add_view(request):
    """POST: product_id, quantity (opcional), next (opcional). Añade al carrito."""
    store = getattr(request, "store", None)
    if not store:
        return redirect("catalog:landing")
    if request.method != "POST":
        return HttpResponseNotAllowed(["POST"])

    try:
        product_id = int(request.POST.get("product_id") or 0)
    except (ValueError, TypeError):
        messages.error(request, "Producto no válido.")
        return redirect("catalog:catalog")
    quantity = 1
    try:
        quantity = max(1, min(int(request.POST.get("quantity") or 1), 99))
    except (ValueError, TypeError):
        pass

    product = Product.objects.filter(
        store=store,
        pk=product_id,
        status=Product.Status.PUBLISHED,
    ).first()
    if not product:
        messages.error(request, "El producto no está disponible.")
        return redirect("catalog:catalog")

    if product.stock is not None:
        cart_now = cart_helpers.get_cart_for_store(request.session, store.id)
        in_cart = cart_now.get(product_id, 0)
        available = max(0, product.stock - in_cart)
        if available <= 0:
            messages.error(request, "No hay stock disponible para este producto.")
            next_url = _safe_redirect_url(request, request.POST.get("next") or "")
            if next_url:
                return redirect(next_url)
            return redirect("catalog:catalog")
        if quantity > available:
            quantity = available
            messages.success(request, f"Solo quedaban {available} disponibles; se agregó esa cantidad al carrito.")
        else:
            messages.success(request, "Producto añadido al carrito.")
    else:
        messages.success(request, "Producto añadido al carrito.")

    cart_helpers.add_to_cart(request.session, store.id, product_id, quantity)

    next_url = _safe_redirect_url(request, request.POST.get("next") or "")
    if next_url:
        return redirect(next_url)
    return redirect("catalog:cart_detail")


def cart_remove_view(request):
    """POST: product_id, next (opcional). Quita del carrito."""
    store = getattr(request, "store", None)
    if not store:
        return redirect("catalog:landing")
    if request.method != "POST":
        return HttpResponseNotAllowed(["POST"])

    try:
        product_id = int(request.POST.get("product_id") or 0)
    except (ValueError, TypeError):
        return redirect("catalog:cart_detail")
    product = Product.objects.filter(store=store, pk=product_id).first()
    if product:
        cart_helpers.remove_from_cart(request.session, store.id, product_id)
    next_url = _safe_redirect_url(request, request.POST.get("next") or "")
    if next_url:
        return redirect(next_url)
    return redirect("catalog:cart_detail")


def cart_update_view(request):
    """POST: product_id, quantity. Actualiza cantidad; si <= 0 quita."""
    store = getattr(request, "store", None)
    if not store:
        return redirect("catalog:landing")
    if request.method != "POST":
        return HttpResponseNotAllowed(["POST"])

    try:
        product_id = int(request.POST.get("product_id") or 0)
    except (ValueError, TypeError):
        return redirect("catalog:cart_detail")
    try:
        quantity = int(request.POST.get("quantity") or 0)
    except (ValueError, TypeError):
        quantity = 0
    product = Product.objects.filter(
        store=store,
        pk=product_id,
        status=Product.Status.PUBLISHED,
    ).first()
    if product:
        if product.stock is not None and quantity > product.stock:
            quantity = product.stock
        cart_helpers.update_cart(request.session, store.id, product_id, quantity)
    next_url = _safe_redirect_url(request, request.POST.get("next") or "")
    if next_url:
        return redirect(next_url)
    return redirect("catalog:cart_detail")


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


def _unique_draft_slug(store):
    """Genera un slug único para un borrador (evita UNIQUE en store+slug cuando la BD no es condicional)."""
    while True:
        slug = "_draft_" + uuid.uuid4().hex[:12]
        if not Product.objects.filter(store=store, slug=slug).exists():
            return slug


@login_required
@owner_required
def product_create_view(request):
    """Crea siempre un nuevo producto (borrador). Cada borrador lleva slug único temporal."""
    product = Product.objects.create(
        store=request.store,
        status=Product.Status.DRAFT,
        slug=_unique_draft_slug(request.store),
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
        and (not product.slug or (product.slug or "").startswith("_draft_"))
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
    created_ids = []

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
        created_ids.append(media.id)
        print(
            "SAVED MEDIA:",
            media.id,
            media.product_id,
            media.image.name if media.image else None,
            file=sys.stderr
        )

    return JsonResponse({"ids": created_ids})


@login_required
@owner_required
def product_media_reorder_view(request, product_id):
    """POST JSON {"order": [id1, id2, ...]} para reordenar media del producto."""
    if request.method != "POST":
        return HttpResponseNotAllowed(["POST"])
    product = get_object_or_404(Product, pk=product_id, store=request.store)
    try:
        data = json.loads(request.body) if request.body else {}
        order_ids = data.get("order") or []
    except (ValueError, TypeError):
        return JsonResponse({"error": "Invalid JSON"}, status=400)
    if not isinstance(order_ids, list):
        return JsonResponse({"error": "order must be a list"}, status=400)
    valid_ids = set(
        product.media.filter(is_active=True).values_list("id", flat=True)
    )
    for id_ in order_ids:
        if id_ not in valid_ids:
            return JsonResponse({"error": "Invalid media id"}, status=400)
    for position, id_ in enumerate(order_ids):
        ProductMedia.objects.filter(pk=id_, product=product).update(order=position)
    return HttpResponse(status=204)


@login_required
@owner_required
def product_media_delete_view(request, product_id, media_id):
    """Soft-delete: marca is_active=False en el ProductMedia."""
    if request.method != "POST":
        return HttpResponseNotAllowed(["POST"])
    media = get_object_or_404(
        ProductMedia,
        pk=media_id,
        product_id=product_id,
        product__store=request.store,
    )
    media.is_active = False
    media.save()
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
def help_hub_view(request):
    """Hub de Ayuda: FAQ, Tutoriales, Quejas y propuestas."""
    return render(request, "owner/help_hub.html")


@login_required
@owner_required
def faq_owner_view(request):
    """Listado de FAQ de la tienda para gestionar (todas, activas e inactivas)."""
    faqs = FAQ.objects.filter(store=request.store).order_by("order", "id")
    return render(request, "owner/help/faq_list.html", {"faqs": faqs})


@login_required
@owner_required
def faq_create_view(request):
    """Crear nueva pregunta frecuente. Orden se asigna al final (máx + 1)."""
    if request.method == "POST":
        form = FAQForm(request.POST)
        if form.is_valid():
            faq = form.save(commit=False)
            faq.store = request.store
            faq.is_active = True
            agg = FAQ.objects.filter(store=request.store).aggregate(m=Max("order"))
            faq.order = (agg["m"] or 0) + 1
            faq.save()
            messages.success(request, "Pregunta frecuente creada.")
            return redirect("catalog:faq_owner")
    else:
        form = FAQForm()
    return render(request, "owner/help/faq_form.html", {"form": form, "title": "Nueva pregunta frecuente"})


@login_required
@owner_required
def faq_update_view(request, pk):
    """Editar pregunta frecuente."""
    faq = get_object_or_404(FAQ, pk=pk, store=request.store)
    if request.method == "POST":
        form = FAQForm(request.POST, instance=faq)
        if form.is_valid():
            form.save()
            messages.success(request, "Pregunta frecuente actualizada.")
            return redirect("catalog:faq_owner")
    else:
        form = FAQForm(instance=faq)
    return render(request, "owner/help/faq_form.html", {"form": form, "faq": faq, "title": "Editar pregunta frecuente"})


@login_required
@owner_required
def faq_delete_view(request, pk):
    """Eliminar pregunta frecuente."""
    faq = get_object_or_404(FAQ, pk=pk, store=request.store)
    if request.method == "POST":
        faq.delete()
        messages.success(request, "Pregunta frecuente eliminada.")
        return redirect("catalog:faq_owner")
    return render(request, "owner/help/faq_confirm_delete.html", {"faq": faq})


@login_required
@owner_required
def faq_reorder_view(request):
    """POST JSON {"order": [id1, id2, ...]} para reordenar FAQs de la tienda."""
    if request.method != "POST":
        return HttpResponseNotAllowed(["POST"])
    try:
        data = json.loads(request.body) if request.body else {}
        order_ids = data.get("order") or []
    except (ValueError, TypeError):
        return JsonResponse({"error": "Invalid JSON"}, status=400)
    if not isinstance(order_ids, list):
        return JsonResponse({"error": "order must be a list"}, status=400)
    valid_ids = set(FAQ.objects.filter(store=request.store).values_list("id", flat=True))
    for id_ in order_ids:
        if id_ not in valid_ids:
            return JsonResponse({"error": "Invalid FAQ id"}, status=400)
    for position, id_ in enumerate(order_ids):
        FAQ.objects.filter(pk=id_, store=request.store).update(order=position)
    return HttpResponse(status=204)


@login_required
@owner_required
def tutorial_list_view(request):
    """Listado de tutoriales (solo lectura)."""
    tutorials = Tutorial.objects.filter(is_active=True).order_by("order")
    return render(request, "owner/help/tutorial_list.html", {"tutorials": tutorials})


@login_required
@owner_required
def complaint_list_view(request):
    """Listado de quejas y propuestas de la tienda con filtros opcionales."""
    qs = StoreFeedback.objects.filter(store=request.store).order_by("-created_at")
    read_filter = request.GET.get("read")
    if read_filter == "0":
        qs = qs.filter(is_read=False)
    elif read_filter == "1":
        qs = qs.filter(is_read=True)
    tipo_filter = request.GET.get("tipo")
    if tipo_filter in ("queja", "propuesta"):
        qs = qs.filter(feedback_type=tipo_filter)
    return render(request, "owner/help/complaint_list.html", {
        "feedbacks": qs,
        "read_filter": read_filter,
        "tipo_filter": tipo_filter,
    })


@login_required
@owner_required
def complaint_mark_read_view(request, pk):
    """Marcar una queja/propuesta como leída."""
    if request.method != "POST":
        return HttpResponseNotAllowed(["POST"])
    feedback = get_object_or_404(StoreFeedback, pk=pk, store=request.store)
    feedback.is_read = True
    feedback.save()
    return redirect("catalog:complaint_list")


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
def store_custom_messages_view(request):
    """Vista para mensajes personalizados (producto y carrito)."""
    config, _ = StoreConfig.objects.get_or_create(store=request.store)
    if request.method == "POST":
        form = StoreCustomMessagesForm(request.POST, instance=config)
        if form.is_valid():
            form.save()
            messages.success(request, "Los mensajes personalizados se guardaron correctamente.")
            return redirect("catalog:store_custom_messages")
    else:
        form = StoreCustomMessagesForm(instance=config)
    return render(request, "owner/store_custom_messages.html", {"form": form})


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