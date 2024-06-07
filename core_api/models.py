import uuid
from django.db import models
from django.contrib.auth.models import (
    AbstractBaseUser,
    PermissionsMixin,
)
from .managers import ActiveUserManager
from django.utils import timezone
from django.conf import settings
from datetime import timedelta, datetime


from django.contrib.auth.models import User
import os


# Create your models here.


class ActiveUser(AbstractBaseUser, PermissionsMixin):
    objects = ActiveUserManager()
    email = models.EmailField(unique=True)
    user_name = models.CharField(max_length=100, blank=True, null=True)
    is_active = models.BooleanField(default=False)
    date_joined = models.DateTimeField(auto_now_add=True)
    password = models.CharField(max_length=128)
    is_staff = models.BooleanField(default=False)
    confirmation_code = models.CharField(max_length=6, default="")
    code_expires = models.DateTimeField(default=timezone.now)
    is_online = models.BooleanField(default=False)
    language = models.CharField(max_length=2, default="fr")

    REQUIRED_FIELDS = ["user_name"]
    USERNAME_FIELD = "email"

    def __str__(self):
        return self.email


class Profile(models.Model):

    user = models.OneToOneField(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    id = models.EmailField(primary_key=True, default=None, editable=True, unique=True)
    profile_img = models.ImageField(upload_to="profile_img", default="blank.png")
    default_req_timeout = models.DurationField(default=timedelta(minutes=30))

    def save(self, *args, **kwargs):
        try:
            this = Profile.objects.get(id=self.id)
            if (
                this.profile_img != self.profile_img
                and this.profile_img.name != "blank.png"
            ):
                old_image_path = os.path.join(
                    settings.MEDIA_ROOT, this.profile_img.path
                )
                if os.path.isfile(old_image_path):
                    os.remove(old_image_path)
        except Profile.DoesNotExist:
            pass
        super().save(*args, **kwargs)


class Requests(models.Model):
    owner = models.ForeignKey(
        Profile, on_delete=models.CASCADE, related_name="requests_made", default=None
    )
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    sourceLat = models.FloatField(default=0)
    sourceLng = models.FloatField(default=0)
    destinationLat = models.FloatField(default=0)
    destinationLng = models.FloatField(default=0)
    request_time = models.DateTimeField(default=timezone.now)
    message = models.TextField(max_length=1000)
    acceptor = models.ForeignKey(
        Profile,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="requests_accepted",
    )

    def __str__(self):
        return f"Request from {self.owner.user.user_name} at {self.request_time}"


class Notification(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    id = models.UUIDField(primary_key=True)
    title = models.CharField(max_length=255)
    body = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)
