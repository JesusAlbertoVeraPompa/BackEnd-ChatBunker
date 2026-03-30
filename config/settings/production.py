"""
Production settings for deployment (Render, etc.).
"""
import os
import dj_database_url
from decouple import Csv, config
from .base import *  # noqa: F401, F403

DEBUG = False

# Security: In production, these should be True
# Si Render maneja el SSL (lo hace por defecto), estas opciones son seguras.
SECURE_PROXY_SSL_HEADER = ("HTTP_X_FORWARDED_PROTO", "https")
SECURE_SSL_REDIRECT = config("SECURE_SSL_REDIRECT", default=True, cast=bool)
SESSION_COOKIE_SECURE = True
CSRF_COOKIE_SECURE = True

# Hosts permitidos
ALLOWED_HOSTS = config("ALLOWED_HOSTS", cast=Csv(), default="localhost")

# CORS: Aquí debes poner la URL de tu GitHub Pages
CORS_ALLOWED_ORIGINS = config("CORS_ALLOWED_ORIGINS", cast=Csv(), default="http://localhost:3000")

# ─────────────────────────────────────────
# DATABASE (MySQL en Render)
# ─────────────────────────────────────────
# Render inyecta DATABASE_URL. Si no existe, intenta usar los valores de base.py
db_from_env = dj_database_url.config(conn_max_age=600, ssl_require=False)
if db_from_env:
    DATABASES["default"].update(db_from_env)
    # Asegurar charset correcto para E2EE
    DATABASES["default"]["OPTIONS"] = {
        "charset": "utf8mb4",
        "init_command": "SET sql_mode='STRICT_TRANS_TABLES'",
    }

# ─────────────────────────────────────────
# CHANNEL LAYERS (Redis en Render)
# ─────────────────────────────────────────
REDIS_URL = config("REDIS_URL", default=None)
if REDIS_URL:
    CHANNEL_LAYERS = {
        "default": {
            "BACKEND": "channels_redis.core.RedisChannelLayer",
            "CONFIG": {
                "hosts": [REDIS_URL],
            },
        },
    }

# ─────────────────────────────────────────
# STATIC FILES (Whitenoise)
# ─────────────────────────────────────────
# Whitenoise sirve los archivos directamente desde Python
STATICFILES_STORAGE = "whitenoise.storage.CompressedManifestStaticFilesStorage"

# Logging: Solo advertencias y errores en producción para ahorrar espacio
LOGGING = {
    "version": 1,
    "disable_existing_loggers": False,
    "formatters": {
        "verbose": {
            "format": "[{levelname}] {asctime} {module} {process:d} {thread:d} {message}",
            "style": "{",
        },
    },
    "handlers": {
        "console": {
            "class": "logging.StreamHandler",
            "formatter": "verbose",
        },
    },
    "root": {
        "handlers": ["console"],
        "level": "WARNING",
    },
    "loggers": {
        "django": {
            "handlers": ["console"],
            "level": "ERROR",
            "propagate": False,
        },
        "apps": {
            "handlers": ["console"],
            "level": "INFO",
            "propagate": False,
        },
    },
}
