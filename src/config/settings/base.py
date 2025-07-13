import os
from datetime import timedelta
from pathlib import Path

import environ

BASE_DIR = Path(__file__).resolve().parent.parent.parent
env = environ.Env()
environ.Env.read_env(BASE_DIR / ".env")
log_dir = BASE_DIR / "LOGS"
os.makedirs(log_dir, exist_ok=True)
INSTALLED_APPS = [
    "jazzmin",
    "django.contrib.admin",
    "django.contrib.auth",
    "django.contrib.contenttypes",
    "django.contrib.sessions",
    "django.contrib.messages",
    "django.contrib.staticfiles",
    "crispy_forms",
    "crispy_bootstrap5",
    "django_extensions",
    "rest_framework",
    "drf_spectacular",
    "drf_spectacular_sidecar",
    "widget_tweaks",
    "djmoney",
    "accounts",
    "common",
    "wms",
]
ROOT_URLCONF = "config.urls"
TEMPLATES = [
    {
        "BACKEND": "django.template.backends.django.DjangoTemplates",
        "DIRS": [BASE_DIR / "templates"],
        "APP_DIRS": True,
        "OPTIONS": {
            "context_processors": [
                "django.template.context_processors.request",
                "django.contrib.auth.context_processors.auth",
                "django.contrib.messages.context_processors.messages",
            ],
        },
    },
]
WSGI_APPLICATION = "config.wsgi.application"
AUTH_PASSWORD_VALIDATORS = [
    {
        "NAME": "django.contrib.auth.password_validation.UserAttributeSimilarityValidator",
    },
    {
        "NAME": "django.contrib.auth.password_validation.MinimumLengthValidator",
    },
    {
        "NAME": "django.contrib.auth.password_validation.CommonPasswordValidator",
    },
    {
        "NAME": "django.contrib.auth.password_validation.NumericPasswordValidator",
    },
]
TIME_ZONE = "UTC"
USE_I18N = True
USE_L10N = True
USE_TZ = True
LANGUAGES = [
    ("uk", "Українська"),
    ("en", "English"),
]
LOCALE_PATHS = [
    BASE_DIR / "locale",
]
MIDDLEWARE = [
    "django.middleware.security.SecurityMiddleware",
    "django.contrib.sessions.middleware.SessionMiddleware",
    "django.middleware.locale.LocaleMiddleware",
    "django.middleware.common.CommonMiddleware",
    "django.middleware.csrf.CsrfViewMiddleware",
    "django.contrib.auth.middleware.AuthenticationMiddleware",
    "django.contrib.messages.middleware.MessageMiddleware",
    "django.middleware.clickjacking.XFrameOptionsMiddleware",
]
DEFAULT_AUTO_FIELD = "django.db.models.BigAutoField"
AUTH_USER_MODEL = "accounts.Customer"
CRISPY_ALLOWED_TEMPLATE_PACKS = "bootstrap5"
CRISPY_TEMPLATE_PACK = "bootstrap5"
STATICFILES_DIRS = [
    BASE_DIR / "src" / "static",
]
STATIC_ROOT = BASE_DIR / "src" / "staticfiles"
STATIC_URL = "/static/"
MEDIA_URL = "/media/"
MEDIA_ROOT = BASE_DIR / "media"
CACHES = {
    "default": {
        "BACKEND": "django.core.cache.backends.locmem.LocMemCache",
        "LOCATION": "unique-snowflake",
        "TIMEOUT": 300,
        "OPTIONS": {
            "MAX_ENTRIES": 1000,
        },
    }
}
REST_FRAMEWORK = {
    "DEFAULT_SCHEMA_CLASS": "drf_spectacular.openapi.AutoSchema",
    "DEFAULT_AUTHENTICATION_CLASSES": ("rest_framework_simplejwt.authentication.JWTAuthentication",),
    "DEFAULT_PERMISSION_CLASSES": ["rest_framework.permissions.IsAuthenticated"],
}
SIMPLE_JWT = {
    "AUTH_HEADER_TYPES": ("Bearer",),
    "ACCESS_TOKEN_LIFETIME": timedelta(minutes=120),
    "REFRESH_TOKEN_LIFETIME": timedelta(days=14),
}
DJOSER = {
    "LOGIN_FIELD": "email",
    "USER_CREATE_PASSWORD_RETYPE": True,
    "PASSWORD_RESET_CONFIRM_RETYPE": True,
    "PASSWORD_RESET_SHOW_EMAIL_NOT_FOUND": True,
    "PASSWORD_RESET_CONFIRM_URL": "auth/password-reset/{uid}/{token}",
}
LANGUAGE_CODE = "uk"
JAZZMIN_SETTINGS = {
    "site_title": "PackPilot Admin",
    "site_brand": "PackPilot",
    "welcome_sign": "Ласкаво просимо до PackPilot Admin!",
    "copyright": "PackPilot",
    "primary_color": "#007bff",
    "secondary_color": "#6c757d",
    "accent": "#17a2b8",
    "navbar": "linear-gradient(90deg, #007bff 0%, #0056b3 100%)",
    "navbar_text": "#ffffff",
    "footer_background": "#f8f9fa",
    "footer_text": "#6c757d",
    "actions_sticky_top": True,
    "related_modal_active": True,
    "show_sidebar": True,
    "navigation_expanded": True,
    "custom_css": "css/style.css",
    "custom_js": None,
    "icons": {
        "wms.product": "bi bi-box-seam",
        "accounts.customer": "bi bi-person",
        "wms.category": "bi bi-tags",
        "wms.stockoperation": "bi bi-arrow-left-right",
        "wms.stockoperationitem": "bi bi-list-check",
        "wms.changelog": "bi bi-clock-history",
    },
    "order_with_respect_to": ["wms", "accounts"],
    "language_chooser": False,
    "search_model": ["wms.Product", "accounts.Customer"],
    "custom_links": {
        "accounts": [{"name": "На сайт", "url": "/", "icon": "bi bi-house-door", "permissions": ["auth.view_user"]}],
    },
    "show_ui_builder": False,
    "hide_apps": ["auth", "common"],
    "hide_models": ["auth.group", "auth.permission", "common.setting"],
}
LOGGING = {
    "version": 1,
    "disable_existing_loggers": False,
    "formatters": {
        "verbose": {
            "format": "[{asctime}] {levelname} {name} {message}",
            "style": "{",
        },
        "simple": {
            "format": "{levelname} {message}",
            "style": "{",
        },
    },
    "handlers": {
        "file": {
            "level": "INFO",
            "class": "logging.handlers.RotatingFileHandler",
            "filename": BASE_DIR / "LOGS" / "wms.log",
            "maxBytes": 1024 * 1024 * 5,
            "backupCount": 5,
            "formatter": "verbose",
        },
        "console": {
            "level": "INFO",
            "class": "logging.StreamHandler",
            "formatter": "simple",
        },
    },
    "loggers": {
        "": {
            "handlers": ["file", "console"],
            "level": "INFO",
            "propagate": True,
        },
    },
}
