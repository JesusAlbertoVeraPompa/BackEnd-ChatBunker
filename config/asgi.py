import os
import django
from django.core.asgi import get_asgi_application

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings.development')
django.setup()

from channels.routing import ProtocolTypeRouter, URLRouter
from apps.chat.middleware import JWTAuthRateLimitMiddleware
from apps.chat.routing import websocket_urlpatterns

application = ProtocolTypeRouter({
    "http": get_asgi_application(),
    "websocket": JWTAuthRateLimitMiddleware(
        URLRouter(
            websocket_urlpatterns
        )
    ),
})
