import os

from config.settings.base import *  # NOQA:F403

SECRET_KEY = os.environ.get("SECRET_KEY")

DEBUG = False

ALLOWED_HOSTS = ['*']

DATABASES = {
    "default": {
        "ENGINE": "django.db.backends.sqlite3",
        "NAME": BASE_DIR / "db.sqlite3",  # NOQA:F405
    }
}

STATIC_ROOT = BASE_DIR / "staticfiles/"
STATIC_URL = "static/"

MEDIA_ROOT = BASE_DIR / "media/"
MEDIA_URL = "media/"