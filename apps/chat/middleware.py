import logging
from urllib.parse import parse_qs
from channels.db import database_sync_to_async
from django.contrib.auth.models import AnonymousUser
from rest_framework_simplejwt.tokens import AccessToken
from django.core.cache import cache
from django.contrib.auth import get_user_model

User = get_user_model()
logger = logging.getLogger(__name__)

@database_sync_to_async
def get_user(user_id):
    try:
        return User.objects.get(id=user_id)
    except User.DoesNotExist:
        return AnonymousUser()

class JWTAuthRateLimitMiddleware:
    """
    Middleware para WebSockets que valida JWT y aplica Rate Limiting.
    """
    def __init__(self, inner):
        self.inner = inner

    async def __call__(self, scope, receive, send):
        # 1. Rate Limiting por IP (DoS protection)
        client_ip = scope.get('client', ['0.0.0.0'])[0]
        cache_key = f"ws_ratelimit_{client_ip}"
        requests_count = cache.get(cache_key, 0)
        
        if requests_count > 1000: # Límite aumentado a 1000 por hora
            logger.warning("WebSocket Rate limit exceeded for IP %s", client_ip)
            return None 

        cache.set(cache_key, requests_count + 1, timeout=3600)

        # 2. JWT Validation
        try:
            query_string = parse_qs(scope['query_string'].decode())
            token_str = query_string.get('token', [None])[0]
        except Exception:
            token_str = None

        if not token_str:
            scope['user'] = AnonymousUser()
        else:
            try:
                # Valida el token de forma directa
                access_token = AccessToken(token_str)
                # En algunas versiones de SimpleJWT el ID está en payload, en otras es un diccionario directo
                user_id = access_token.get('user_id') or getattr(access_token, 'payload', {}).get('user_id')
                
                if user_id:
                    scope['user'] = await get_user(user_id)
                else:
                    scope['user'] = AnonymousUser()
            except Exception as exc:
                logger.error("WebSocket JWT validation failed: %s", exc)
                scope['user'] = AnonymousUser()

        return await self.inner(scope, receive, send)
