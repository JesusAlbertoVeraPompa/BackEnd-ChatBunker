"""
Production settings for deployment (Render, etc.).
"""
import os
#import dj_database_url
from decouple import Csv, config
from .base import *  # noqa: F401, F403

DEBUG = False

# Security
SECURE_PROXY_SSL_HEADER = ("HTTP_X_FORWARDED_PROTO", "https")
SECURE_SSL_REDIRECT = config("SECURE_SSL_REDIRECT", default=True, cast=bool)
SESSION_COOKIE_SECURE = True
CSRF_COOKIE_SECURE = True

# COOP: Importante para Google Login Popup
# Sin esto, el navegador bloquea la comunicación del popup con la app
SECURE_CROSS_ORIGIN_OPENER_POLICY = 'same-origin-allow-popups'

# Hosts permitidos
ALLOWED_HOSTS = config("ALLOWED_HOSTS", cast=Csv(), default="backend-chatbunker.onrender.com,localhost")

# ─────────────────────────────────────────
# CORS CONFIGURATION (Fuerza Bruta)
# ─────────────────────────────────────────
# Permitimos todos los orígenes temporalmente para asegurar la conexión
CORS_ALLOW_ALL_ORIGINS = True
CORS_ALLOW_CREDENTIALS = True

# CSRF: Aunque CORS sea libre, Django exige orígenes confiables para el POST
CSRF_TRUSTED_ORIGINS = [
    "https://jesusalbertoverapompa.github.io",
    "https://backend-chatbunker.onrender.com",
]

# ─────────────────────────────────────────
# DATABASE (MySQL en Render)
# ─────────────────────────────────────────
"""
db_from_env = dj_database_url.config(conn_max_age=600, ssl_require=False)
if db_from_env:
    DATABASES["default"].update(db_from_env)
    DATABASES["default"]["OPTIONS"] = {
        "charset": "utf8mb4",
        "init_command": "SET sql_mode='STRICT_TRANS_TABLES'",
    }
"""
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
STATICFILES_STORAGE = "whitenoise.storage.CompressedManifestStaticFilesStorage"

# Logging
LOGGING = {
    "version": 1,
    "disable_existing_loggers": False,
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
