"""
ASGI config for s_carpool project.

It exposes the ASGI callable as a module-level variable named ``application``.

For more information on this file, see
https://docs.djangoproject.com/en/5.0/howto/deployment/asgi/
"""

import os

# Set the default Django settings module
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "s_carpool.settings")

# Add diagnostic print statement
print(f"DJANGO_SETTINGS_MODULE: {os.getenv('DJANGO_SETTINGS_MODULE')}")

import django
from django.core.asgi import get_asgi_application
from channels.routing import ProtocolTypeRouter, URLRouter
from core_api.middleware import TokenAuthMiddleware
import core_api.routing

# Initialize Django
try:
    django.setup()
    print("Django settings loaded successfully.")
except Exception as e:
    print(f"Error loading Django settings: {e}")

# Define the authentication middleware
auth = TokenAuthMiddleware(URLRouter(core_api.routing.websocket_urlpatterns))

# Define the ASGI application
application = ProtocolTypeRouter(
    {
        "http": get_asgi_application(),
        "websocket": auth,
    }
)
