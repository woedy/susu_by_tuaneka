from rest_framework import serializers

from notifications.models import Notification


class NotificationSerializer(serializers.ModelSerializer):
    created_at = serializers.SerializerMethodField()

    def get_created_at(self, obj):
        return obj.created_at.strftime("%d-%m-%y")


    class Meta:
        model = Notification
        fields = ['id', 'subject', 'body', 'created_at', 'read' ]