import os

from config.settings.base import *  # NOQA:F403

SECRET_KEY = env("SECRET_KEY", default="insecure-key-for-dev-only")  # NOQA:F405

DEBUG = True

ALLOWED_HOSTS = env.list("ALLOWED_HOSTS", default=[])  # NOQA:F405

# MIDDLEWARE + = ['']

if os.environ.get("GITHUB_WORKFLOW"):
    DATABASES = {
        "default": {
            "ENGINE": "django.db.backends.postgresql",
            "NAME": "postgres",
            "USER": "postgres",
            "PASSWORD": "postgres",
            "HOST": "0.0.0.0",
            "PORT": 5432,
        },
    }
else:
    DATABASES = {
        "default": {
            "ENGINE": "django.db.backends.sqlite3",
            "NAME": BASE_DIR / "db.sqlite3",  # NOQA:F405
        }
    }

STATIC_URL = "/static/"
