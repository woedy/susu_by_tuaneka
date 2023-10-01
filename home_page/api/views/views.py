from django.contrib.auth import get_user_model
from rest_framework import status
from rest_framework.authentication import TokenAuthentication
from rest_framework.decorators import permission_classes, api_view, authentication_classes
from rest_framework.generics import get_object_or_404
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response

from home_page.api.serializers import HomePaymentScheduleSerializer, HomeSusuGroupSerializer
from notifications.api.serializers import NotificationSerializer
from notifications.models import Notification
from susu_groups.models import SusuGroup, PaymentSchedule, SusuGroupUser
from user_profile.models import PersonalInfo

User = get_user_model()



@api_view(['GET', ])
@permission_classes([IsAuthenticated, ])
@authentication_classes([TokenAuthentication, ])
def susu_user_home(request):
    payload = {}
    user_data = {}
    data = {}
    errors = []

    if request.method == 'GET':
        user_id = request.query_params.get('user_id', None)

        if not user_id:
            payload['message'] = "Error"
            errors.append("User ID Required.")
        else:
            has_notification = False

            user = get_object_or_404(User, user_id=user_id)
            personal_info = get_object_or_404(PersonalInfo, user=user)

            notifications = Notification.objects.all().filter(user=user)
            notifications_serializer = NotificationSerializer(notifications, many=True)
            if notifications_serializer:
                notifications = notifications_serializer.data

            for notification in notifications:
                if notification['read'] == False:
                    has_notification = True

            public_groups = SusuGroup.objects.all().filter(group_type="Public")
            public_groups_serializer = HomeSusuGroupSerializer(public_groups, many=True)
            if public_groups_serializer:
                public_groups = public_groups_serializer.data


            payment_schedules = PaymentSchedule.objects.all()

            user_payment_schedules = []

            for payment_schedule in payment_schedules:
                if payment_schedule.group_user.user == user:
                    user_payment_schedules.append(payment_schedule)

                    print(payment_schedule)


            payment_schedules_serializer = HomePaymentScheduleSerializer(user_payment_schedules, many=True)
            if payment_schedules_serializer:
                payment_schedules = payment_schedules_serializer.data

            user_data['full_name'] = user.full_name
            user_data['profile_photo'] = personal_info.photo.url

            data['user_data'] = user_data
            data['has_notification'] = has_notification
            data['public_groups'] = public_groups
            data['payment_schedules'] = payment_schedules

            payload['response'] = "Successful"
            payload['data'] = data

        if errors:
            # Return error response with list of errors
            # payload['response'] = 'Error'
            payload['errors'] = errors
            return Response(payload, status=status.HTTP_404_NOT_FOUND)

        return Response(payload, status=status.HTTP_200_OK)

