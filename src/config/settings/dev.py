import os

from config.settings.base import *  # NOQA:F403
from django.conf import settings

SECRET_KEY = env('SECRET_KEY', default='dev-secret-key')

DEBUG = env.bool('DEBUG', default=True)

ALLOWED_HOSTS = env.list('ALLOWED_HOSTS', default=[])

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
    # Use PostgreSQL for Docker environment
    DATABASES = {
        "default": {
            "ENGINE": "django.db.backends.postgresql",
            "NAME": env('POSTGRES_DB', default='wms_db'),
            "USER": env('POSTGRES_USER', default='wms_user'),
            "PASSWORD": env('POSTGRES_PASSWORD', default='wms_password'),
            "HOST": env('POSTGRES_HOST', default='postgres'),
            "PORT": env('POSTGRES_PORT', default='5432'),
        },
    }

STATIC_URL = "/static/"
