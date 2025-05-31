from common.models import Setting


def get_setting(key, default=None):
    try:
        return Setting.objects.get(key=key).value
    except Setting.DoesNotExist:
        return default


def set_setting(key, value):
    setting, created = Setting.objects.get_or_create(key=key)
    setting.value = value
    setting.save()
