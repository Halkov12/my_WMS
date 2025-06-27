from django.contrib.auth import get_user_model
from django.db import models  # NOQA:F401
from djmoney.models.fields import MoneyField
from django.core.exceptions import ValidationError
from django.db.models.signals import pre_save, post_delete
from django.dispatch import receiver

from common.models import BaseModel


class Category(models.Model):
    name = models.CharField(max_length=100)

    def __str__(self):
        return self.name


class UNIT_CHOICES(models.IntegerChoices):
    PIECES = 1, "шт"
    KILOGRAMS = 2, "кг"
    LITER = 3, "л"
    GRAM = 4, "г"


class Product(BaseModel):
    name = models.CharField(max_length=255)
    barcode = models.CharField(max_length=100, blank=True, unique=True)
    purchase_price = MoneyField(max_digits=10, decimal_places=2, null=True, blank=True, default_currency="UAH")
    selling_price = MoneyField(max_digits=10, decimal_places=2, null=True, blank=True, default_currency="UAH")
    unit = models.SmallIntegerField(choices=UNIT_CHOICES, default=UNIT_CHOICES.PIECES)
    quantity = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    is_active = models.BooleanField(default=True)
    category = models.ForeignKey(
        "wms.Category",
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
    )
    photo = models.ImageField(upload_to='img/products/', null=True, blank=True, verbose_name='Фото')
    description = models.TextField(blank=True, verbose_name='Опис')

    def __str__(self):
        return f"{self.name} {self.selling_price} {self.quantity}"

    def clean(self):
        super().clean()
        if self.photo:
            if self.photo.size > 2*1024*1024:
                raise ValidationError('Максимальний розмір фото — 2 МБ.')
            if not self.photo.file.content_type.startswith('image/'):
                raise ValidationError('Можна завантажувати лише зображення.')


class OPERATION_CHOICES(models.IntegerChoices):
    RECEIPT = 1, "receipt"
    ISSUE = 2, "issue"
    WRITE_OFF = 3, "write off"


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


@receiver(post_delete, sender=Product)
def delete_product_photo(sender, instance, **kwargs):
    if instance.photo:
        instance.photo.delete(save=False)


@receiver(pre_save, sender=Product)
def auto_delete_old_photo_on_change(sender, instance, **kwargs):
    if not instance.pk:
        return
    try:
        old_photo = Product.objects.get(pk=instance.pk).photo
    except Product.DoesNotExist:
        return
    new_photo = instance.photo
    if old_photo and old_photo != new_photo:
        old_photo.delete(save=False)
