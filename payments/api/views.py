from django.contrib.auth import get_user_model
from rest_framework import status
from rest_framework.authentication import TokenAuthentication
from rest_framework.decorators import permission_classes, api_view, authentication_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response

from home_page.api.serializers import HomeSusuGroupSerializer
from payments.api.serializers import ListPaymentSerializer, ListPaymentScheduleSerializer
from payments.models import Payment
from susu_groups.api.serializers import PaymentScheduleSerializer, ListSusuGroupSerializer
from susu_groups.models import PaymentSchedule, SusuGroup

User = get_user_model()

@api_view(['GET', ])
@permission_classes([IsAuthenticated, ])
@authentication_classes([TokenAuthentication, ])
def my_payments_view(request):
    payload = {}
    data = {}
    user_id_errors = []
    errors = {}

    next_due_payment = {}

    user_id = request.query_params.get('user_id', None)

    if not user_id:
        user_id_errors.append('User ID is required.')
        if user_id_errors:
            errors['user_id'] = user_id_errors
            payload['message'] = "Error"
            payload['errors'] = errors
            return Response(payload, status=status.HTTP_404_NOT_FOUND)

    user = User.objects.get(user_id=user_id)

    all_payments = Payment.objects.all().filter(user=user).order_by('-created_at')
    all_payments_serializer = ListPaymentSerializer(all_payments, many=True)
    if all_payments_serializer:
        all_payments = all_payments_serializer.data

    payments = Payment.objects.all().filter(user=user).filter(refund=False).order_by('-created_at')
    payments_serializer = ListPaymentSerializer(payments, many=True)
    if payments_serializer:
        payments = payments_serializer.data

    refunds = Payment.objects.all().filter(user=user).filter(refund=True).order_by('-created_at')
    refunds_serializer = ListPaymentSerializer(refunds, many=True)
    if refunds_serializer:
        refunds = refunds_serializer.data


    payment_schedules = PaymentSchedule.objects.all().order_by('due_date')
    user_payment_schedules = []

    for payment_schedule in payment_schedules:
        if payment_schedule.group_user.user == user:
            user_payment_schedules.append(payment_schedule)

            print(payment_schedule)


    if user_payment_schedules != []:

        the_payment_schedule = user_payment_schedules[0]
        if the_payment_schedule is not None:
            payment_schedules_serializer = PaymentScheduleSerializer(the_payment_schedule, many=False)
            if payment_schedules_serializer:
                next_due_payment = payment_schedules_serializer.data

    all_user_groups = []
    user_groups = SusuGroup.objects.all()
    for group in user_groups:
        for susu_user in group.susu_group_users.all():
            if susu_user.user == user:
                payment_schedule = PaymentSchedule.objects.all().filter(group_user=susu_user).filter(
                    user_susu_group=group).first()
                print(payment_schedule)

                user_groups_serializer = ListSusuGroupSerializer(group, many=False)
                if user_groups_serializer:
                    _group = user_groups_serializer.data

                the_user_group = {}
                the_user_group['group'] = _group
                the_user_group['status'] = payment_schedule.status
                all_user_groups.append(the_user_group)

    data['all_payments'] = all_payments
    data['payments'] = payments
    data['refunds'] = refunds
    data['next_due_payment'] = next_due_payment
    data['all_user_groups'] = all_user_groups



    payload['message'] = "Successful"
    payload['data'] = data

    return Response(payload, status=status.HTTP_200_OK)





@api_view(['GET', ])
@permission_classes([IsAuthenticated, ])
@authentication_classes([TokenAuthentication, ])
def my_payment_schedule_view(request):
    payload = {}
    data = {}
    user_id_errors = []
    errors = {}

    user_id = request.query_params.get('user_id', None)

    if not user_id:
        user_id_errors.append('User ID is required.')
        if user_id_errors:
            errors['user_id'] = user_id_errors
            payload['message'] = "Error"
            payload['errors'] = errors
            return Response(payload, status=status.HTTP_404_NOT_FOUND)

    user = User.objects.get(user_id=user_id)

    all_payment_schedules = PaymentSchedule.objects.all().order_by('-created_at')

    user_schedules = []
    for pay_schedule in all_payment_schedules:
        if pay_schedule.group_user.user == user:
            user_schedules.append(pay_schedule)

    all_payment_schedules_serializer = ListPaymentScheduleSerializer(user_schedules, many=True)
    if all_payment_schedules_serializer:
        all_payment_schedules = all_payment_schedules_serializer.data

    data['all_payment_schedules'] = all_payment_schedules



    payload['message'] = "Successful"
    payload['data'] = data

    return Response(payload, status=status.HTTP_200_OK)


