"""
ASGI config for s_carpool project.

It exposes the ASGI callable as a module-level variable named ``application``.

For more information on this file, see
https://docs.djangoproject.com/en/5.0/howto/deployment/asgi/
"""

import os
import django
from channels.routing import ProtocolTypeRouter, URLRouter
from django.core.asgi import get_asgi_application
from core_api.middleware import TokenAuthMiddleware
import core_api.routing

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "s_carpool.settings")

# Ensure Django setup is called before importing models
django.setup()

# Print statement for debugging
print(f"DJANGO_SETTINGS_MODULE: {os.getenv('DJANGO_SETTINGS_MODULE')}")
print("Django settings loaded successfully.")

# Define the authentication middleware
auth = TokenAuthMiddleware(URLRouter(core_api.routing.websocket_urlpatterns))

# Define the ASGI application
application = ProtocolTypeRouter(
    {
        "http": get_asgi_application(),
        "websocket": auth,
    }
)
