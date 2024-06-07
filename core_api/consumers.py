import uuid
from channels.generic.websocket import AsyncWebsocketConsumer
import json

from django.contrib.auth.models import AnonymousUser
from channels.db import database_sync_to_async
from asgiref.sync import sync_to_async
from .models import Notification, Requests, Profile, ActiveUser


class LocationConsumer(AsyncWebsocketConsumer):

    async def connect(self):
        # self.user = self.get_user()
        # if isinstance(self.user, AnonymousUser):
        #     await self.close()

        self.group_id = self.scope["url_route"]["kwargs"]["request_id"]

        self.group_name = self.group_id
        await self.channel_layer.group_add(self.group_name, self.channel_name)
        await self.accept()

    async def disconnect(self, code):
        await self.channel_layer.group_discard(self.group_name, self.channel_name)

    async def receive(self, text_data=None, bytes_data=None):

        event = {"type": "forward_msg", "data": text_data}
        await self.channel_layer.group_send(self.group_name, event)

    async def forward_msg(self, event):
        await self.send(text_data=event["data"])

    def get_user(self):
        return self.scope["user"]


class RequestConsumer(AsyncWebsocketConsumer):

    async def connect(self):
        self.user = await self.get_user()
        if isinstance(self.user, AnonymousUser):
            await self.close()

        self.group_name = "requests"
        await self.channel_layer.group_add(self.group_name, self.channel_name)
        await self.accept()

    async def disconnect(self, code):
        if hasattr(self, "group_name"):
            await self.channel_layer.group_discard(self.group_name, self.channel_name)

    async def receive(self, text_data=None, bytes_data=None):
        request_data = json.loads(text_data)

        id = request_data.get("id")

        sourceLat = request_data.get("sourceLat")
        sourceLng = request_data.get("sourceLng")
        destinationLat = request_data.get("destinationLat")
        destinationLng = request_data.get("destinationLng")
        owner = request_data.get("owner")
        msg = request_data.get("message")
        if (
            sourceLat
            and sourceLng
            and destinationLat
            and destinationLng
            and owner
            and id
        ):

            try:
                await self.createNewRequest(
                    sLat=sourceLat,
                    sLng=sourceLng,
                    dLat=destinationLat,
                    dLng=destinationLng,
                    owner=owner,
                    msg=msg,
                    ID=id,
                )
                event = {"type": "forward_msg", "data": text_data}
                await self.channel_layer.group_send(self.group_name, event)
            except Exception as e:
                print(e)
                return

        event = {"type": "forward_msg", "data": text_data}
        await self.channel_layer.group_send(self.group_name, event)

    async def forward_msg(self, event):
        await self.send(text_data=event["data"])

    async def get_user(self):
        return self.scope["user"]

    @database_sync_to_async
    def createNewRequest(self, ID, sLat, sLng, dLat, dLng, owner, msg):
        ownerId = owner["email"]

        Owner = ActiveUser.objects.get(email=ownerId)
        profile = Profile.objects.get(user=Owner)
        if profile:
            try:
                Requests.objects.create(
                    id=ID,
                    owner=profile,
                    sourceLat=sLat,
                    sourceLng=sLng,
                    destinationLat=dLat,
                    destinationLng=dLng,
                    message=msg,
                )

            except Exception as e:
                print(f"error {e}")

        else:
            return


class NotificationConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        self.user = self.scope["user"]
        if isinstance(self.user, AnonymousUser):
            self.close()
        self.user.is_online = True
        await database_sync_to_async(self.user.save)()
        await self.channel_layer.group_add(f"user_{self.user.id}", self.channel_name)
        await self.accept()
        event = ""
        if self.user.language == "en":
            event = {
                "type": "send_notification",
                "message": {
                    'id':uuid.uuid4(),
                    "title": "Welcome Back",
                    "body": f"Checking for new requests",
                },
            }
        else:
            event = {
                "type": "send_notification",
                "message": {
                    "id": uuid.uuid4(),
                    "title": "Content de te revoir",
                    "body": f"Vérification des nouvelles demandes",
                },
            }
        await self.channel_layer.group_send(f"user_{self.user.id}", event)

        notifications = await sync_to_async(list)(
            Notification.objects.filter(user=self.user)
        )
        for notification in notifications:
            await self.send(
                text_data=json.dumps(
                    {
                        "id": notification.id,
                        "title": notification.title,
                        "body": notification.body,
                    }
                )
            )

    async def disconnect(self, close_code):
        await self.channel_layer.group_discard(
            f"user_{self.user.id}", self.channel_name
        )
        self.user.is_online = False
        await database_sync_to_async(self.user.save)()

    async def receive(self, text_data):
        data = json.loads(text_data)
        await self.send(text_data=json.dumps(data))

    async def send_notification(self, event):
        await self.send(text_data=json.dumps(event["message"]))
