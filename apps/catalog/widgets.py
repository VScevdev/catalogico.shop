from django.forms import ClearableFileInput


class StoreConfigLogoInput(ClearableFileInput):
    """Widget para el logo: sin URL visible, solo checkbox eliminar y input archivo."""
    template_name = "forms/widgets/store_config_logo.html"
