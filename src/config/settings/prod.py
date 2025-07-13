import os
from config.settings.base import *
SECRET_KEY = env("SECRET_KEY", default="some-very-secret-key")
DEBUG = env.bool("DEBUG", default=False)
ALLOWED_HOSTS = os.getenv("ALLOWED_HOSTS", "").split(",")
ROOT_URLCONF = "config.urls"
DATABASES = {
    "default": {
        "ENGINE": "django.db.backends.sqlite3",
        "NAME": BASE_DIR / "db.sqlite3",
    }
}
STATIC_ROOT = BASE_DIR / "staticfiles/"
STATIC_URL = "/static/"
MEDIA_ROOT = BASE_DIR / "media/"
MEDIA_URL = "/media/"
if not DEBUG:
    MEDIA_URL = "http://localhost/media/"