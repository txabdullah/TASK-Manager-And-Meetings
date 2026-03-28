from .base import *

DEBUG = False
DJANGO_SETTINGS_MODULE = "config.settings.production"

INSTALLED_APPS = ["whitenoise.runserver_nostatic"] + INSTALLED_APPS

MIDDLEWARE.insert(1, "whitenoise.middleware.WhiteNoiseMiddleware")

STATICFILES_STORAGE = "whitenoise.storage.CompressedStaticFilesStorage"

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

SECURE_PROXY_SSL_HEADER = ("HTTP_X_FORWARDED_PROTO", "https")
USE_X_FORWARDED_HOST = True

SECURE_SSL_REDIRECT = config("SECURE_SSL_REDIRECT", default=False, cast=bool)
SESSION_COOKIE_SECURE = config("SESSION_COOKIE_SECURE", default=False, cast=bool)
CSRF_COOKIE_SECURE = config("CSRF_COOKIE_SECURE", default=False, cast=bool)

csrf_origins = config("CSRF_TRUSTED_ORIGINS", default="", cast=lambda v: [s.strip() for s in v.split(",")] if v else [])
if csrf_origins:
    CSRF_TRUSTED_ORIGINS = csrf_origins

CORS_ALLOW_ALL_ORIGINS = False
