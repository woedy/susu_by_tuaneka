from django.contrib.auth import get_user_model
from django.db import models

from user_profile.models import AdminInfo

User = get_user_model()

class NotificationManager():
    pass


class Notification(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='user_notification')
    notification_admin = models.ForeignKey(AdminInfo, on_delete=models.CASCADE, related_name='notification_admin', null=True, blank=True)
    subject = models.CharField(max_length=200, null=True, blank=True)
    body = models.TextField(null=True, blank=True)
    read = models.BooleanField(default=False)

    active = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)


    objects = NotificationManager()

