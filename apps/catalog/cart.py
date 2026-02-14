"""
Helpers para el carrito guardado en sesión Django.
Estructura: session['cart'] = { str(store_id): { str(product_id): quantity } }
Siempre usamos claves string para coincidir con la serialización JSON de la sesión
y así no crear dos entradas (int vs str) para la misma tienda.
"""
from typing import Dict, Any

CART_KEY = "cart"
MAX_QUANTITY = 99
MAX_ITEMS = 50


def _normalize_cart(raw: Dict) -> Dict[int, int]:
    """Convierte keys a int para devolver al resto del código."""
    if not raw:
        return {}
    return {int(k): int(v) for k, v in raw.items() if int(v) > 0}


def get_cart_for_store(session: Any, store_id: int) -> Dict[int, int]:
    """Devuelve el carrito de la tienda: { product_id: quantity }."""
    cart = session.get(CART_KEY) or {}
    store_key = str(store_id)
    store_cart = cart.get(store_key) or {}
    return _normalize_cart(store_cart)


def cart_count_for_store(session: Any, store_id: int) -> int:
    """Suma de cantidades del carrito de esa tienda."""
    store_cart = get_cart_for_store(session, store_id)
    return sum(store_cart.values())


def add_to_cart(
    session: Any,
    store_id: int,
    product_id: int,
    quantity: int = 1,
) -> None:
    """Añade o suma cantidad al carrito. Limita por MAX_QUANTITY y MAX_ITEMS."""
    if quantity <= 0:
        return
    quantity = min(quantity, MAX_QUANTITY)
    if CART_KEY not in session:
        session[CART_KEY] = {}
    store_key = str(store_id)
    product_key = str(product_id)
    if store_key not in session[CART_KEY]:
        session[CART_KEY][store_key] = {}
    store_cart = session[CART_KEY][store_key]
    # Limitar líneas distintas
    if product_key not in store_cart and len(store_cart) >= MAX_ITEMS:
        return
    current = store_cart.get(product_key) or 0
    store_cart[product_key] = min(current + quantity, MAX_QUANTITY)
    session.modified = True


def remove_from_cart(session: Any, store_id: int, product_id: int) -> None:
    """Quita un ítem del carrito."""
    cart = session.get(CART_KEY) or {}
    store_key = str(store_id)
    product_key = str(product_id)
    if store_key not in cart:
        return
    store_cart = cart[store_key]
    if product_key in store_cart:
        del store_cart[product_key]
        session.modified = True


def update_cart(
    session: Any,
    store_id: int,
    product_id: int,
    quantity: int,
) -> None:
    """Actualiza cantidad; si <= 0, quita el ítem."""
    if quantity <= 0:
        remove_from_cart(session, store_id, product_id)
        return
    quantity = min(quantity, MAX_QUANTITY)
    if CART_KEY not in session:
        session[CART_KEY] = {}
    store_key = str(store_id)
    product_key = str(product_id)
    if store_key not in session[CART_KEY]:
        session[CART_KEY][store_key] = {}
    session[CART_KEY][store_key][product_key] = quantity
    session.modified = True


def set_cart_for_store(session: Any, store_id: int, store_cart: Dict[int, int]) -> None:
    """Sobrescribe el carrito de la tienda (para limpieza de ítems inválidos)."""
    if CART_KEY not in session:
        session[CART_KEY] = {}
    store_key = str(store_id)
    session[CART_KEY][store_key] = {
        str(k): int(v) for k, v in store_cart.items() if v > 0
    }
    session.modified = True
