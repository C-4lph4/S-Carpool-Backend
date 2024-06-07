"""
ASGI config for s_carpool project.

It exposes the ASGI callable as a module-level variable named ``application``.

For more information on this file, see
https://docs.djangoproject.com/en/5.0/howto/deployment/asgi/
"""

import os, django

from django.core.asgi import get_asgi_application

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "s_carpool.settings")
django.setup()


from channels.routing import ProtocolTypeRouter, URLRouter
from core_api.middleware import TokenAuthMiddleware
import core_api.routing

# from core_api.middleware import TokenAuthMiddleware


auth = TokenAuthMiddleware(URLRouter(core_api.routing.websocket_urlpatterns))

application = ProtocolTypeRouter(
    {
        "http": get_asgi_application(),
        "websocket": auth,
    }
)
