from django.contrib.auth import get_user_model
from django.db import models  # NOQA:F401

from common.models import BaseModel


class Category(models.Model):
    name = models.CharField(max_length=100)

    def __str__(self):
        return self.name


class UNIT_CHOICES(models.IntegerChoices):
    PIECES = 0, "pcs"
    KILOGRAMS = 1, "kgs"
    LITER = 2, "lt"
    GRAM = 3, "g"


class Product(BaseModel):
    name = models.CharField(max_length=255)
    barcode = models.CharField(max_length=100, blank=True, unique=True)
    purchase_price = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    selling_price = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    unit = models.SmallIntegerField(choices=UNIT_CHOICES, default=UNIT_CHOICES.PIECES)
    quantity = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    is_active = models.BooleanField(default=True)
    category = models.ForeignKey(
        "wms.Category",
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
    )

    def __str__(self):
        return f"{self.name} {self.selling_price} {self.quantity}"


class OPERATION_CHOICES(models.IntegerChoices):
    RECEIPT = 0, "receipt"
    ISSUE = 1, "issue"
    WRITE_OFF = 2, "write off"


class StockOperation(BaseModel):
    operation_type = models.SmallIntegerField(choices=OPERATION_CHOICES, default=OPERATION_CHOICES.RECEIPT)
    created_by = models.ForeignKey(get_user_model(), on_delete=models.SET_NULL, null=True)
    reason = models.CharField(max_length=255, blank=True)
    note = models.TextField(blank=True)

    def __str__(self):
        return f"{self.operation_type} {self.created_by} {self.reason}"


class StockOperationItem(models.Model):
    operation = models.ForeignKey("wms.StockOperation", related_name="items", on_delete=models.CASCADE)
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    quantity = models.DecimalField(max_digits=10, decimal_places=2)

    def __str__(self):
        return f"{self.operation} {self.product} {self.quantity}"


class ChangeLog(BaseModel):
    user = models.ForeignKey(get_user_model(), on_delete=models.SET_NULL, null=True)
    action = models.CharField(max_length=255)
    product = models.ForeignKey("wms.Product", null=True, blank=True, on_delete=models.SET_NULL)
    details = models.JSONField(null=True, blank=True)

    def __str__(self):
        return f"{self.action} {self.product}"
