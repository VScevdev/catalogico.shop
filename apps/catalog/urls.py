from django.urls import path
from .views import *

app_name = "catalog"

urlpatterns = [
    path("", catalog_view, name="catalog"),
    path("producto/<slug:slug>/", product_detail_view, name="product_detail"),
    path("sucursales/", branches_public_view, name="branches_public"),
    path("carrito/", cart_detail_view, name="cart_detail"),
    path("carrito/agregar/", cart_add_view, name="cart_add"),
    path("carrito/quitar/", cart_remove_view, name="cart_remove"),
    path("carrito/actualizar/", cart_update_view, name="cart_update"),

    path("privacy", privacy_view, name="privacy"),

    path("configuracion/", config_panel_view, name="store_config"),
    path("configuracion/apariencia/", store_config_view, name="store_config_appearance"),
    path("configuracion/informacion-contacto/", store_info_contact_view, name="store_config_info_contact"),
    path("configuracion/mensajes-personalizados/", store_custom_messages_view, name="store_custom_messages"),
    path("configuracion/sucursales/", branch_list_view, name="branch_list"),
    path("configuracion/sucursales/crear/", branch_create_view, name="branch_create"),
    path("configuracion/sucursales/<int:pk>/editar/", branch_update_view, name="branch_update"),
    path("configuracion/sucursales/<int:pk>/eliminar/", branch_delete_view, name="branch_delete"),
    path("categorias/", category_list_view, name="category_list"),
    path("categorias/crear/", category_create_view, name="category_create"),
    path("categorias/<int:pk>/editar/", category_update_view, name="category_update"),
    path("categorias/<int:pk>/eliminar/", category_delete_view, name="category_delete"),

    path("productos/", product_list_view, name="product_list"),
    path("productos/crear/", product_create_view, name="product_create"),
    path("productos/<int:pk>/editar/", product_update_view, name="product_update"),
    path("productos/<int:pk>/eliminar/", product_delete_view, name="product_delete"),
    path("productos/<int:product_id>/media/upload/", product_media_upload_view, name="product_media_upload"),
    path("productos/<int:pk>/publicar/", product_publish_view, name="product_publish"),
    path("productos/<int:pk>/borrador/", product_draft_view, name="product_draft"),
    path("productos/<int:pk>/cancelar/", product_cancel_view, name="product_cancel"),
]
