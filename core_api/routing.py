from django.urls import re_path
from . import consumers

websocket_urlpatterns = [
    re_path(
        r"^ws/share_loc/(?P<request_id>[a-f0-9-]+)$",
        consumers.LocationConsumer.as_asgi(),
    ),
    re_path(r"ws/share_loc/$", consumers.RequestConsumer.as_asgi()),
    re_path(r"ws/notification/$", consumers.NotificationConsumer.as_asgi()),
]
