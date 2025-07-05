from config.settings.base import *  # NOQA:F403

SECRET_KEY = env("SECRET_KEY", default="some-very-secret-key")  # NOQA:F405

DEBUG = env.bool("DEBUG", default=False)  # NOQA:F405

ALLOWED_HOSTS = env.list("ALLOWED_HOSTS", default=["*"])  # NOQA:F405

ROOT_URLCONF = "config.urls"

DATABASES = {
    "default": {
        "ENGINE": "django.db.backends.sqlite3",
        "NAME": BASE_DIR / "db.sqlite3",  # NOQA:F405
    }
}

STATIC_ROOT = BASE_DIR / "staticfiles/"  # NOQA:F405
STATIC_URL = "/static/"

MEDIA_ROOT = BASE_DIR / "media/"  # NOQA:F405
MEDIA_URL = "/media/"

if not DEBUG:
    MEDIA_URL = "http://localhost/media/"
