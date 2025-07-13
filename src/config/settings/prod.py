from config.settings.base import *  # noqa: F401, F403

SECRET_KEY = env("SECRET_KEY", default="some-very-secret-key")  # noqa: F405
DEBUG = env.bool("DEBUG", default=False)  # noqa: F405
ALLOWED_HOSTS = os.getenv("ALLOWED_HOSTS", "").split(",")  # noqa: F405, F403
ROOT_URLCONF = "config.urls"  # noqa: F405, F403
DATABASES = {
    "default": {
        "ENGINE": "django.db.backends.sqlite3",
        "NAME": BASE_DIR / "db.sqlite3",  # noqa: F405
    }
}
STATIC_ROOT = BASE_DIR / "staticfiles/"  # noqa: F405
STATIC_URL = "/static/"
MEDIA_ROOT = BASE_DIR / "media/"  # noqa: F405
MEDIA_URL = "/media/"
if not DEBUG:
    MEDIA_URL = "http://localhost/media/"  # noqa: F405, F403
