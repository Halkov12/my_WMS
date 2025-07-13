from django.contrib import admin
from accounts.models import Customer
@admin.register(Customer)
class CustomerAdmin(admin.ModelAdmin):
    list_display = ["email", "first_name", "last_name", "role", "is_active", "date_joined"]
    list_filter = ["role", "is_active", "is_staff", "date_joined"]
    search_fields = ["email", "first_name", "last_name"]
    ordering = ["-date_joined"]
    fieldsets = (
        (
            "Основна інформація",
            {"fields": ("email", "first_name", "last_name", "phone_number", "birth_date", "photo", "role")},
        ),
        ("Робоча інформація", {"fields": ("position", "department")}),
        ("Права доступу", {"fields": ("is_active", "is_staff", "is_superuser", "groups", "user_permissions")}),
        ("Важливі дати", {"fields": ("date_joined", "last_login_date", "total_logins", "profile_views")}),
    )
    readonly_fields = [
        "date_joined",
        "last_login_date",
        "total_logins",
        "profile_views",
    ]