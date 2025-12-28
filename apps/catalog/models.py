from django.db import models
from django.utils.text import slugify

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

    class Meta:
        ordering = ["name"]
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
    

#-- Thumbnail --#
@property
def thumbnail(self):
    return self.images.order_by("order").first()

#-- Links de compra --#
class ProductLink(models.Model):
    LINK_CHOICES = (
        ("whatsapp", "WhatsApp"),
        ("instagram", "Instagram"),
        ("mercadolibre", "MercadoLibre"),
        ("external", "Externo"),
    )

    product = models.ForeignKey(
        Product,
        related_name="links",
        on_delete=models.CASCADE
    )
    link_type = models.CharField(
        max_length=20,
        choices=LINK_CHOICES,
        verbose_name="Tipo de link"
    )
    url = models.URLField(
        verbose_name="URL"
    )
    button_text = models.CharField(
        max_length=100,
        verbose_name="Texto del botón"
    )
    order = models.PositiveIntegerField(
        default=0,
        verbose_name="Orden"
    )

    class Meta:
        ordering = ["order"]
        verbose_name = "Link de producto"
        verbose_name_plural = "Links de producto"

    def __str__(self):
        return f"{self.product.name} - {self.link_type}"