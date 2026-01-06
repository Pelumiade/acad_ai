from .base import *

DEBUG = True

# Database - SQLite for development
DATABASES = {
    "default": {
        "ENGINE": "django.db.backends.sqlite3",
        "NAME": BASE_DIR / "db.sqlite3",
    }
}

# CORS for local development - allow all origins and methods
CORS_ALLOW_ALL_ORIGINS = True
CORS_ALLOW_CREDENTIALS = True
CORS_ALLOW_HEADERS = [
    "accept",
    "accept-encoding",
    "authorization",
    "content-type",
    "dnt",
    "origin",
    "user-agent",
    "x-csrftoken",
    "x-requested-with",
]
CORS_ALLOW_METHODS = [
    "DELETE",
    "GET",
    "OPTIONS",
    "PATCH",
    "POST",
    "PUT",
]

# CSRF settings for development
CSRF_TRUSTED_ORIGINS = [
    "http://localhost:8000",
    "http://localhost:9000",
    "http://localhost:9007",
    "http://localhost:9008",
    "http://127.0.0.1:8000",
    "http://127.0.0.1:9000",
    "http://127.0.0.1:9007",
    "http://127.0.0.1:9008",
]

# Email backend for development
EMAIL_BACKEND = "django.core.mail.backends.console.EmailBackend"
