from django.core.exceptions import PermissionDenied
from django.shortcuts import redirect
from functools import wraps


def owner_required(view_func):
    @wraps(view_func)
    def _wrapped_view(request, *args, **kwargs):
        store = getattr(request, "store", None)
        if not store:
            raise PermissionDenied("No hay tienda en contexto.")
        if not request.user.is_authenticated:
            return redirect("accounts:login")
        if not hasattr(request.user, "store") or request.user.store != store:
            raise PermissionDenied("No tienes permiso para administrar esta tienda.")
        return view_func(request, *args, **kwargs)
    return _wrapped_view