from django.contrib import admin
from .models import Warehouse, Product, Stock, Movement


@admin.register(Warehouse)
class WarehouseAdmin(admin.ModelAdmin):
    list_display = ("code", "name", "location", "is_active")
    list_filter = ("is_active",)
    search_fields = ("code", "name", "location")


@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    list_display = ("sku", "name", "unit", "is_active")
    list_filter = ("is_active",)
    search_fields = ("sku", "name")


@admin.register(Stock)
class StockAdmin(admin.ModelAdmin):
    list_display = ("warehouse", "product", "quantity")
    list_filter = ("warehouse", "product")
    search_fields = ("warehouse__name", "product__name", "product__sku")


@admin.register(Movement)
class MovementAdmin(admin.ModelAdmin):
    list_display = (
        "created_at",
        "movement_type",
        "product",
        "warehouse",
        "quantity",
        "reference",
    )
    list_filter = ("movement_type", "warehouse", "product")
    search_fields = ("product__name", "product__sku", "reference", "notes")
    date_hierarchy = "created_at"

