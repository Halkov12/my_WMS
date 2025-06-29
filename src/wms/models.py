from django.contrib.auth import get_user_model
from django.core.exceptions import ValidationError
from django.db import models  # NOQA:F401
from django.db.models.signals import post_delete, pre_save
from django.dispatch import receiver
from djmoney.models.fields import MoneyField

from common.models import BaseModel


class Category(models.Model):
    name = models.CharField("Назва категорії", max_length=100)

    class Meta:
        verbose_name = "Категорія"
        verbose_name_plural = "Категорії"

    def __str__(self):
        return self.name


class UNIT_CHOICES(models.IntegerChoices):
    PIECES = 1, "шт"
    KILOGRAMS = 2, "кг"
    LITER = 3, "л"
    GRAM = 4, "г"


class Product(BaseModel):
    name = models.CharField("Назва товару", max_length=255)
    barcode = models.CharField("Штрихкод", max_length=100, blank=True, unique=True)
    purchase_price = MoneyField("Закупівельна ціна", max_digits=10, decimal_places=2, null=True, blank=True, default_currency="UAH")
    selling_price = MoneyField("Ціна продажу", max_digits=10, decimal_places=2, null=True, blank=True, default_currency="UAH")
    unit = models.SmallIntegerField("Одиниця виміру", choices=UNIT_CHOICES, default=UNIT_CHOICES.PIECES)
    quantity = models.DecimalField("Кількість", max_digits=10, decimal_places=2, default=0)
    is_active = models.BooleanField("Активний", default=True)
    category = models.ForeignKey(
        "wms.Category",
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        verbose_name="Категорія"
    )
    photo = models.ImageField(upload_to="img/products/", null=True, blank=True, verbose_name="Фото")
    description = models.TextField(blank=True, verbose_name="Опис")

    class Meta:
        verbose_name = "Товар"
        verbose_name_plural = "Товари"

    def __str__(self):
        return f"{self.name} {self.selling_price} {self.quantity}"

    def clean(self):
        super().clean()
        if self.photo:
            if self.photo.size > 2 * 1024 * 1024:
                raise ValidationError("Максимальний розмір фото — 2 МБ.")
            if not self.photo.file.content_type.startswith("image/"):
                raise ValidationError("Можна завантажувати лише зображення.")


class OPERATION_CHOICES(models.IntegerChoices):
    RECEIPT = 1, "Прийом"
    ISSUE = 2, "Видача"
    WRITE_OFF = 3, "Списання"


class StockOperation(BaseModel):
    operation_type = models.SmallIntegerField("Тип операції", choices=OPERATION_CHOICES, default=OPERATION_CHOICES.RECEIPT)
    created_by = models.ForeignKey(get_user_model(), on_delete=models.SET_NULL, null=True, verbose_name="Користувач")
    reason = models.CharField("Причина", max_length=255, blank=True)
    note = models.TextField("Примітка", blank=True)

    class Meta:
        verbose_name = "Операція"
        verbose_name_plural = "Операції"

    def __str__(self):
        return f"{self.operation_type} {self.created_by} {self.reason}"


class StockOperationItem(models.Model):
    operation = models.ForeignKey("wms.StockOperation", related_name="items", on_delete=models.CASCADE, verbose_name="Операція")
    product = models.ForeignKey(Product, on_delete=models.CASCADE, verbose_name="Товар")
    quantity = models.DecimalField("Кількість", max_digits=10, decimal_places=2)

    class Meta:
        verbose_name = "Позиція операції"
        verbose_name_plural = "Позиції операцій"

    def __str__(self):
        return f"{self.operation} {self.product} {self.quantity}"


class ChangeLog(BaseModel):
    user = models.ForeignKey(get_user_model(), on_delete=models.SET_NULL, null=True, verbose_name="Користувач")
    action = models.CharField("Дія", max_length=255)
    product = models.ForeignKey("wms.Product", null=True, blank=True, on_delete=models.SET_NULL, verbose_name="Товар")
    details = models.JSONField("Деталі", null=True, blank=True)

    class Meta:
        verbose_name = "Журнал змін"
        verbose_name_plural = "Журнали змін"

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
