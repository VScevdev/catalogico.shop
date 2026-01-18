from django.urls import path
from .views import catalog_view, product_detail_view, privacy_view, category_list_view, category_create_view, category_update_view, category_delete_view

app_name = "catalog"

urlpatterns = [
    path("", catalog_view, name="catalog"),
    path("producto/<slug:slug>/", product_detail_view, name="product_detail"),
    path("privacy", privacy_view, name="privacy"),
    path("categories/", category_list_view, name="category_list"),
    path("categories/create/", category_create_view, name="category_create"),
    path("categories/<int:pk>/edit/", category_update_view, name="category_update"),
    path("categories/<int:pk>/delete/", category_delete_view, name="category_delete"),
]
