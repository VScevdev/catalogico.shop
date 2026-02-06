from django.conf import settings
from django.http import HttpResponseNotFound
from django.utils.deprecation import MiddlewareMixin

from .models import Store


class TenantMiddleware(MiddlewareMixin):
    """
    Extrae el subdominio del host y resuelve la tienda (Store).
    Estructura: {slug}.catalogico.shop → slug
    """

    def process_request(self, request):
        request.store = None

        host = request.get_host().split(":")[0].lower()
        root_domain = getattr(settings, "ROOT_DOMAIN", "catalogico.shop").lower()

        # Si el host es exactamente el dominio raíz o www.dominio_raíz → landing
        if host == root_domain or host == f"www.{root_domain}":
            return None  # Continuar; la vista de landing manejará

        # Si el host termina en .{root_domain}, extraer el subdominio
        suffix = f".{root_domain}"
        if host.endswith(suffix):
            subdomain = host[: -len(suffix)]
            if subdomain and subdomain != "www":
                try:
                    store = Store.objects.get(slug=subdomain, is_active=True)
                    request.store = store
                except Store.DoesNotExist:
                    return HttpResponseNotFound("Tienda no encontrada")

        return None
