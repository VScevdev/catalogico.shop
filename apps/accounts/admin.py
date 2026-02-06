from django.contrib import admin
from .models import User

@admin.register(User)
class UserAdmin(admin.ModelAdmin):
    list_display = ("username", "email", "is_owner", "is_staff", "is_active")
    list_filter = ("is_owner", "is_staff", "is_active")
    search_fields = ("username", "email")