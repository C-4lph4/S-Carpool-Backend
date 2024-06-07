from rest_framework_simplejwt.views import TokenObtainPairView
from rest_framework_simplejwt.serializers import TokenObtainPairSerializer
from rest_framework_simplejwt.exceptions import InvalidToken, TokenError
from rest_framework.response import Response
from rest_framework import status
from django.shortcuts import get_object_or_404
from .models import ActiveUser


class CustomTokenObtainPairView(TokenObtainPairView):
    def post(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        try:

            serializer.is_valid(raise_exception=True)

            return Response(serializer.validated_data, status=status.HTTP_200_OK)
        except TokenError as e:
            email = request.data.get("email")
            user = get_object_or_404(ActiveUser, email=email)
            if user and not user.is_active:
                return Response(
                    {"message": "pendingUser"}, status=status.HTTP_401_UNAUTHORIZED
                )
            return Response(
                {"message": "Invalid credentials"}, status=status.HTTP_401_UNAUTHORIZED
            )
        except Exception as e:
            print(e)
            return Response(
                {"message": "Unknown error occured"},
                status=status.HTTP_401_UNAUTHORIZED,
            )
