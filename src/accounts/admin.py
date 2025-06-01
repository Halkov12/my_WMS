from django.contrib import admin

from accounts.models import Customer


@admin.register(Customer)
class ProductAdmin(admin.ModelAdmin):
    pass
