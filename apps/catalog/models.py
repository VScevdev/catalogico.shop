from django.db import models
from django.utils.text import slugify
from django.core.exceptions import ValidationError

import urllib.parse

import re
import unicodedata

# Create your models here.


# -- Categoría --
class Category(models.Model):
    name = models.CharField(
        max_length=100,
        verbose_name="Nombre"
    )

    slug = models.SlugField(
        max_length=120,
        unique=True,
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

    def __str__(self):
        return self.name

    def save(self, *args, **kwargs):
        if not self.slug:
            base_slug = self._generate_slug(self.name)
            slug = base_slug
            counter = 1

            while Category.objects.filter(slug=slug).exists():
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
        unique=True,
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

    status = models.CharField(
        max_length=20,
        choices=Status.choices,
        default=Status.DRAFT
    )

    is_active = models.BooleanField(default=True)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

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

            while Product.objects.filter(slug=slug).exists():
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
        config = StoreConfig.objects.first()
        if not config:
            return "#"

        if self.link_type == "whatsapp" and config.whatsapp_number:
            message = config.whatsapp_message_template.replace(
                "{{ product }}",
                self.product.name
            )
            encoded_message = urllib.parse.quote(message)
            return f"https://wa.me/{config.whatsapp_number}?text={encoded_message}"

        if self.link_type == "instagram" and config.instagram_username:
            return f"https://instagram.com/{config.instagram_username}"

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
    
# Store Contact Data
class StoreConfig(models.Model):
    whatsapp_number = models.CharField(
        max_length=30,
        blank=True,
        verbose_name="Número de WhatsApp (sin + ni espacios)"
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
        default="Hola! Estoy interesado/a en el producto \'{{ product }}\'",
        verbose_name="Mensaje automático de WhatsApp",
        help_text='Usar {{ product }} para el nombre del producto.'
    )

    class Meta:
        verbose_name = "Configuración de la tienda"
        verbose_name_plural = "Configuración de la tienda"

    def save(self, *args, **kwargs):
        if not self.pk and StoreConfig.objects.exists():
            raise ValidationError("Solo puede existir una configuración de la tienda")
        super().save(*args, **kwargs)

    def __str__(self):
        return "Configuración de la tienda"