from django.db import models
from django.db.models.signals import post_delete, post_save
from django.dispatch import receiver
from django.utils.translation import gettext_lazy as _


class BaseModel(models.Model):
    class Meta:
        abstract = True

    created_at = models.DateTimeField(_("Created at"), auto_now_add=True, null=True)
    updated_at = models.DateTimeField(_("Updated at"), auto_now=True, null=True)


class Setting(models.Model):
    key = models.CharField(_("Key"), max_length=100, unique=True)
    value = models.CharField(_("Value"), max_length=255)

    class Meta:
        verbose_name = _("Setting")
        verbose_name_plural = _("Settings")

    def __str__(self):
        return self.key


@receiver(post_save, sender=Setting)
def log_setting_save(sender, instance, created, **kwargs):
    from wms.models import ChangeLog

    user = getattr(instance, "_log_user", None)
    action = "Setting created" if created else "Setting modified"
    ChangeLog.objects.create(
        user=user,
        action=action,
        details={
            "key": instance.key,
            "value": instance.value,
        },
    )


@receiver(post_delete, sender=Setting)
def log_setting_delete(sender, instance, **kwargs):
    from wms.models import ChangeLog

    user = getattr(instance, "_log_user", None)
    ChangeLog.objects.create(
        user=user,
        action="Setting deleted",
        details={
            "key": instance.key,
            "value": instance.value,
        },
    )
