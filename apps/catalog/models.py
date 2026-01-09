from django.db import models
from django.utils.text import slugify
from django.core.exceptions import ValidationError

import urllib.parse

# Create your models here.


#-- Categoría --#
class Category(models.Model):
    name = models.CharField(
        max_length=100,
        unique=True,
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
    order = models.PositiveIntegerField(
        default=0,
        verbose_name="Orden"
    )

    class Meta:
        ordering = ["order", "name"]
        verbose_name = "Categoría"
        verbose_name_plural = "Categorías"

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.name)
        super().save(*args, **kwargs)

    def __str__(self):
        return self.name


#-- Producto --#
class Product(models.Model):
    category = models.ForeignKey(
        Category,
        related_name="products",
        on_delete=models.PROTECT,
        verbose_name="Categoría"
    )
    name = models.CharField(
        max_length=150,
        verbose_name="Nombre"
    )
    slug = models.SlugField(
        max_length=180,
        unique=True,
        blank=True
    )
    description = models.TextField(
        blank=True,
        verbose_name="Descripción"
    )
    price = models.DecimalField(
        max_digits=18,
        decimal_places=2,
        verbose_name="Precio"
    )
    is_active = models.BooleanField(
        default=True,
        verbose_name="Activo"
    )
    created_at = models.DateTimeField(
        auto_now_add=True
    )
    updated_at = models.DateTimeField(
        auto_now=True
    )
    #-- Thumbnail --#
    @property
    def thumbnail(self):
        return self.images.order_by("order").first()
    
    #-- Links Ordenados --#
    @property
    def ordered_links(self):
        return sorted(
            self.links.all(),
            key=lambda link: link.priority
        )

    class Meta:
        ordering = []
        verbose_name = "Producto"
        verbose_name_plural = "Productos"

    def save(self, *args, **kwargs):
        if not self.slug:
            base_slug = slugify(self.name)
            slug = base_slug
            counter = 1
            while Product.objects.filter(slug=slug).exists():
                slug = f"{base_slug}-{counter}"
                counter += 1
            self.slug = slug
        super().save(*args, **kwargs)

    def __str__(self):
        return self.name
    

#-- Imagenes producto --#
class ProductImage(models.Model):
    product = models.ForeignKey(
        Product,
        related_name="images",
        on_delete=models.CASCADE
    )
    image = models.ImageField(
        upload_to="products/",
        verbose_name="Imagen"
    )
    order = models.PositiveIntegerField(
        default=0,
        verbose_name="Orden"
    )

    class Meta:
        ordering = ["order"]
        verbose_name = "Imagen de producto"
        verbose_name_plural = "Imágenes de producto"

    def __str__(self):
        return f"Imagen {self.order} - {self.product.name}"
    

#-- Links de compra --#
class ProductLink(models.Model):
    LINK_CHOICES = (
        ("whatsapp", "WhatsApp"),
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
    
    def clean(self):
        if self.link_type == "external":
            if not self.url:
                raise ValidationError({
                    "url": "Campo obligatorio."
                })
            if not self.button_text:
                raise ValidationError({
                    "button_text": "Campo obligatorio."
                })
            
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