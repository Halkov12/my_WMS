from django.contrib import admin

from common.models import Setting


@admin.register(Setting)
class StockOperationAdmin(admin.ModelAdmin):
    list_display = ["key", "value"]
