from django import template

register = template.Library()

@register.filter
def ars(value):
    try:
        value = int(value)
        return f"{value:,.2f}".replace(",", "X").replace(".", ",").replace("X", ".")
    except Exception:
        return value