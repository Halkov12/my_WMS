from django.contrib import admin

from .models import (Category, ChangeLog, Product, StockOperation,
                     StockOperationItem)


@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    list_display = ["name", "category", "quantity", "unit", "is_active"]
    list_filter = ["category", "is_active"]
    search_fields = ["name", "barcode"]


@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ["name"]
    list_filter = ["name"]
    search_fields = ["name"]


@admin.register(StockOperation)
class StockOperationAdmin(admin.ModelAdmin):
    list_display = ["operation_type", "created_by", "reason"]
    list_filter = ["operation_type", "created_by"]
    search_fields = ["operation_type"]


@admin.register(StockOperationItem)
class StockOperationItemAdmin(admin.ModelAdmin):
    list_display = ["operation", "product", "quantity"]
    list_filter = ["operation", "product"]


@admin.register(ChangeLog)
class ChangeLogAdmin(admin.ModelAdmin):
    list_display = ["user", "action", "product"]
    list_filter = ["user", "action"]
