from django.db import models
from django.utils.text import slugify
from django.core.exceptions import ValidationError
from django.conf import settings
from django.urls import reverse

import urllib.parse

import re
import unicodedata

# Create your models here.


# -- Categoría --
class Category(models.Model):
    store = models.ForeignKey(
        "core.Store",
        on_delete=models.CASCADE,
        related_name="categories",
        verbose_name="Tienda"
    )

    name = models.CharField(
        max_length=100,
        verbose_name="Nombre"
    )

    slug = models.SlugField(
        max_length=120,
        blank=True
    )

    is_active = models.BooleanField(
        default=True,
        verbose_name="Activa"
    )

    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["name"]
        verbose_name = "Categoría"
        verbose_name_plural = "Categorías"
        constraints = [
            models.UniqueConstraint(
                fields=["store", "slug"],
                name="catalog_category_store_slug_unique"
            ),
        ]

    def __str__(self):
        return self.name

    def save(self, *args, **kwargs):
        if not self.slug:
            base_slug = self._generate_slug(self.name)
            slug = base_slug
            counter = 1
            qs = Category.objects.filter(store=self.store)
            while qs.filter(slug=slug).exists():
                slug = f"{base_slug}-{counter}"
                counter += 1
            self.slug = slug

        super().save(*args, **kwargs)

    @staticmethod
    def _generate_slug(text: str) -> str:
        # Normaliza acentos (Electrónica -> Electronica)
        text = unicodedata.normalize("NFKD", text)
        text = text.encode("ascii", "ignore").decode("ascii")

        text = text.lower()

        # Reemplaza cualquier cosa que no sea letra o número por -
        text = re.sub(r"[^a-z0-9]+", "-", text)

        # Elimina - repetidos y bordes
        text = re.sub(r"-+", "-", text).strip("-")

        return text


#-- Producto --#
class Product(models.Model):
    class Status(models.TextChoices):
        DRAFT = "draft", "Borrador"
        PUBLISHED = "published", "Publicado"

    store = models.ForeignKey(
        "core.Store",
        on_delete=models.CASCADE,
        related_name="products",
        verbose_name="Tienda"
    )

    name = models.CharField(
        max_length=150,
        verbose_name="Nombre",
        blank=True
    )

    category = models.ForeignKey(
        Category,
        related_name="products",
        on_delete=models.PROTECT,
        null=True,
        blank=True,
        verbose_name="Categoría"
    )

    slug = models.SlugField(
        max_length=180,
        blank=True,
    )

    description = models.TextField(
        blank=True,
        verbose_name="Descripción"
        )

    price = models.DecimalField(
        max_digits=18,
        decimal_places=2,
        null=True,
        blank=True,
        verbose_name="Precio"
    )

    stock = models.PositiveIntegerField(
        null=True,
        blank=True,
        default=None,
        verbose_name="Stock",
        help_text="Dejar vacío si no controlás el stock. En 0 no se puede agregar al carrito."
    )

    status = models.CharField(
        max_length=20,
        choices=Status.choices,
        default=Status.DRAFT
    )

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=["store", "slug"],
                condition=models.Q(status="published"),
                name="catalog_product_store_slug_unique",
            ),
        ]

    # ---------- PROPERTIES ----------

    @property
    def is_draft(self):
        return self.status == self.Status.DRAFT

    @property
    def thumbnail(self):
        return (
            self.media
            .filter(media_type="image", is_active=True)
            .order_by("order", "id")
            .first()
        )

    # ---------- SAVE ----------

    def save(self, *args, **kwargs):
        if self.status == self.Status.PUBLISHED and not self.slug:
            base_slug = self._generate_slug(self.name)
            slug = base_slug
            counter = 1
            qs = Product.objects.filter(store=self.store)
            while qs.filter(slug=slug).exists():
                slug = f"{base_slug}_{counter}"
                counter += 1
            self.slug = slug

        super().save(*args, **kwargs)

    @staticmethod
    def _generate_slug(text: str) -> str:
        # Normaliza acentos
        text = unicodedata.normalize("NFKD", text)
        text = text.encode("ascii", "ignore").decode("ascii")

        text = text.lower()

        # Elimina números
        text = re.sub(r"\d+", "", text)

        # Espacios → _
        text = re.sub(r"\s+", "_", text.strip())

        # Solo letras y _
        text = re.sub(r"[^a-z_]", "", text)

        return text

    def __str__(self):
        return self.name
    

#-- Media producto --#
class ProductMedia(models.Model):
    IMAGE = "image"
    VIDEO = "video"

    MEDIA_TYPE_CHOICES = [
        (IMAGE, "Imagen"),
        (VIDEO, "Video"),
    ]

    product = models.ForeignKey(
        Product,
        related_name="media",
        on_delete=models.CASCADE
    )

    media_type = models.CharField(
        max_length=10,
        choices=MEDIA_TYPE_CHOICES,
        default=IMAGE
    )

    image = models.ImageField(
        upload_to="products/images/",
        blank=True,
        null=True
    )

    video = models.FileField(
        upload_to="products/videos/",
        blank=True,
        null=True
    )

    order = models.PositiveIntegerField(default=0)

    is_active = models.BooleanField(default=True)

    class Meta:
        ordering = ["order"]

    def clean(self):
        from django.core.exceptions import ValidationError

        if self.media_type == self.IMAGE and not self.image:
            raise ValidationError("Una imagen requiere archivo de imagen.")

        if self.media_type == self.VIDEO and not self.video:
            raise ValidationError("Un video requiere archivo de video.")

    def __str__(self):
        return f"{self.product} - {self.media_type}"
    

#-- Links de compra --#
class ProductLink(models.Model):
    LINK_CHOICES = (
        ("whatsapp", "Whatsapp"),
        ("instagram", "Instagram"),
        ("facebook", "Facebook"),
        ("mercadolibre", "MercadoLibre"),        
        ("external", "Externo"),
    )

    LINK_PRIORITY = {
        "whatsapp": 1,        
        "instagram": 2,
        "mercadolibre": 3,
        "facebook": 4,
        "external": 5,
    }

    product = models.ForeignKey(
        Product,
        related_name="links",
        on_delete=models.CASCADE
    )

    link_type = models.CharField(
        max_length=20,
        choices=LINK_CHOICES,
        verbose_name="Tipo de link",
    )

    url = models.URLField(
        blank=True,
        verbose_name="URL (Solo external)",
    )

    button_text = models.CharField(
        max_length=100,
        blank=True,
        verbose_name="Texto del botón (Solo external)",
    )

    order = models.PositiveIntegerField(
        default=0,
        verbose_name="Orden",
    )

    class Meta:
        ordering = ["order"]
        verbose_name = "Link de producto"
        verbose_name_plural = "Links de producto"
            
    def get_url(self):
        try:
            config = self.product.store.config
        except (StoreConfig.DoesNotExist, AttributeError):
            return "#"
        if not config:
            return "#"

        store = self.product.store
        product_url = ""
        if self.product.slug:
            root = getattr(settings, "ROOT_DOMAIN", "catalogico.shop")
            path = reverse("catalog:product_detail", args=[self.product.slug])
            product_url = f"https://{store.slug}.{root}{path}"

        def build_message():
            template = config.whatsapp_message_template or ""
            if not template:
                return ""
            msg = template.replace("{{ product }}", self.product.name or "")
            if "{{ url }}" in msg:
                msg = msg.replace("{{ url }}", product_url or "")
            return msg

        if self.link_type == "whatsapp" and config.whatsapp_number:
            message = build_message()
            if not message:
                message = self.product.name or ""
            encoded_message = urllib.parse.quote(message)
            return f"https://wa.me/{config.whatsapp_number}?text={encoded_message}"

        if self.link_type == "instagram" and config.instagram_username:
            message = build_message()
            if not message:
                message = self.product.name or ""
            encoded_message = urllib.parse.quote(message)
            return f"https://ig.me/m/{config.instagram_username}?text={encoded_message}"

        if self.link_type == "facebook" and config.facebook_page:
            return f"https://facebook.com/{config.facebook_page}"

        if self.link_type == "mercadolibre" and config.mercadolibre_store:
            return f"https://mercadolibre.com.ar/{config.mercadolibre_store}"

        return self.url
    
    @property
    def priority(self):
        return self.LINK_PRIORITY.get(self.link_type, 99)

    def save(self, *args, **kwargs):
        if self.link_type != "external":
            self.button_text = dict(self.LINK_CHOICES)[(self.link_type)]
            self.url = "" 
        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.product.name} - {self.link_type}"
    
# Sucursal (para tiendas con múltiples locales)
class Branch(models.Model):
    store = models.ForeignKey(
        "core.Store",
        on_delete=models.CASCADE,
        related_name="branches",
        verbose_name="Tienda"
    )
    country = models.CharField(max_length=100, blank=True, verbose_name="País")
    province = models.CharField(max_length=100, blank=True, verbose_name="Provincia")
    city = models.CharField(max_length=100, blank=True, verbose_name="Ciudad")
    address = models.CharField(max_length=255, blank=True, verbose_name="Dirección")
    hours = models.CharField(max_length=200, blank=True, verbose_name="Horarios")
    location_url = models.URLField(blank=True, verbose_name="URL de Google Maps (generado automáticamente al guardar)")

    class Meta:
        ordering = ["id"]
        verbose_name = "Sucursal"
        verbose_name_plural = "Sucursales"

    def __str__(self):
        parts = [p for p in [self.city, self.province, self.country] if p]
        return " - ".join(parts) if parts else f"Sucursal #{self.id}"


# Store Contact Data
class StoreConfig(models.Model):
    store = models.OneToOneField(
        "core.Store",
        on_delete=models.CASCADE,
        related_name="config",
        verbose_name="Tienda"
    )

    # Ubicación principal (cuando no hay múltiples sucursales)
    country = models.CharField(max_length=100, blank=True, verbose_name="País")
    province = models.CharField(max_length=100, blank=True, verbose_name="Provincia")
    city = models.CharField(max_length=100, blank=True, verbose_name="Ciudad")
    address = models.CharField(
        max_length=255,
        blank=True,
        verbose_name="Dirección"
    )
    hours = models.CharField(
        max_length=200,
        blank=True,
        verbose_name="Horarios"
    )
    location_url = models.URLField(
        blank=True,
        verbose_name="URL de ubicación"
    )

    whatsapp_number = models.CharField(
        max_length=30,
        blank=True,
        verbose_name="Número de WhatsApp"
    )

    instagram_username = models.CharField(
        max_length=100,
        blank=True,
        verbose_name="Usuario de Instagram"
    )

    facebook_page = models.CharField(
        max_length=100,
        blank=True,
        verbose_name="Página de Facebook"
    )

    mercadolibre_store = models.CharField(
        max_length=100,
        blank=True,
        verbose_name="Tienda de MercadoLibre"
    )

    whatsapp_message_template = models.TextField(
        default="Hola! Estoy interesado/a en el producto '{{ product }}' ({{ url }})",
        verbose_name="Mensaje automático (WhatsApp e Instagram)",
        help_text='Usar {{ product }} para el nombre del producto y {{ url }} para la URL del producto.'
    )

    order_message_template = models.TextField(
        blank=True,
        default="Hola, mi pedido:\n{{ items }}\nTotal: {{ total }}",
        verbose_name="Mensaje del pedido del carrito (WhatsApp e Instagram)",
        help_text='Usar {{ items }} para la lista de productos (nombre y cantidad por línea) y {{ total }} para el total. Mismo mensaje para WhatsApp e Instagram.'
    )

    # Botones de compra por defecto al crear producto
    default_link_whatsapp = models.BooleanField(default=False, verbose_name="WhatsApp por defecto")
    default_link_instagram = models.BooleanField(default=False, verbose_name="Instagram por defecto")
    default_link_facebook = models.BooleanField(default=False, verbose_name="Facebook por defecto")
    default_link_mercadolibre = models.BooleanField(default=False, verbose_name="MercadoLibre por defecto")

    # Logo (header + favicon)
    logo = models.ImageField(
        upload_to="stores/logos/",
        blank=True,
        null=True,
        verbose_name="Logo",
        help_text="Logo de la tienda (header y favicon)"
    )

    # === MODO CLARO (7 colores) ===
    color_bg = models.CharField(
        max_length=7,
        blank=True,
        default="#ffffff",
        verbose_name="Color fondo de página",
        help_text="Fondo general de la tienda"
    )
    color_surface = models.CharField(
        max_length=7,
        blank=True,
        default="#f8f8f8",
        verbose_name="Color superficies",
        help_text="Tarjetas, cajas, áreas elevadas"
    )
    color_surface_secondary = models.CharField(
        max_length=7,
        blank=True,
        default="#f0f0f0",
        verbose_name="Color superficies secundarias",
        help_text="Tarjetas alternativas, headers"
    )
    color_text = models.CharField(
        max_length=7,
        blank=True,
        default="#111111",
        verbose_name="Color texto principal",
        help_text="Texto principal de la tienda"
    )
    color_primary = models.CharField(
        max_length=7,
        blank=True,
        default="#3483fa",
        verbose_name="Color primario",
        help_text="Botones, enlaces, detalles destacados"
    )
    color_primary_hover = models.CharField(
        max_length=7,
        blank=True,
        default="#468cf6",
        verbose_name="Color primario al pasar el mouse",
        help_text="Hover sobre botones y enlaces"
    )
    color_border = models.CharField(
        max_length=7,
        blank=True,
        default="#e0e0e0",
        verbose_name="Color bordes",
        help_text="Líneas separadoras y bordes"
    )
    color_muted = models.CharField(
        max_length=7,
        blank=True,
        default="#6b6b6b",
        verbose_name="Color texto secundario",
        help_text="Texto de menor importancia"
    )

    # === MODO OSCURO (7 colores) ===
    color_bg_dark = models.CharField(
        max_length=7,
        blank=True,
        default="#121212",
        verbose_name="Color fondo de página (modo oscuro)",
        help_text="Fondo general de la tienda"
    )
    color_surface_dark = models.CharField(
        max_length=7,
        blank=True,
        default="#1e1e1e",
        verbose_name="Color superficies (modo oscuro)",
        help_text="Tarjetas, cajas, áreas elevadas"
    )
    color_surface_secondary_dark = models.CharField(
        max_length=7,
        blank=True,
        default="#2a2a2a",
        verbose_name="Color superficies secundarias (modo oscuro)",
        help_text="Tarjetas alternativas, headers"
    )
    color_text_dark = models.CharField(
        max_length=7,
        blank=True,
        default="#f5f5f5",
        verbose_name="Color texto principal (modo oscuro)",
        help_text="Texto principal de la tienda"
    )
    color_primary_dark = models.CharField(
        max_length=7,
        blank=True,
        default="#3483fa",
        verbose_name="Color primario (modo oscuro)",
        help_text="Botones, enlaces, detalles destacados"
    )
    color_primary_hover_dark = models.CharField(
        max_length=7,
        blank=True,
        default="#468cf6",
        verbose_name="Color primario al pasar el mouse (modo oscuro)",
        help_text="Hover sobre botones y enlaces"
    )
    color_border_dark = models.CharField(
        max_length=7,
        blank=True,
        default="#333333",
        verbose_name="Color bordes (modo oscuro)",
        help_text="Líneas separadoras y bordes"
    )
    color_muted_dark = models.CharField(
        max_length=7,
        blank=True,
        default="#aaaaaa",
        verbose_name="Color texto secundario (modo oscuro)",
        help_text="Texto de menor importancia"
    )

    class Meta:
        verbose_name = "Configuración de la tienda"
        verbose_name_plural = "Configuración de la tienda"

    def save(self, *args, **kwargs):
        super().save(*args, **kwargs)

    def __str__(self):
        return "Configuración de la tienda"