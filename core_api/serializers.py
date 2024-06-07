import base64
import datetime
from rest_framework import serializers
from .models import Requests, Profile


class PasswordSerializer(serializers.Serializer):
    current_password = serializers.CharField(required=True)
    new_password = serializers.CharField(required=True)


class ProfileImgSirializer(serializers.Serializer):
    new_profile_img = serializers.ImageField(required=True)


class DurationInMinutesField(serializers.Field):
    def to_representation(self, value):
        # Convert duration to minutes
        if isinstance(value, datetime.timedelta):
            total_seconds = value.total_seconds()
            minutes = total_seconds / 60
            return round(minutes)
        return value

    def to_internal_value(self, data):
        # Convert minutes back to timedelta
        try:
            minutes = int(data)
            return datetime.timedelta(minutes=minutes)
        except ValueError:
            raise serializers.ValidationError(
                "Duration must be an integer representing minutes"
            )


class ProfileSerializer(serializers.ModelSerializer):
    username = serializers.CharField(source="user.user_name")
    email = serializers.EmailField(source="user.email")
    profile_img = serializers.CharField(source="profile_img.url")
    reqDuration = DurationInMinutesField(source="default_req_timeout")

    class Meta:
        model = Profile
        fields = ["username", "email", "profile_img", "reqDuration"]


class RequestSerializer(serializers.ModelSerializer):
    owner = ProfileSerializer()
    acceptor = ProfileSerializer(allow_null=True, required=False)
    message = serializers.SerializerMethodField()

    class Meta:
        model = Requests
        fields = "__all__"

    def get_message(self, obj):
        # Encode the message to base64
        return base64.b64encode(obj.message.encode()).decode()
