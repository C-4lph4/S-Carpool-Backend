from django.urls import path
from . import views
from .token_pair_view import CustomTokenObtainPairView
from rest_framework_simplejwt.views import TokenRefreshView


urlpatterns = [
    path("", views.home),
    path("core_api/signup", views.signUP, name="SignUp"),
    path("core_api/code", views.requestCode, name="RequestCode"),
    path("core_api/email_confirmation", views.confirmEmail, name="confirmEmail"),
    path("core_api/profile", views.profile, name="Profile"),
    path("core_api/profile/change_password", views.changePassword, name="ChangePass"),
    path(
        "core_api/profile/profile_img",
        views.changeProfileImage,
        name="Change_ProfileImage",
    ),
    path("core_api/token", CustomTokenObtainPairView.as_view(), name="Token_obtain"),
    path("core_api/token/refresh", TokenRefreshView.as_view(), name="token_refresh"),
    path("core_api/requests", views.requests, name="requests"),
    path("core_api/notification", views.notifications, name="notifications"),
]
