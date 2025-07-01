from djmoney.contrib.django_rest_framework import MoneyField
from rest_framework import serializers

from accounts.models import Customer
from wms.models import Product


class ProductSerializer(serializers.ModelSerializer):
    purchase_price = MoneyField(max_digits=10, decimal_places=2, default_currency="UAH")
    selling_price = MoneyField(max_digits=10, decimal_places=2, default_currency="UAH")

    class Meta:
        model = Product
        fields = "__all__"


class ProductDetailSerializer(serializers.ModelSerializer):
    category_name = serializers.CharField(source="category.name", default="-")
    unit = serializers.CharField(source="get_unit_display")
    photo = serializers.ImageField(use_url=True)

    class Meta:
        model = Product
        fields = [
            "id",
            "name",
            "photo",
            "category_name",
            "barcode",
            "quantity",
            "unit",
            "purchase_price",
            "selling_price",
            "created_at",
        ]


class UserRoleSerializer(serializers.ModelSerializer):
    role_display = serializers.CharField(source="get_role_display")

    class Meta:
        model = Customer
        fields = ["id", "email", "first_name", "last_name", "role", "role_display"]