from django.urls import path
from .views import test_secure

urlpatterns = [
    path("test-secure/", test_secure),
]