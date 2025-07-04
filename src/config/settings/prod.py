import os

from config.settings.base import *  # NOQA:F403

SECRET_KEY = env("SECRET_KEY")  # NOQA:F405

DEBUG = env.bool("DEBUG", default=False)  # NOQA:F405

ALLOWED_HOSTS = env.list("ALLOWED_HOSTS", default=["*"])  # NOQA:F405

ROOT_URLCONF = "config.urls"

DATABASES = {
    "default": {
        "ENGINE": "django.db.backends.postgresql",
        "NAME": os.environ.get("POSTGRES_DB"),
        "USER": os.environ.get("POSTGRES_USER"),
        "PASSWORD": os.environ.get("POSTGRES_PASSWORD"),
        "HOST": os.environ.get("POSTGRES_HOST", "localhost"),
        "PORT": os.environ.get("POSTGRES_PORT", "5432"),
    }
}

STATIC_ROOT = BASE_DIR / "staticfiles/"  # NOQA:F405
STATIC_URL = "/static/"

MEDIA_ROOT = BASE_DIR / "media/"  # NOQA:F405
MEDIA_URL = "/media/"

if not DEBUG:
    MEDIA_URL = "http://localhost/media/"
