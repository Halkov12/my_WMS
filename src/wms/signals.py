from django.contrib.auth import get_user_model
from django.db.models.signals import post_delete, post_save, pre_save
from django.dispatch import receiver
from wms.models import ChangeLog, Notification, Product, StockOperation
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
@receiver(post_save, sender=Product)
def log_product_save(sender, instance, created, **kwargs):
    user = getattr(instance, "_log_user", None)
    action = "Product created" if created else "Product modified"
    ChangeLog.objects.create(
        user=user,
        action=action,
        product=instance,
        details={
            "name": instance.name,
            "barcode": instance.barcode,
            "quantity": str(instance.quantity),
            "selling_price": str(instance.selling_price),
        },
    )
@receiver(post_delete, sender=Product)
def log_product_delete(sender, instance, **kwargs):
    user = getattr(instance, "_log_user", None)
    ChangeLog.objects.create(
        user=user,
        action="Product deleted",
        details={
            "name": instance.name,
            "barcode": instance.barcode,
            "quantity": str(instance.quantity),
            "selling_price": str(instance.selling_price),
        },
    )
@receiver(post_save, sender=StockOperation)
def log_operation_save(sender, instance, created, **kwargs):
    user = getattr(instance, "_log_user", None)
    action = "Operation created"
    ChangeLog.objects.create(
        user=user,
        action=action,
        details={
            "operation_type": instance.get_operation_type_display(),
            "reason": instance.reason,
            "note": instance.note,
        },
    )
@receiver(post_delete, sender=StockOperation)
def log_operation_delete(sender, instance, **kwargs):
    user = getattr(instance, "_log_user", None)
    ChangeLog.objects.create(
        user=user,
        action="Operation deleted",
        details={
            "operation_type": instance.get_operation_type_display(),
            "reason": instance.reason,
            "note": instance.note,
        },
    )
@receiver(post_save, sender=Product)
def create_product_notification(sender, instance, created, **kwargs):
    if created:
        Notification.objects.create(
            type=1,
            message=f"New product added: {instance.name}",
            user=instance._log_user if hasattr(instance, "_log_user") else None,
        )