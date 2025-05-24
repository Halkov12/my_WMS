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
    pass


@admin.register(StockOperation)
class StockOperationAdmin(admin.ModelAdmin):
    pass


@admin.register(StockOperationItem)
class StockOperationItemAdmin(admin.ModelAdmin):
    pass


@admin.register(ChangeLog)
class ChangeLogAdmin(admin.ModelAdmin):
    pass
