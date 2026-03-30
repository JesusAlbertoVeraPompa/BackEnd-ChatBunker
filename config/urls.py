"""
urls.py — Configuración principal de URLs del proyecto.
"""
from django.conf import settings
from django.conf.urls.static import static
from django.contrib import admin
from django.urls import include, path

urlpatterns = [
    # Panel de administración Django
    path("admin/", admin.site.urls),

    # API v1 — Autenticación
    path("api/v1/auth/", include("apps.accounts.urls", namespace="accounts")),

    # API v1 — Gestión de usuarios
    path("api/v1/users/", include("apps.users.urls", namespace="users")),

    # API v1 — Mensajería privada (E2EE)
    path("api/v1/chat/", include("apps.chat.urls")),
]

# En desarrollo, sirve los archivos de media directamente desde Django.
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
