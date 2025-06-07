from djmoney.contrib.django_rest_framework import MoneyField
from rest_framework import serializers

from wms.models import Product


class ProductSerializer(serializers.ModelSerializer):
    purchase_price = MoneyField(max_digits=10, decimal_places=2, default_currency="UAH")
    selling_price = MoneyField(max_digits=10, decimal_places=2, default_currency="UAH")

    class Meta:
        model = Product
        fields = "__all__"
