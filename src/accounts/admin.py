from django.contrib import admin  # NOQA:F401

from accounts.models import Customer


# Register your models here.
@admin.register(Customer)
class ProductAdmin(admin.ModelAdmin):
    ...
