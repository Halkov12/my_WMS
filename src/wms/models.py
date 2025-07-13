from django.contrib.auth import get_user_model
from django.core.exceptions import ValidationError
from django.db import models
from django.utils.translation import gettext_lazy as _
from djmoney.models.fields import MoneyField

from common.models import BaseModel


class Category(models.Model):
    name = models.CharField(_("Category name"), max_length=100)

    class Meta:
        verbose_name = _("Category")
        verbose_name_plural = _("Categories")

    def __str__(self):
        return self.name


class UNIT_CHOICES(models.IntegerChoices):
    PIECES = 1, _("pcs")
    KILOGRAMS = 2, _("kg")
    LITER = 3, _("l")
    GRAM = 4, _("g")


class Product(BaseModel):
    name = models.CharField(_("Product name"), max_length=255)
    barcode = models.CharField(_("Barcode"), max_length=100, blank=True, unique=True)
    purchase_price = MoneyField(
        _("Purchase price"),
        max_digits=10,
        decimal_places=2,
        null=True,
        blank=True,
        default_currency="UAH",
    )
    selling_price = MoneyField(
        _("Selling price"),
        max_digits=10,
        decimal_places=2,
        null=True,
        blank=True,
        default_currency="UAH",
    )
    unit = models.SmallIntegerField(_("Unit of measurement"), choices=UNIT_CHOICES, default=UNIT_CHOICES.PIECES)
    quantity = models.DecimalField(_("Quantity"), max_digits=10, decimal_places=2, default=0)
    min_quantity = models.DecimalField(_("Minimum stock"), max_digits=10, decimal_places=2, default=5)
    is_active = models.BooleanField(_("Active"), default=True)
    category = models.ForeignKey(
        "wms.Category",
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        verbose_name=_("Category"),
    )
    photo = models.ImageField(upload_to="img/products/", null=True, blank=True, verbose_name=_("Photo"))
    description = models.TextField(blank=True, verbose_name=_("Description"))

    class Meta:
        verbose_name = _("Product")
        verbose_name_plural = _("Products")
        indexes = [
            models.Index(fields=["barcode"]),
            models.Index(fields=["category"]),
        ]

    def __str__(self):
        return f"{self.name} {self.selling_price} {self.quantity}"

    def clean(self):
        super().clean()
        if self.photo:
            if self.photo.size > 2 * 1024 * 1024:
                raise ValidationError(_("Maximum photo size is 2 MB."))
            if not self.photo.file.content_type.startswith("image/"):
                raise ValidationError(_("Only images can be uploaded."))


class OPERATION_CHOICES(models.IntegerChoices):
    RECEIPT = 1, _("Receipt")
    ISSUE = 2, _("Issue")
    WRITE_OFF = 3, _("Write-off")


class StockOperation(BaseModel):
    operation_type = models.SmallIntegerField(
        _("Operation type"), choices=OPERATION_CHOICES, default=OPERATION_CHOICES.RECEIPT
    )
    created_by = models.ForeignKey(
        get_user_model(),
        on_delete=models.SET_NULL,
        null=True,
        verbose_name=_("User"),
    )
    reason = models.CharField(_("Reason"), max_length=255, blank=True)
    note = models.TextField(_("Note"), blank=True)

    class Meta:
        verbose_name = _("Operation")
        verbose_name_plural = _("Operations")

    def __str__(self):
        return f"{self.operation_type} {self.created_by} {self.reason}"


class StockOperationItem(models.Model):
    operation = models.ForeignKey(
        "wms.StockOperation",
        related_name="items",
        on_delete=models.CASCADE,
        verbose_name=_("Operation"),
    )
    product = models.ForeignKey(Product, on_delete=models.CASCADE, verbose_name=_("Product"))
    quantity = models.DecimalField(_("Quantity"), max_digits=10, decimal_places=2)

    class Meta:
        verbose_name = _("Operation item")
        verbose_name_plural = _("Operation items")
        indexes = [
            models.Index(fields=["product"]),
            models.Index(fields=["operation"]),
        ]

    def __str__(self):
        return f"{self.operation} {self.product} {self.quantity}"


class ChangeLog(BaseModel):
    user = models.ForeignKey(
        get_user_model(),
        on_delete=models.SET_NULL,
        null=True,
        verbose_name=_("User"),
    )
    action = models.CharField(_("Action"), max_length=255)
    product = models.ForeignKey(
        "wms.Product",
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        verbose_name=_("Product"),
    )
    details = models.JSONField(_("Details"), null=True, blank=True)

    class Meta:
        verbose_name = _("Change log")
        verbose_name_plural = _("Change logs")

    def __str__(self):
        return f"{self.action} {self.product}"


class Notification(models.Model):
    TYPE_CHOICES = [
        (1, _("New product")),
        (2, _("Product receipt")),
        (3, _("Product issue")),
        (4, _("Write-off")),
        (5, _("New user")),
        (6, _("Other")),
    ]
    type = models.PositiveSmallIntegerField(choices=TYPE_CHOICES)
    message = models.CharField(max_length=255)
    created_at = models.DateTimeField(auto_now_add=True)
    user = models.ForeignKey("accounts.Customer", null=True, blank=True, on_delete=models.SET_NULL)
    is_read = models.BooleanField(default=False)

    class Meta:
        ordering = ["-created_at"]

    def __str__(self):
        return self.message


class Inventory(models.Model):
    date = models.DateTimeField(_("Inventory date"), auto_now_add=True)
    user = models.ForeignKey(get_user_model(), on_delete=models.SET_NULL, null=True, verbose_name=_("User"))
    note = models.TextField(_("Note"), blank=True)

    class Meta:
        verbose_name = _("Inventory")
        verbose_name_plural = _("Inventories")

    def __str__(self):
        return f"Інвентаризація від {self.date:%Y-%m-%d %H:%M}"


class InventoryItem(models.Model):
    inventory = models.ForeignKey(
        Inventory, related_name="items", on_delete=models.CASCADE, verbose_name=_("Inventory")
    )
    product = models.ForeignKey(Product, on_delete=models.CASCADE, verbose_name=_("Product"))
    actual_quantity = models.DecimalField(_("Actual quantity"), max_digits=10, decimal_places=2)

    class Meta:
        verbose_name = _("Inventory item")
        verbose_name_plural = _("Inventory items")
        indexes = [
            models.Index(fields=["product"]),
            models.Index(fields=["inventory"]),
        ]

    def __str__(self):
        return f"{self.product} ({self.actual_quantity})"
