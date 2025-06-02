from common.models import Setting  # або ваша модель

def get_setting(key, default=None):
    try:
        return Setting.objects.get(key=key).value
    except Setting.DoesNotExist:
        return default

def set_setting(key, value):
    obj, _ = Setting.objects.get_or_create(key=key)
    obj.value = value
    obj.save()
