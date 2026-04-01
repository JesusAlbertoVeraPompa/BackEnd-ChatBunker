"""
Production settings for deployment (Render, etc.).
"""
from decouple import Csv, config
from .base import *  # noqa: F401, F403

DEBUG = False

# Security
SECURE_PROXY_SSL_HEADER = ("HTTP_X_FORWARDED_PROTO", "https")
SECURE_SSL_REDIRECT = config("SECURE_SSL_REDIRECT", default=True, cast=bool)
SESSION_COOKIE_SECURE = True
CSRF_COOKIE_SECURE = True

# COOP: importante para popups de login social (Google/Facebook).
SECURE_CROSS_ORIGIN_OPENER_POLICY = "same-origin-allow-popups"

# Hosts permitidos
ALLOWED_HOSTS = config(
    "ALLOWED_HOSTS",
    cast=Csv(),
    default="backend-chatbunker.onrender.com,localhost",
)

# CORS: allowlist estricta en produccion (sin wildcard)
CORS_ALLOW_ALL_ORIGINS = False
CORS_ALLOWED_ORIGINS = config(
    "CORS_ALLOWED_ORIGINS",
    cast=Csv(),
    default="https://jesusalbertoverapompa.github.io,https://backend-chatbunker.onrender.com",
)
# La API usa JWT en Authorization header; no requiere cookies cross-site.
CORS_ALLOW_CREDENTIALS = config("CORS_ALLOW_CREDENTIALS", default=False, cast=bool)

# CSRF: origenes confiables (lista CSV por variable de entorno)
CSRF_TRUSTED_ORIGINS = config(
    "CSRF_TRUSTED_ORIGINS",
    cast=Csv(),
    default="https://jesusalbertoverapompa.github.io,https://backend-chatbunker.onrender.com",
)

# Channel layers (Redis en Render)
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

# Static files (Whitenoise)
STATICFILES_STORAGE = "whitenoise.storage.CompressedManifestStaticFilesStorage"

# Logging
LOGGING = {
    "version": 1,
    "disable_existing_loggers": False,
    "formatters": {
        "verbose": {
            "format": "{levelname} {asctime} {module} {process:d} {thread:d} {message}",
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
    },
}
