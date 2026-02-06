from django.db import models


class Store(models.Model):
    name = models.CharField(max_length=150, verbose_name="Nombre")
    slug = models.SlugField(
        max_length=100,
        unique=True,
        verbose_name="Slug (subdominio)"
    )
    owner = models.OneToOneField(
        "accounts.User",
        on_delete=models.CASCADE,
        related_name="store",
        verbose_name="Dueño"
    )
    is_active = models.BooleanField(default=True, verbose_name="Activa")
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = "Tienda"
        verbose_name_plural = "Tiendas"
        ordering = ["name"]

    def __str__(self):
        return self.name
