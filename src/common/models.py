from django.db import models


class BaseModel(models.Model):
    class Meta:
        abstract = True

    created_at = models.DateTimeField("Дата створення", auto_now_add=True, null=True)
    updated_at = models.DateTimeField("Дата оновлення", auto_now=True, null=True)


class Setting(models.Model):
    key = models.CharField("Ключ", max_length=100, unique=True)
    value = models.CharField("Значення", max_length=255)

    class Meta:
        verbose_name = "Налаштування"
        verbose_name_plural = "Налаштування"

    def __str__(self):
        return self.key
