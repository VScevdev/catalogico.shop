from django.conf import settings
from django.contrib.auth.views import LoginView as BaseLoginView
from django.shortcuts import redirect
from django.urls import reverse


class LoginView(BaseLoginView):
    """Login que redirige al subdominio de la tienda del usuario (si es owner)."""

    template_name = "accounts/login.html"

    def get_success_url(self):
        next_url = self.request.GET.get("next", "")
        user = self.request.user

        # Si el usuario es owner y tiene tienda, redirigir a su subdominio
        if hasattr(user, "store") and user.store:
            store = user.store
            root = getattr(settings, "ROOT_DOMAIN", "catalogico.shop")
            port = ""
            host = self.request.get_host()
            if ":" in host:
                port = ":" + host.split(":")[-1]
            base = f"{self.request.scheme}://{store.slug}.{root}{port}"
            if next_url and next_url.startswith("/"):
                return f"{base}{next_url}"
            return f"{base}/"

        # Usuario sin tienda: mantener comportamiento por defecto
        if next_url:
            return next_url
        return reverse("catalog:catalog")
