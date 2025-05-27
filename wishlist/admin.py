from django.contrib import admin
from .models import Wishlist, Wish
# Register your models here.


@admin.register(Wishlist)
class WishlistAdmin(admin.ModelAdmin):
    """
    Admin interface for the Wishlist model.
    """
    list_display = ("user", "title", "created_at")
    search_fields = ("title",)
    list_filter = ("created_at",)
    ordering = ("-created_at",)


@admin.register(Wish)
class WishAdmin(admin.ModelAdmin):
    """
    Admin interface for the Wish model.
    """
    list_display = ("wishlist", "item_name", "item_price", "created_at")
    search_fields = ("item_name",)
    list_filter = ("created_at",)
    ordering = ("-created_at",)