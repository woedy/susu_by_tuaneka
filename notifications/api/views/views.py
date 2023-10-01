from django.contrib.auth import get_user_model
from rest_framework import status
from rest_framework.decorators import permission_classes, api_view, authentication_classes
from rest_framework.response import Response

from notifications.api.serializers import NotificationSerializer
from notifications.models import Notification

User = get_user_model()

@api_view(['GET', ])
@permission_classes([])
@authentication_classes([])
def get_user_notification_view(request):
    payload = {}
    data = {}
    user_data = {}

    errors = []

    user_id = request.query_params.get('user_id', None)

    if not user_id:
        payload['message'] = "Error"
        errors.append("User ID Required.")

    user = User.objects.get(user_id=user_id)


    notifications = Notification.objects.all().filter(user=user).order_by('-created_at')

    notifications_serializer = NotificationSerializer(notifications, many=True)
    if notifications_serializer:
        notifications = notifications_serializer.data

    print(notifications)

    if errors:
        payload['errors'] = errors
        return Response(payload, status=status.HTTP_404_NOT_FOUND)

    payload['message'] = "Successful"
    payload['data'] = notifications

    return Response(payload, status=status.HTTP_200_OK)

