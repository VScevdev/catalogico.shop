from django.urls import path
from .views import *

app_name = "catalog"

urlpatterns = [
    path("", catalog_view, name="catalog"),
    path("producto/<slug:slug>/", product_detail_view, name="product_detail"),

    path("privacy", privacy_view, name="privacy"),

    path("categorias/", category_list_view, name="category_list"),
    path("categorias/crear/", category_create_view, name="category_create"),
    path("categorias/<int:pk>/editar/", category_update_view, name="category_update"),
    path("categorias/<int:pk>/eliminar/", category_delete_view, name="category_delete"),

    path("productos/", product_list_view, name="product_list"),
    path("productos/crear/", product_create_view, name="product_create"),
    path("productos/<int:pk>/editar/", product_update_view, name="product_update"),
    path("productos/<int:pk>/eliminar/", product_delete_view, name="product_delete"),
    path("productos/<int_product_id>/media/upload", product_media_upload_view, name="product_media_upload")
]
