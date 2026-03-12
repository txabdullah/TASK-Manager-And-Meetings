from .base import *

DEBUG = False
DJANGO_SETTINGS_MODULE = "config.settings.production"

database_url = config("DATABASE_URL", default="")
if database_url:
    import dj_database_url
    DATABASES = {"default": dj_database_url.config(default=database_url, conn_max_age=600)}
else:
    DATABASES = {
        "default": {
            "ENGINE": "django.db.backends.sqlite3",
            "NAME": BASE_DIR / "db.sqlite3",
        }
    }
