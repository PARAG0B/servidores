from django.contrib import admin
from .models import Warehouse, Product, Stock, Movement


@admin.register(Warehouse)
class WarehouseAdmin(admin.ModelAdmin):
    list_display = ("name", "location")
    search_fields = ("name", "location")


@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    list_display = ("code", "name", "unit", "min_stock", "is_active")
    list_filter = ("is_active",)
    search_fields = ("code", "name")


@admin.register(Stock)
class StockAdmin(admin.ModelAdmin):
    list_display = ("product", "warehouse", "quantity")
    list_filter = ("warehouse", "product")
    search_fields = ("product__name", "product__code", "warehouse__name")


@admin.register(Movement)
class MovementAdmin(admin.ModelAdmin):
    list_display = ("product", "movement_type", "quantity", "warehouse_from", "warehouse_to", "created_at", "user")
    list_filter = ("movement_type", "warehouse_from", "warehouse_to", "created_at")
    search_fields = ("product__name", "product__code", "user__username")
    date_hierarchy = "created_at"

