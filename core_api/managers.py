from django.contrib.auth.models import BaseUserManager
from django.contrib.auth import get_user_model


class ActiveUserManager(BaseUserManager):

    def createUser(self, email, password, model=None, **extra_fields):
        if not email:
            return None

        email = self.normalize_email(email)

        try:
            user = self.model(email=email, **extra_fields)

        except:
            model = get_user_model()

            user = model(email=email, **extra_fields)

        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_superuser(self, email, password, **extra_fields):
        extra_fields.setdefault("is_staff", True)
        extra_fields.setdefault("is_superuser", True)
        extra_fields.setdefault("is_active", True)
        return self.createUser(email, password, **extra_fields)

    def get_by_natural_key(self, username):
        return self.get(email=username)

    def __init__(self):
        super().__init__()
