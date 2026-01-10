from django.urls import path
from .views import catalog_view, product_detail_view, privacy_view

app_name = "catalog"

urlpatterns = [
    path("", catalog_view, name="catalog"),
    path("producto/<slug:slug>/", product_detail_view, name="product_detail"),
    path("privacy", privacy_view, name="privacy")
]
