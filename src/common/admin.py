from django.contrib import admin  # NOQA:F401

from common.models import Setting


# Register your models here.

@admin.register(Setting)
class StockOperationAdmin(admin.ModelAdmin):
    list_display = ["key", "value"]
