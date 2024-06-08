from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework import status
from django.shortcuts import get_object_or_404
from django.shortcuts import render
from django.contrib.auth.hashers import check_password
from django.utils import timezone

from s_carpool import settings

from .serializers import (
    PasswordSerializer,
    ProfileSerializer,
    RequestSerializer,
    ProfileImgSirializer,
)

from .models import ActiveUser, Notification, Profile, Requests
from .managers import ActiveUserManager
from .send import send_code

from datetime import datetime, timedelta
import os
from threading import Thread


# Create your views


def home(request):
    return render(request, "index.html")


@api_view(["GET", "POST"])
def confirmEmail(request):
    try:
        email = request.data.get("email")
        confirmation_code = request.data.get("code")
    except:
        return Response({"message": "Invalid data"}, status=400)

    pending_user = get_object_or_404(ActiveUser, email=email)
    if (
        pending_user.confirmation_code == confirmation_code
        and pending_user.code_expires > timezone.now()
    ):

        pending_user.is_active = True
        pending_user.save()

        return Response({"message": "Success"})
    elif pending_user.code_expires <= timezone.now():
        return Response({"message": "code expired"}, status=400)
    return Response({"message": "Failed"}, status=400)


@api_view(["POST"])
def signUP(request):
    try:
        username = request.data.get("username")
        password = request.data.get("password")
        email = request.data.get("email")
        language = request.data.get("language")

        if not username or not password or not email:
            return Response(
                {"message": "username, email and password are required"}, status=400
            )

        if ActiveUser.objects.filter(email=email).exists():
            return Response({"message": "Account exists"}, status=400)

        user_manager = ActiveUserManager()
        user = user_manager.createUser(
            email=email, password=password, user_name=username, language=language
        )

        # Start a new thread for code generation
        Thread(target=generate_code, args=(email, user)).start()

        return Response({"message": "success"}, status=201)

    except Exception as e:
        return Response({"message": "Failed"}, status=400)


@api_view(["POST"])
def requestCode(request):
    email = None
    try:
        email = request.data.get("email")
        Pending_user = get_object_or_404(ActiveUser, email=email)
        if not Pending_user:
            return Response({"message": "E-mail not registered."}, status=400)
        else:
            confirmation = send_code(email)
            if not confirmation:
                return Response(
                    {"message": "An error occured generating code"}, status=400
                )

            Pending_user.confirmation_code = confirmation
            Pending_user.code_expires = timezone.now() + timedelta(minutes=5)
            Pending_user.save()
        return Response({"message": "Success"})
    except Exception as e:

        return Response({"message": "Email not registered"}, status=404)


@api_view(["GET", "POST"])
@permission_classes([IsAuthenticated])
def profile(request):
    user = request.user
    try:
        profile = Profile.objects.get(user=user)
    except Profile.DoesNotExist:
        return Response(
            {"message": "Profile not found"}, status=status.HTTP_404_NOT_FOUND
        )

    if request.method == "GET":
        serializer = ProfileSerializer(profile)
        return Response(serializer.data)

    elif request.method == "POST":

        username = request.data.get("username")
        req_timeout = request.data.get("reqDuration")

        if not username or not req_timeout:
            return Response(
                {"message": "Bad Request"}, status=status.HTTP_400_BAD_REQUEST
            )

        try:
            req_timeout = int(req_timeout)
        except ValueError:
            return Response(
                {"message": "Request duration must be an integer"},
                status=status.HTTP_400_BAD_REQUEST,
            )

        user.user_name = username
        user.save()
        print(user.email)

        profile.default_req_timeout = timedelta(minutes=req_timeout)
        profile.save()

        return Response({"message": "Success"}, status=status.HTTP_200_OK)


@api_view(["POST"])
@permission_classes([IsAuthenticated])
def changePassword(request):
    try:
        serializer = PasswordSerializer(data=request.data)
        if serializer.is_valid():
            user = request.user
            old_pass = serializer.data.get("current_password")
            new_pass = serializer.data.get("new_password")
            if not check_password(old_pass, user.password):
                return Response(
                    {"message": "Incorrect old password"},
                    status=status.HTTP_400_BAD_REQUEST,
                )

            user.set_password(new_pass)
            user.save()
            return Response({"message": "success"}, status=200)
    except Exception as e:
        print(e)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


def generate_code(email, activeuser):
    try:
        confirmation = send_code(email)

        if confirmation:

            activeuser.confirmation_code = confirmation
            activeuser.code_expires = datetime.now() + timedelta(minutes=5)
            activeuser.save()
            return True
    except Exception as e:
        return False


@api_view(["GET", "POST"])
@permission_classes([IsAuthenticated])
def requests(request):
    if request.method == "GET":
        try:
            requests = Requests.objects.all()
            serializer = RequestSerializer(requests, many=True)
            return Response(serializer.data, status=status.HTTP_200_OK)
        except Exception as e:
            return Response(
                {"message": "Failed to retrieve requests"},
                status=status.HTTP_400_BAD_REQUEST,
            )

    elif request.method == "POST":
        try:
            cancel = request.data.get("cancel")
            request_id = request.data.get("request_id")
            req = Requests.objects.get(id=request_id)
            user = request.user
            profile = Profile.objects.get(user=user)
            owner = Profile.objects.get(user=user)

            if cancel == "true":
                if profile == req.acceptor:
                    req.acceptor = None
                    req.save()
                    return Response(
                        {"message": "Request cancelled successfully"},
                        status=status.HTTP_200_OK,
                    )
                else:
                    return Response(
                        {"message": "Unauthorized action"},
                        status=status.HTTP_401_UNAUTHORIZED,
                    )
            elif cancel == "false":
                if req.profile == owner:
                    req.delete()
                    return Response(
                        {"message": "Request deleted successfully"},
                        status=status.HTTP_202_ACCEPTED,
                    )
                else:
                    return Response(
                        {"message": "Forbidden action"},
                        status=status.HTTP_403_FORBIDDEN,
                    )
            else:
                if req.acceptor == None:

                    req.acceptor = profile
                    req.save()
                    return Response(
                        {"message": "Request accepted successfully"},
                        status=status.HTTP_201_CREATED,
                    )
                else:
                    return Response(
                        {"message": f"Failed to process request: {str(e)}"},
                        status=status.HTTP_406_NOT_ACCEPTABLE,
                    )

        except Requests.DoesNotExist:
            return Response(
                {"message": "Request not found"}, status=status.HTTP_404_NOT_FOUND
            )
        except Profile.DoesNotExist:
            return Response(
                {"message": "Profile not found"}, status=status.HTTP_404_NOT_FOUND
            )
        except Exception as e:
            return Response(
                {"message": f"Failed to process request: {str(e)}"},
                status=status.HTTP_400_BAD_REQUEST,
            )


@api_view(["POST"])
@permission_classes([IsAuthenticated])
def changeProfileImage(request):
    user = request.user
    profile = Profile.objects.get(user=user)
    if "new_profile_image" not in request.FILES:
        return Response(
            {"error": "No file was submitted."}, status=status.HTTP_400_BAD_REQUEST
        )

    new_image = request.FILES["new_profile_image"]
    file_extension = os.path.splitext(new_image.name)[1]
    new_image.name = f"{user.email}{file_extension}"
    serializer = ProfileImgSirializer(data={"new_profile_img": new_image})
    if serializer.is_valid():
        if profile.profile_img and profile.profile_img.name != "blank.png":
            old_image_path = os.path.join(settings.MEDIA_ROOT, profile.profile_img.path)
            if os.path.isfile(old_image_path):
                os.remove(old_image_path)

        profile.profile_img = serializer.validated_data["new_profile_img"]
        profile.save()
        return Response({"message": "Success"}, status=status.HTTP_200_OK)
    print(serializer.errors)
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


@api_view(["POST"])
@permission_classes([IsAuthenticated])
def notifications(request):
    not_id = request.data.get("not_id")

    if not not_id:
        return Response(
            {"error": "Notification ID is required."},
            status=status.HTTP_400_BAD_REQUEST,
        )

    notification_exists = Notification.objects.filter(
        user=request.user, id=not_id
    ).exists()

    if notification_exists:
        Notification.objects.filter(user=request.user, id=not_id).delete()
        return Response({"message": "Notification deleted successfully."})
    else:
        return Response(
            {"error": "Notification not found."}, status=status.HTTP_404_NOT_FOUND
        )
