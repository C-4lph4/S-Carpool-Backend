import uuid
from django.db.models.signals import post_save
from django.dispatch import receiver
from django.contrib.auth import get_user_model
from .models import Notification, Profile, Requests
from channels.layers import get_channel_layer
from asgiref.sync import async_to_sync

User = get_user_model()


@receiver(post_save, sender=User)
def create_profile(sender, instance, created, **kwargs):
    if not created and instance.is_active:

        Profile.objects.get_or_create(user=instance, id=instance.email)


@receiver(post_save, sender=Requests)
def send_request_notification(sender, instance, created, **kwargs):

    try:
        active_users = User.objects.filter(is_active=True).exclude(
            email=instance.owner.id
        )
        channel_layer = get_channel_layer()

        for active_user in active_users:
            print(active_user)
            message = {
                "id": uuid.uuid4(),
                "title": (
                    "Nouvelle requête" if active_user.language == "fr" else "New Request"
                ),
                "body": (
                    f"Il y a une nouvelle demande de {instance.owner.user.user_name}"
                    if active_user.language == "fr"
                    else f"There is a new request from {instance.owner.user.user_name}"
                ),
            }

            saveNotification(
                receiver=active_user, title=message["title"], body=message["body"],id=message['id']
            )
            sendNotification(
                channel_layer=channel_layer, message=message, receiver=active_user.id
            )
    except Exception as e:
        print(e)


@receiver(post_save, sender=Requests)
def send_acceptance_notification(sender, instance, created, **kwargs):
    if not created and instance.acceptor:
        channel_layer = get_channel_layer()
        message = {
            "id": uuid.uuid4(),
            "title": (
                "Requête acceptée"
                if instance.owner.language == "fr"
                else "Request Accepted"
            ),
            "body": (
                f"Votre demande a été acceptée par {instance.acceptor.user.user_name}"
                if instance.owner.language == "fr"
                else f"Your request has been accepted by {instance.acceptor.user.user_name}"
            ),
        }
        saveNotification(
            receiver=instance.owner,
            title=message["title"],
            body=message["body"],
            id=message["id"],
        )

        sendNotification(
            channel_layer=channel_layer, message=message, receiver=instance.owner.id
        )


def saveNotification(receiver, title, body, id):
    Notification.objects.create(user=receiver, title=title, body=body, id=id)


def sendNotification(channel_layer, message, receiver):
    async_to_sync(channel_layer.group_send)(
        f"user_{receiver}",
        {
            "type": "send_notification",
            "message": message,
        },
    )
