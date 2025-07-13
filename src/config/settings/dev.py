from config.settings.base import *  # noqa: F401, F403

SECRET_KEY = env("SECRET_KEY", default="insecure-key-for-dev-only")  # noqa: F405
DEBUG = True
ALLOWED_HOSTS = env.list("ALLOWED_HOSTS", default=[])  # noqa: F401, F405
if os.environ.get("GITHUB_WORKFLOW"):  # noqa: F405
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
            "NAME": BASE_DIR / "db.sqlite3",  # noqa: F405
        }
    }
STATIC_URL = "/static/"
