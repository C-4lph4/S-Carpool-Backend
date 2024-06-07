from django.contrib import admin
from .models import ActiveUser, Profile, Requests, Notification

admin.site.register(ActiveUser)
admin.site.register(Profile)
admin.site.register(Requests)
admin.site.register(Notification)
