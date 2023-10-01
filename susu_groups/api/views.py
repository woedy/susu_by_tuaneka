import datetime
from datetime import date, timedelta
from django.utils import timezone

from django.conf import settings
from django.shortcuts import get_object_or_404

from celery import shared_task
from django.contrib.auth import get_user_model
from django.core.mail import send_mail
from django.template.loader import get_template
from mysite.settings import FCM_SERVER_KEY
from pyfcm import FCMNotification
from rest_framework import status
from rest_framework.authentication import TokenAuthentication
from rest_framework.decorators import authentication_classes, permission_classes, api_view
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from django.urls import reverse

from all_activities.models import AllActivity
from mysite.utils import generate_private_group_code
from notifications.models import Notification
from payments.models import Payment
from susu_groups.api.serializers import ListSusuGroupSerializer, DetailSusuGroupSerializer
from susu_groups.models import SusuGroup, SusuPosition, SusuGroupUser, InvitedMember, Contribution, Payout, \
    SusuGroupUserReminders, PaymentSchedule
from user_profile.models import Wallet, PersonalInfo

User = get_user_model()


@api_view(['GET', ])
@permission_classes([IsAuthenticated, ])
@authentication_classes([TokenAuthentication, ])
def view_all_user_susu_groups(request):
    payload = {}
    user_data = {}
    data = {}
    errors = []

    if request.method == 'GET':
        user_id = request.query_params.get('user_id', None)

        if not user_id:
            payload['message'] = "Error"
            errors.append("User ID Required.")

        user = User.objects.get(user_id=user_id)

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

        data['all_user_groups'] = all_user_groups

    if errors:
        # Return error response with list of errors
        # payload['response'] = 'Error'
        payload['errors'] = errors
        return Response(payload, status=status.HTTP_404_NOT_FOUND)

    payload['message'] = "Successful"
    payload['data'] = data

    return Response(payload, status=status.HTTP_200_OK)


@api_view(['GET', ])
@permission_classes([IsAuthenticated, ])
@authentication_classes([TokenAuthentication, ])
def view_all_public_susu_groups(request):
    payload = {}
    user_data = {}
    data = {}
    errors = []

    if request.method == 'GET':
        user_id = request.query_params.get('user_id', None)

        if not user_id:
            payload['message'] = "Error"
            errors.append("User ID Required.")

        public_groups = SusuGroup.objects.all().filter(group_type="Public")
        public_groups_serializer = ListSusuGroupSerializer(public_groups, many=True)
        if public_groups_serializer:
            public_groups = public_groups_serializer.data

        data['all_public_groups'] = public_groups

    if errors:
        # Return error response with list of errors
        # payload['response'] = 'Error'
        payload['errors'] = errors
        return Response(payload, status=status.HTTP_404_NOT_FOUND)

    payload['message'] = "Successful"
    payload['data'] = data

    return Response(payload, status=status.HTTP_200_OK)


@api_view(['GET', ])
@permission_classes([IsAuthenticated, ])
@authentication_classes([TokenAuthentication, ])
def view_all_private_susu_groups(request):
    payload = {}
    user_data = {}
    data = {}
    errors = []

    if request.method == 'GET':
        user_id = request.query_params.get('user_id', None)

        if not user_id:
            payload['message'] = "Error"
            errors.append("User ID Required.")

        private_groups = SusuGroup.objects.all().filter(group_type="Private")
        private_groups_serializer = ListSusuGroupSerializer(private_groups, many=True)
        if private_groups_serializer:
            private_groups = private_groups_serializer.data

        data['all_private_groups'] = private_groups

    if errors:
        # Return error response with list of errors
        # payload['response'] = 'Error'
        payload['errors'] = errors
        return Response(payload, status=status.HTTP_404_NOT_FOUND)

    payload['message'] = "Successful"
    payload['data'] = data

    return Response(payload, status=status.HTTP_200_OK)


@api_view(['GET', ])
@permission_classes([IsAuthenticated, ])
@authentication_classes([TokenAuthentication, ])
def susu_group_detail_view(request):
    payload = {}
    user_data = {}
    data = {}
    errors = {}
    group_errors = []
    user_id_errors = []

    if request.method == 'GET':
        group_id = request.query_params.get('group_id', None)
        user_id = request.query_params.get('user_id', None)

        if not user_id:
            user_id_errors.append('User ID is required.')
            if user_id_errors:
                errors['user_id'] = user_id_errors
                payload['message'] = "Error"
                payload['errors'] = errors
                return Response(payload, status=status.HTTP_404_NOT_FOUND)

        if not group_id:
            group_errors.append('Group ID is required.')
            if group_errors:
                errors['group_id'] = group_errors
                payload['message'] = "Error"
                payload['errors'] = errors
                return Response(payload, status=status.HTTP_404_NOT_FOUND)

        user = User.objects.get(user_id=user_id)
        group_detail = SusuGroup.objects.get(group_id=group_id)

        the_susu_user = SusuGroupUser.objects.filter(user=user).filter(group_id=group_detail.group_id).first()

        if the_susu_user is not None:
            print("##############")
            print("USER AVAILABLE")
            print(the_susu_user)

            for susu_user in group_detail.susu_group_users.all():
                payload['message'] = "Successful"
                payload['availability'] = True

                payment_schedule = PaymentSchedule.objects.all().filter(group_user=the_susu_user).filter(
                    user_susu_group=group_detail).first()
                print(payment_schedule)
                payload['payment_status'] = payment_schedule.status
                payload['is_turn'] = the_susu_user.is_turn

        else:
            print("##############")
            print("USER NOT AVAILABLE")
            print(the_susu_user)
            payload['message'] = "Successful"
            payload['availability'] = False

        user_groups_serializer = DetailSusuGroupSerializer(group_detail, many=False)
        if user_groups_serializer:
            _group = user_groups_serializer.data
            payload['data'] = _group

            return Response(payload, status=status.HTTP_200_OK)



    if errors:
        # Return error response with list of errors
        # payload['response'] = 'Error'
        payload['errors'] = errors
        return Response(payload, status=status.HTTP_404_NOT_FOUND)

    return Response(payload, status=status.HTTP_200_OK)


@api_view(['POST', ])
@permission_classes([IsAuthenticated, ])
@authentication_classes([TokenAuthentication, ])
def create_private_susu_group_view(request):
    payload = {}
    data = {}

    errors = {}
    user_id_errors = []
    user_id_errors = []

    user_id = request.data.get('user_id', '0')
    group_name = request.data.get('group_name', '0')
    group_description = request.data.get('group_description', '0')
    capacity = request.data.get('capacity', '0')
    target_amount = request.data.get('target_amount', '0')
    payment_cycle = request.data.get('payment_cycle', '0')
    start_date = request.data.get('start_date', '0')
    members = request.data.get('members', '0')

    if not user_id:
        user_id_errors.append('User ID is required.')
        if user_id_errors:
            errors['user_id'] = user_id_errors
            payload['message'] = "Error"
            payload['errors'] = errors
            return Response(payload, status=status.HTTP_404_NOT_FOUND)

    user = User.objects.all().filter(user_id=user_id).first()
    if not user:
        user_id_errors.append('User does not exist')
        if user_id_errors:
            errors['user_id'] = user_id_errors
            payload['message'] = "Error"
            payload['errors'] = errors
            return Response(payload, status=status.HTTP_404_NOT_FOUND)

    print("############")

    new_private_group = SusuGroup.objects.create(
        group_name=group_name,
        group_description=group_description,
        capacity=capacity,
        target_amount=target_amount,
        payment_cycle=payment_cycle,
        start_date=start_date,
        group_creator=user,
        group_type="Private",
        group_code=generate_private_group_code()
    )

    ###### SEND EMAIL TO MEMBER TO JOIN #######

    # SEND EMAIL

    host_scheme = getattr(settings, 'HOST_SCHEME', "http://")
    base_url = getattr(settings, 'BASE_URL', 'https://www.susubytuaneka.com')
    key_path = reverse("susu_groups:join_susu_group_site")
    path = "{host}{base}{path}".format(base=base_url, path=key_path, host=host_scheme)

    for member in members:
        invite_member = InvitedMember.objects.create(
            email=member,
            group=new_private_group,
            invitation_sent=True,
        )
        context = {
            'path': path,
            'email': member,
            'full_name': user.full_name,
            'group_name': group_name,
            'group_code': new_private_group.group_code,
        }

        txt_ = get_template("susu_group/join/join.txt").render(context)
        html_ = get_template("susu_group/join/join.html").render(context)
        subject = 'Invitation to join ' + group_name + ' on Susu by Tuaneka.'
        from_email = settings.DEFAULT_FROM_EMAIL
        recipient_list = [member]
        sent_mail = send_mail(
            subject,
            txt_,
            from_email,
            recipient_list,
            html_message=html_,
            fail_silently=False
        )

    group_detail = SusuGroup.objects.get(group_id=new_private_group.group_id)
    group_detail_serializer = DetailSusuGroupSerializer(group_detail, many=False)
    if group_detail_serializer:
        group_detail = group_detail_serializer.data

    new_activity = AllActivity.objects.create(
        user=user,
        subject="Create Private Group",
        body=user.email + " Just created a private group"
    )
    new_activity.save()

    new_activity = Notification.objects.create(
        user=user,
        subject="Create Private Group",
        body=" You created a private group called " + group_name
    )
    new_activity.save()

    payload['message'] = "Successful"
    payload['data'] = group_detail

    return Response(payload, status=status.HTTP_200_OK)



@api_view(['GET', ])
@permission_classes([IsAuthenticated, ])
@authentication_classes([TokenAuthentication, ])
def show_susu_group_positions(request):
    payload = {}

    errors = {}
    group_errors = []
    user_id_errors = []

    positions_list = []

    user_id = request.query_params.get('user_id', None)
    group_id = request.query_params.get('group_id', None)

    if not user_id:
        user_id_errors.append('User ID is required.')
        if user_id_errors:
            errors['user_id'] = user_id_errors
            payload['message'] = "Error"
            payload['errors'] = errors
            return Response(payload, status=status.HTTP_404_NOT_FOUND)

    if not group_id:
        group_errors.append('Group ID is required.')
        if group_errors:
            errors['group_id'] = group_errors
            payload['message'] = "Error"
            payload['errors'] = errors
            return Response(payload, status=status.HTTP_404_NOT_FOUND)

    try:
        susu_group = SusuGroup.objects.get(group_id=group_id)
    except SusuGroup.DoesNotExist:
        group_errors.append('Group does not exist.')
        if group_errors:
            errors['group_id'] = group_errors
            payload['message'] = "Error"
            payload['errors'] = errors
            return Response(payload, status=status.HTTP_404_NOT_FOUND)

    positions = SusuPosition.objects.filter(group=susu_group).filter(cycle_number=susu_group.cycle_number).filter(
        rotation_number=susu_group.rotation_number)

    for position_num in range(1, int(susu_group.capacity) + 1):
        position = positions.filter(position=position_num).first()
        if position:
            position_dict = {
                'position': position.position,
                'state': position.state,
                'full_name': position.susu_user.user.full_name if position.state == 'occupied' else None,
                'paid_amount': position.susu_user.paid_amount,
                'paid_on': position.susu_user.paid_on,
                'paid': position.susu_user.paid,
                'photo': position.susu_user.user.personal_info.photo.url
            }

        else:
            position_dict = {
                'position': position_num,
                'state': 'vacant',
                'user': None
            }

        positions_list.append(position_dict)
        # print(positions_list)

    payload['message'] = "Successful"
    payload['data'] = positions_list

    return Response(payload, status=status.HTTP_200_OK)


@api_view(['GET', ])
@permission_classes([IsAuthenticated, ])
@authentication_classes([TokenAuthentication, ])
def display_payment_schedule(request):
    payload = {}
    data = {}

    errors = {}
    group_errors = []
    user_id_errors = []

    user_id = request.query_params.get('user_id', None)
    group_id = request.query_params.get('group_id', None)
    user_position = request.query_params.get('position', None)

    if not user_id:
        user_id_errors.append('User ID is required.')
        if user_id_errors:
            errors['user_id'] = user_id_errors
            payload['message'] = "Error"
            payload['errors'] = errors
            return Response(payload, status=status.HTTP_404_NOT_FOUND)

    if not group_id:
        group_errors.append('Group ID is required.')
        if group_errors:
            errors['group_id'] = group_errors
            payload['message'] = "Error"
            payload['errors'] = errors
            return Response(payload, status=status.HTTP_404_NOT_FOUND)

    try:
        susu_group = SusuGroup.objects.get(group_id=group_id)
    except SusuGroup.DoesNotExist:
        group_errors.append('Group does not exist.')
        if group_errors:
            errors['group_id'] = group_errors
            payload['message'] = "Error"
            payload['errors'] = errors
            return Response(payload, status=status.HTTP_404_NOT_FOUND)

    group_capacity = susu_group.capacity
    group_cycle_amount = susu_group.target_amount
    start_date = susu_group.start_date
    current_date = date.today()

    if susu_group.payment_cycle == "Monthly":
        payout_date = start_date + datetime.timedelta(days=int(user_position) * 30)
        payout_amount = int(group_capacity) * int(group_cycle_amount) - group_cycle_amount

        print("###########")
        print(payout_date)
        print(payout_amount)

    if susu_group.payment_cycle == "Weekly":
        payout_date = start_date + datetime.timedelta(weeks=int(user_position))
        payout_amount = int(group_capacity) * int(group_cycle_amount) - group_cycle_amount

        print("###########")
        print(payout_date)
        print(payout_amount)

    if susu_group.payment_cycle == "Yearly":
        payout_date = start_date.replace(year=start_date.year + int(user_position))
        payout_amount = int(group_capacity) * int(group_cycle_amount) - group_cycle_amount
        print("###########")
        print(payout_date)
        print(payout_amount)

    data['payout_amount'] = payout_amount
    data['payout_date'] = payout_date.strftime("%d-%m-%y")

    payload['message'] = "Successful"
    payload['data'] = data

    return Response(payload, status=status.HTTP_200_OK)


@api_view(['POST', ])
@permission_classes([IsAuthenticated, ])
@authentication_classes([TokenAuthentication, ])
def join_susu_group_site(request):
    payload = {}
    data = {}

    payload['message'] = "Successful"
    payload['data'] = data

    return Response(payload, status=status.HTTP_200_OK)


@api_view(['POST', ])
@permission_classes([IsAuthenticated, ])
@authentication_classes([TokenAuthentication, ])
def join_susu_group_view(request):
    payload = {}
    data = {}

    errors = {}
    position_errors = []

    user_id = request.data.get('user_id', '0')
    group_id = request.data.get('group_id', '0')
    position = request.data.get('position', '0')


    group = SusuGroup.objects.get(group_id=group_id)

    user = User.objects.get(user_id=user_id)
    personal_info = PersonalInfo.objects.get(user=user)

    group_position_exist = SusuPosition.objects.all().filter(group=group).filter(position=position).first()

    if group_position_exist:
        position_errors.append('The position is already occupied. Choose another position')
        if position_errors:
            errors['position'] = position_errors
            payload['message'] = "Error"
            payload['errors'] = errors
            return Response(payload, status=status.HTTP_404_NOT_FOUND)

    susu_group_user = SusuGroupUser.objects.create(
        user=user,
        payment_option=personal_info.payment_method,
        payment_number=personal_info.phone,
        rotation_number=group.rotation_number,
        cycle_number=group.cycle_number,
        group_id=group.group_id

    )
    group.susu_group_users.add(susu_group_user)
    group.number_of_people = int(group.number_of_people) + 1
    group.save()

    group_position = SusuPosition.objects.create(
        position=int(position),
        state="occupied",
        susu_user=susu_group_user,
        group=group,
        rotation_number=group.rotation_number,
        cycle_number=group.cycle_number,

    )

    group_capacity = group.capacity
    group_cycle_amount = group.target_amount
    start_date = group.start_date

    if group.payment_cycle == "Monthly":
        due_date = start_date + datetime.timedelta(days=30)

        payment_schedule = PaymentSchedule.objects.create(
            group_user=susu_group_user,
            user_susu_group=group,
            payment_for=group.start_date.strftime("%B"),
            due_date=due_date,
            amount=group.target_amount,
            rotation_number=group.rotation_number,
            cycle_number=group.cycle_number
        )

    if group.payment_cycle == "Weekly":
        payout_date = start_date + datetime.timedelta(weeks=1)

        payment_schedule = PaymentSchedule.objects.create(
            group_user=susu_group_user,
            user_susu_group=group,
            payment_for="Week " + str(group.rotation_number),
            due_date=payout_date,
            amount=group.target_amount,
            rotation_number=group.rotation_number,
            cycle_number=group.cycle_number
        )

    if group.payment_cycle == "Yearly":
        pass

    data['group_id'] = group_id

    new_activity = AllActivity.objects.create(
        user=user,
        subject="Join Group",
        body=user.email + " Just joined a group"
    )
    new_activity.save()

    new_notification = Notification.objects.create(
        user=user,
        subject="Join Group",
        body=" You joined a group called " + group.group_name
    )
    new_notification.save()

    payload['message'] = "Successful"
    payload['data'] = data

    return Response(payload, status=status.HTTP_200_OK)


@api_view(['POST', ])
@permission_classes([IsAuthenticated, ])
@authentication_classes([TokenAuthentication, ])
def join_private_susu_group_view(request):
    payload = {}
    data = {}

    errors = {}

    group_code_errors = []

    user_id = request.data.get('user_id', '0')


    group_code = request.data.get('group_code', '0')

    try:
        group = SusuGroup.objects.get(group_code=group_code)
    except SusuGroup.DoesNotExist:
        group = None

    if not group:
        group_code_errors.append('Invalid group code')
        errors['group_code'] = group_code_errors
        payload['message'] = "Error"
        payload['errors'] = errors
        return Response(payload, status=status.HTTP_404_NOT_FOUND)

    user = User.objects.get(user_id=user_id)

    data['group_id'] = group.group_id
    payload['message'] = "Successful"
    payload['data'] = data

    return Response(payload, status=status.HTTP_200_OK)


@api_view(['POST', ])
@permission_classes([IsAuthenticated, ])
@authentication_classes([TokenAuthentication, ])
def make_contribution_to_group(request):
    payload = {}
    data = {}

    user_id = request.data.get('user_id', '0')
    group_id = request.data.get('group_id', '0')
    momo_reference = request.data.get('momo_reference', '0')
    paid_amount = request.data.get('paid_amount', '0')

    user = User.objects.get(user_id=user_id)

    susu_group_user = None

    group_detail = SusuGroup.objects.get(group_id=group_id)
    wallet = Wallet.objects.get(user=user)

    all_group_users = group_detail.susu_group_users.all()
    for group_user in all_group_users:
        if group_user.user == user:
            susu_group_user = group_user

    payment_schedule = PaymentSchedule.objects.all().filter(group_user=group_user).filter(
        user_susu_group=group_detail).filter(cycle_number=group_detail.cycle_number).filter(
        rotation_number=group_detail.rotation_number).first()
    payment_schedule.status = "PAID"
    payment_schedule.save()


    susu_group_user.momo_reference = momo_reference
    susu_group_user.paid = True
    susu_group_user.paid_amount = paid_amount
    susu_group_user.paid_on = timezone.now()
    susu_group_user.confirm_payment = False
    susu_group_user.save()

    user_balance = wallet.balance
    target_amount = group_detail.target_amount

    new_user_balance = int(user_balance) - int(target_amount)
    wallet.balance = new_user_balance
    wallet.save()

    new_contribution = Contribution.objects.create(
        susu_user=susu_group_user,
        group=group_detail,
        amount=target_amount,
        rotation_number=group_detail.rotation_number,
        cycle_number=group_detail.cycle_number
    )

    new_payment = Payment.objects.create(
        user=user,
        amount=target_amount,
        notes="Contribution for " + group_detail.group_name,
        group=group_detail,
        payment_for=group_detail.start_date.strftime("%B"),
        payment_method="Mobile Money",
        payment_type='Contribution',
        rotation_number=group_detail.rotation_number,
        cycle_number=group_detail.cycle_number
    )

    new_notification = Notification.objects.create(
        user=user,
        subject="Contribution for " + group_detail.group_name,
        body="You just made a payment to " + group_detail.group_name + " We will send you a notification as soon as the receiver confirms your payment."
    )
    new_notification.save()

    # Send sender push Notification
    sender_push_not = send_push_notification(
        "Contribution for " + group_detail.group_name,
        "You just made a payment to " + group_detail.group_name + " We will send you a notification as soon as the receiver confirms your payment.",
        user.fcm_token
    )

    # Send sender Email
    sender_email = send_mail(
        "Contribution for " + group_detail.group_name,
        "You just made a payment to " + group_detail.group_name + " We will send you a notification as soon as the receiver confirms your payment.",
        'no-reply@teamalfy.co.uk',
        [user.email],
        fail_silently=False,
    )

    # check for receiver and send notification
    for susu_user in group_detail.susu_group_users.all():
        user_position = SusuPosition.objects.filter(susu_user=susu_user).filter(group=group_detail).filter(
            cycle_number=group_detail.cycle_number).filter(rotation_number=group_detail.rotation_number).first()

        if int(user_position.position) == int(group_detail.rotation_number):
            print(susu_user)

            receiver_email = susu_user.user.email
            fcm_token = susu_user.user.fcm_token
            subject = "Contribution for " + group_detail.group_name
            body = user.full_name + " just made a payment to you momo account, please check and confirm the payment."

            # Send notification
            receiver_notification = Notification.objects.create(
                user=user,
                subject=subject,
                body=body
            )
            receiver_notification.save()

            # Send Email
            receiver_email = send_mail(
                subject,
                body,
                'no-reply@teamalfy.co.uk',
                [receiver_email],
                fail_silently=False,
            )

            # Send push Notification
            receiver_push_not = send_push_notification(subject, body, fcm_token)

    data['group_id'] = group_id

    payload['message'] = "Successful"
    payload['data'] = data

    return Response(payload, status=status.HTTP_200_OK)


@api_view(['POST', ])
@permission_classes([IsAuthenticated, ])
@authentication_classes([TokenAuthentication, ])
def receive_payouts_view(request):
    payload = {}
    data = {}

    user_id = request.data.get('user_id', '0')
    group_id = request.data.get('group_id', '0')

    user = User.objects.get(user_id=user_id)

    group_detail = SusuGroup.objects.get(group_id=group_id)
    wallet = Wallet.objects.get(user=user)
    susu_group_user = SusuGroupUser.objects.get(user=user)

    user_balance = wallet.balance
    target_amount = group_detail.target_amount

    total_payout_amount = int(target_amount) * int(group_detail.capacity)
    payout_to_user = int(total_payout_amount) - int(target_amount)

    new_user_balance = int(user_balance) + int(payout_to_user)

    wallet.balance = new_user_balance
    wallet.save()

    new_payout = Payout.objects.create(
        susu_user=susu_group_user,
        group=group_detail,
        amount=payout_to_user,
        cycle_number=group_detail.cycle_number
    )

    # Increase cycle number
    group_detail.cycle_number = int(group_detail.cycle_number) + 1
    group_detail.save()

    payload['message'] = "Successful"
    payload['data'] = data

    return Response(payload, status=status.HTTP_200_OK)


@api_view(['POST', ])
@permission_classes([IsAuthenticated, ])
@authentication_classes([TokenAuthentication, ])
def payout_reminder_view(request):
    payload = {}
    data = {}

    payload['message'] = "Successful"
    payload['data'] = data

    return Response(payload, status=status.HTTP_200_OK)


@api_view(['GET'])
@permission_classes([IsAuthenticated])
@authentication_classes([TokenAuthentication])
def show_payment_confirmation_list(request):
    payload = {}
    data = {}

    user_id = request.query_params.get('user_id', None)
    group_id = request.query_params.get('group_id', None)

    user = User.objects.get(user_id=user_id)
    group = SusuGroup.objects.get(group_id=group_id)

    susu_g_user = None
    all_users = []

    for susu_user in group.susu_group_users.all():
        if susu_user.user == user:
            print(susu_user)
            susu_g_user = susu_user

    if susu_g_user not in group.susu_group_users.all():
        print("Not in group")
        payload['message'] = "Successful"
        payload['group'] = "Not in group"

    if susu_g_user.is_turn == False:
        print("Not Your turn")
        payload['message'] = "Successful"
        payload['group'] = "Not Your turn"


    elif susu_g_user.is_turn == True:
        print("Your turn")
        for _susu_user in group.susu_group_users.all():
            personal_info = PersonalInfo.objects.get(user=_susu_user.user)
            if _susu_user.is_turn == False:
                print(_susu_user)
                the_user = {
                    'user_id': _susu_user.user.user_id,
                    'full_name': _susu_user.user.full_name,
                    'phone': personal_info.phone,
                    'photo': personal_info.photo.url,

                    'is_turn': _susu_user.is_turn,
                    'group_id': group.group_id,
                    'paid': _susu_user.paid,
                    'confirm_payment': _susu_user.confirm_payment,
                    'momo_reference': _susu_user.momo_reference
                }
                all_users.append(the_user)

    payload['message'] = "Successful"
    payload['data'] = all_users

    return Response(payload, status=status.HTTP_200_OK)


@api_view(['GET'])
@permission_classes([IsAuthenticated])
@authentication_classes([TokenAuthentication])
def show_payment_confirmation_list_CHAT(request):
    payload = {}
    data = {}

    user_id = request.query_params.get('user_id', None)
    group_id = request.query_params.get('group_id', None)

    user = get_object_or_404(User, user_id=user_id)
    group = get_object_or_404(SusuGroup, group_id=group_id)

    all_users = []
    for susu_user in group.susu_group_users.all():
        if not susu_user.is_turn:
            print("####################")
            print("It is not his turn")
            print(susu_user.user)
            the_user = {
                'user_id': susu_user.user.user_id,
                'full_name': susu_user.user.full_name,
                'is_turn': susu_user.is_turn,
                'group_id': group.group_id,
                'paid': susu_user.paid,
                'confirm_payment': susu_user.confirm_payment,
                'momo_reference': susu_user.momo_reference
            }
            all_users.append(the_user)
        elif susu_user.is_turn:
            print("####################")
            print("It is his turn")
            print(susu_user.user)
            if susu_user.user.user_id == user_id:
                print("He is the user checking")
                print(susu_user.user)
                if susu_user.is_turn:
                    print(susu_user.user.email)
                    payload['message'] = "Successful"
                    payload['data'] = all_users
            else:
                payload['message'] = "Successful"
                payload['data'] = "Not User's Turn."

    if 'message' not in payload:
        payload['message'] = "Successful"
        payload['data'] = {}

    return Response(payload, status=status.HTTP_200_OK)


@api_view(['GET', ])
@permission_classes([IsAuthenticated, ])
@authentication_classes([TokenAuthentication, ])
def show_payment_confirmation_list2222(request):
    payload = {}
    data = {}

    user_id = request.query_params.get('user_id', None)
    group_id = request.query_params.get('group_id', None)

    user = User.objects.get(user_id=user_id)
    group = SusuGroup.objects.get(group_id=group_id)

    all_users = []
    for susu_user in group.susu_group_users.all():
        if susu_user.is_turn == False:
            print("####################")
            print("It is not his turn")
            print(susu_user.user)
            the_user = {}
            the_user['user_id'] = susu_user.user.user_id
            the_user['user_id'] = susu_user.user.full_name
            the_user['is_turn'] = susu_user.is_turn
            the_user['group_id'] = group.group_id
            the_user['paid'] = susu_user.paid
            the_user['confirm_payment'] = susu_user.confirm_payment
            the_user['momo_reference'] = susu_user.momo_reference
            all_users.append(the_user)
        if susu_user.is_turn == True:
            print("####################")
            print("It is his turn")
            print(susu_user.user)
            if susu_user.user.user_id == user_id:
                print("He is the user checking")
                print(susu_user.user)
                if susu_user.is_turn == True:
                    print(susu_user.user.email)
                    payload['message'] = "Successful"
                    payload['data'] = all_users
            else:
                payload['message'] = "Successful"
                payload['data'] = {}
                payload['data'] = "Not User's Turn."

            # if susu_user.user.user_id == user_id:
            #     continue  # Skip the user with the specified user_id
            # elif susu_user.user.user_id == user_id:
            #     if susu_user.is_turn == True:
            #         print(susu_user.user.email)
            #         the_user = {}
            #         the_user['user_id'] = susu_user.user.user_id
            #         the_user['user_id'] = susu_user.user.full_name
            #         the_user['is_turn'] = susu_user.is_turn
            #         the_user['group_id'] = group.group_id
            #         the_user['paid'] = susu_user.paid
            #         the_user['momo_reference'] = susu_user.momo_reference
            #         all_users.append(the_user)

    # print(all_users)

    # payload['message'] = "Successful"

    return Response(payload, status=status.HTTP_200_OK)


@api_view(['POST', ])
@permission_classes([IsAuthenticated, ])
@authentication_classes([TokenAuthentication, ])
def confirm_payment(request):
    payload = {}
    data = {}

    user_id = request.data.get('user_id', '0')
    other_user_id = request.data.get('other_user_id', '0')
    group_id = request.data.get('group_id', '0')
    momo_reference = request.data.get('momo_reference', '0')

    user = User.objects.get(user_id=user_id)
    other_user = User.objects.get(user_id=other_user_id)

    other_group_user = SusuGroupUser.objects.all().filter(user=other_user).first()

    group = SusuGroup.objects.get(group_id=group_id)
    other_user_pay_schedule = PaymentSchedule.objects.filter(group_user=other_group_user).filter(
        user_susu_group=group).first()

    if momo_reference == other_group_user.momo_reference:
        print("#####################")
        print("TRUE MOMOOOOOO")
        other_group_user.confirm_payment = True
        other_group_user.save()

        other_user_pay_schedule.status = "CONFIRM PAID"
        other_user_pay_schedule.save()

        payload['message'] = "Successful"
        payload['data'] = 'User payment confirmed'
    else:
        print("#####################")
        print("MAGAE YOU FOR PAY")
        other_group_user.confirm_payment = False
        other_group_user.save()
        payload['message'] = "Successful"
        payload['data'] = 'User payment not confirmed'

    # payload['message'] = "Successful"
    # payload['data'] = data
    #
    return Response(payload, status=status.HTTP_200_OK)


@api_view(['POST', ])
@permission_classes([IsAuthenticated, ])
@authentication_classes([TokenAuthentication, ])
def kickout_user(request):
    payload = {}
    data = {}
    user_id_errors = []
    group_id_errors = []
    errors = {}

    user_id = request.data.get('user_id', '0')
    group_id = request.data.get('group_id', '0')
    kickout_user_id = request.data.get('kickout_user_id', '0')

    if not user_id:
        user_id_errors.append('User ID is required.')
        if user_id_errors:
            errors['user_id'] = user_id_errors
            payload['message'] = "Error"
            payload['errors'] = errors
            return Response(payload, status=status.HTTP_404_NOT_FOUND)

    if not kickout_user_id:
        user_id_errors.append('Kickout User ID is required.')
        if user_id_errors:
            errors['user_id'] = user_id_errors
            payload['message'] = "Error"
            payload['errors'] = errors
            return Response(payload, status=status.HTTP_404_NOT_FOUND)

    if not group_id:
        group_id_errors.append('Group ID is required.')
        if group_id_errors:
            errors['group_id'] = group_id_errors
            payload['message'] = "Error"
            payload['errors'] = errors
            return Response(payload, status=status.HTTP_404_NOT_FOUND)

    user = User.objects.get(user_id=user_id)
    kickout_user = User.objects.get(user_id=kickout_user_id)

    # group_user = SusuGroupUser.objects.all().filter(user=user)
    group = SusuGroup.objects.get(group_id=group_id)

    if group.group_creator == user:
        print(group.group_creator)
        payload['message'] = "Successful"
        payload['group_info'] = "User kicked out successfully."
        data['group_id'] = group.group_id

        for group_user in group.susu_group_users.all():

            if group_user.user == kickout_user:
                group.susu_group_users.remove(group_user)
                group.number_of_people = int(group.number_of_people) - 1
                group.save()

                payment_schedules = PaymentSchedule.objects.all().filter(group_user=group_user)
                payment_schedules.delete()

                positions = SusuPosition.objects.all().filter(susu_user=group_user)
                positions.delete()

                group_user.delete()

                new_activity = AllActivity.objects.create(
                    user=user,
                    subject="Kick out",
                    body=user.email + " Just got kicked out of a group"
                )
                new_activity.save()
                new_notification = Notification.objects.create(
                    user=user,
                    subject="Kick out",
                    body="You just got kicked out of a group called " + group.group_name
                )
                new_notification.save()

    else:
        print("NOT GROUP CREATOR")
        payload['message'] = "Successful"
        payload['group_info'] = "You are not the creator of this group."

    # data['group_id'] = group.group_id
    #
    # new_activity = AllActivity.objects.create(
    #    user=user,
    #    subject="Kick out",
    #    body=user.email + " Just got kicked out of a group"
    # )
    # new_activity.save()
    #
    # new_notification = Notification.objects.create(
    #    user=user,
    #    subject="Kick out",
    #    body="You just got kicked out of a group called " + group.group_name
    # )
    # new_notification.save()

    payload['message'] = "Successful"
    payload['data'] = data

    return Response(payload, status=status.HTTP_200_OK)


@api_view(['POST', ])
@permission_classes([IsAuthenticated, ])
@authentication_classes([TokenAuthentication, ])
def delete_group(request):
    payload = {}
    data = {}
    user_id_errors = []
    group_id_errors = []
    errors = {}

    user_id = request.data.get('user_id', '0')
    group_id = request.data.get('group_id', '0')

    if not user_id:
        user_id_errors.append('User ID is required.')
        if user_id_errors:
            errors['user_id'] = user_id_errors
            payload['message'] = "Error"
            payload['errors'] = errors
            return Response(payload, status=status.HTTP_404_NOT_FOUND)

    if not group_id:
        group_id_errors.append('Group ID is required.')
        if group_id_errors:
            errors['group_id'] = group_id_errors
            payload['message'] = "Error"
            payload['errors'] = errors
            return Response(payload, status=status.HTTP_404_NOT_FOUND)

    user = User.objects.get(user_id=user_id)
    group_detail = SusuGroup.objects.get(group_id=group_id)
    group_name = group_detail.group_name

    if group_detail.group_creator != user:
        user_id_errors.append('You dont have permissions to delete this group')
        if user_id_errors:
            errors['user_id'] = user_id_errors
            payload['message'] = "Error"
            payload['errors'] = errors
            return Response(payload, status=status.HTTP_404_NOT_FOUND)

    group_detail.delete()

    new_activity = AllActivity.objects.create(
        user=user,
        subject="Delete Group",
        body=user.email + " Deleted a group"
    )
    new_activity.save()

    new_notification = Notification.objects.create(
        user=user,
        subject="Delete Group",
        body="You deleted a group called " + group_name
    )
    new_notification.save()

    payload['message'] = "Successful"
    payload['data'] = "Group deleted successfully"

    return Response(payload, status=status.HTTP_200_OK)


def send_push_notification(title, body, registration_id):
    push_service = FCMNotification(api_key=FCM_SERVER_KEY)
    message_title = title
    message_body = body
    result = push_service.notify_single_device(registration_id=registration_id, message_title=message_title,
                                               message_body=message_body)
    return result


#####################################
###  AUTOMATION
#########################


@shared_task
def postpone_start_date():
    for group in SusuGroup.objects.all():
        group_capacity = group.capacity
        group_number_of_people = group.number_of_people
        start_date = group.start_date

        print(group.group_name)
        print(group_capacity)
        print(start_date.date())

        if group_number_of_people != group_capacity:
            if start_date.date() == timezone.now().date():
                print("#################")
                print("Move ........")

                new_start_date = start_date + datetime.timedelta(weeks=1)

                susu_group = SusuGroup.objects.get(group_id=group.group_id)
                susu_group.start_date = new_start_date
                susu_group.cycle_started = False
                susu_group.save()

                # send message to users in group
                for susu_user in susu_group.susu_group_users.all():

                    pay_schedule = PaymentSchedule.objects.filter(group_user=susu_user).filter(
                        user_susu_group=group).filter(cycle_number=group.cycle_number).filter(
                        rotation_number=group.rotation_number).first()

                    if group.payment_cycle == "Monthly":
                        print("Monthly")
                        due_date = start_date + datetime.timedelta(days=30)

                        pay_schedule.payment_for = group.start_date.strftime("%B")
                        pay_schedule.due_date = due_date
                        pay_schedule.save()

                        send_mail(
                            'Group Cycle start date postponed',
                            'Because all the positions in ' + susu_group.group_name + ' is not occupied, the start date of the cycle has been postponed to ' + str(
                                new_start_date.date()),
                            'no-reply@teamalfy.co.uk',
                            [susu_user.user.email],
                            fail_silently=False,
                        )


                    elif group.payment_cycle == "Weekly":
                        print("Weekly")
                        due_date = start_date + datetime.timedelta(weeks=1)

                        pay_schedule.payment_for = "Week " + str(group.rotation_number)
                        pay_schedule.due_date = due_date

                        pay_schedule.save()

                        send_mail(
                            'Group Cycle start date postponed',
                            'Because all the positions in ' + susu_group.group_name + ' is not occupied, the start date of the cycle has been postponed to ' + str(
                                new_start_date.date()),
                            'no-reply@teamalfy.co.uk',
                            [susu_user.user.email],
                            fail_silently=False,
                        )

                new_activity = AllActivity.objects.create(
                    subject="Group Cycle start date postponed",
                    body='Because all the positions in ' + susu_group.group_name + ' is not occupied, the start date of the cycle has been postponed to ' + str(
                        new_start_date.date())
                )
                new_activity.save()

        elif group_number_of_people == group_capacity:
            if start_date.date() > timezone.now().date() and group.cycle_started == False:
                print("#################")
                print("START TOMORROW ........")

                now = timezone.now()
                next_day = now + timedelta(days=1)

                # new_start_date = datetime.now().date() + datetime.timedelta(days=1)

                susu_group = SusuGroup.objects.get(group_id=group.group_id)
                susu_group.start_date = next_day.date()
                susu_group.cycle_started = True
                susu_group.save()

                # send message to users in group
                for susu_user in susu_group.susu_group_users.all():

                    pay_schedule = PaymentSchedule.objects.filter(group_user=susu_user).filter(
                        user_susu_group=group).filter(cycle_number=group.cycle_number).filter(
                        rotation_number=group.rotation_number).first()

                    if group.payment_cycle == "Monthly":
                        due_date = start_date + datetime.timedelta(days=30)

                        pay_schedule.payment_for = group.start_date.strftime("%B")
                        pay_schedule.due_date = due_date
                        pay_schedule.save()


                    elif group.payment_cycle == "Weekly":
                        due_date = start_date + datetime.timedelta(weeks=1)

                        pay_schedule.payment_for = "Week " + str(group.rotation_number)
                        pay_schedule.due_date = due_date
                        pay_schedule.save()

                    send_mail(
                        'Group Cycle Starts',
                        'The positions in this cycle are now full and the start date of ' + susu_group.group_name + ' is tomorrow ' + str(
                            susu_group.start_date),
                        'no-reply@teamalfy.co.uk',
                        [susu_user.user.email],
                        fail_silently=False,
                    )

                new_activity = AllActivity.objects.create(
                    subject="Group Cycle Starts",
                    body='The positions in this cycle are now full and the start date of ' + susu_group.group_name + ' is tomorrow ' + str(
                        susu_group.start_date),
                )
                new_activity.save()

            elif start_date.date() == timezone.now().date() and group.cycle_started == True:
                susu_group = SusuGroup.objects.get(group_id=group.group_id)

                for susu_user in susu_group.susu_group_users.all():
                    send_mail(
                        'Group Cycle Starts',
                        'The Cycle for ' + susu_group.group_name + ' starts today.',
                        'no-reply@teamalfy.co.uk',
                        [susu_user.user.email],
                        fail_silently=False,
                    )
                new_activity = AllActivity.objects.create(
                    subject="Group Cycle Starts",
                    body='The Cycle for ' + susu_group.group_name + ' starts today.'
                )
                new_activity.save()


@shared_task
def send_payment_due_notification_due_before():
    for group in SusuGroup.objects.all():
        for susu_user in group.susu_group_users.all():
            user_payment_schedule = PaymentSchedule.objects.all().filter(group_user=susu_user).filter(
                cycle_number=group.cycle_number).filter(rotation_number=group.rotation_number).first()
            if user_payment_schedule.status == "PAID":
                print("User paid already")
                print(user_payment_schedule.group_user.user.email)
                print(user_payment_schedule.status)
            elif user_payment_schedule.status == "PAY NOW":
                if user_payment_schedule.due_date.date() - datetime.timedelta(days=1) == timezone.now().date():
                    print("PAY NOWWWWWWWW")
                    print(user_payment_schedule.group_user.user.email)
                    print(user_payment_schedule.status)

                    send_mail(
                        'Payment Due Reminder',
                        'Hello ' + user_payment_schedule.group_user.user.full_name + ', You are reminded to make your payment for ' + group.group_name + " by the end of tomorrow.",
                        'no-reply@teamalfy.co.uk',
                        [user_payment_schedule.group_user.user.email.lower()],
                        fail_silently=False,
                    )

                    new_activity = AllActivity.objects.create(
                        subject="Payment Due Reminder",
                        body='Hello ' + user_payment_schedule.group_user.user.full_name + ', You are reminded to make your payment for ' + group.group_name + " by the end of tomorrow.",
                    )
                    new_activity.save()


@shared_task
def send_payment_due_notification_due_day():
    for group in SusuGroup.objects.all():
        for susu_user in group.susu_group_users.all():
            user_payment_schedule = PaymentSchedule.objects.all().filter(group_user=susu_user).filter(
                cycle_number=group.cycle_number).filter(rotation_number=group.rotation_number).first()
            if user_payment_schedule.status == "PAID":
                print("User paid already")
                print(user_payment_schedule.group_user.user.email)
                print(user_payment_schedule.status)
            elif user_payment_schedule.status == "PAY NOW":
                if user_payment_schedule.due_date.date() == timezone.now().date():
                    print("PAY NOWWWWWWWW")
                    print(user_payment_schedule.group_user.user.email)
                    print(user_payment_schedule.status)

                    send_mail(
                        'Payment Due Reminder',
                        'Hello ' + user_payment_schedule.group_user.user.full_name + ', You  are reminded to make your payment for ' + group.group_name + " by the end of today.",
                        'no-reply@teamalfy.co.uk',
                        [user_payment_schedule.group_user.user.email.lower()],
                        fail_silently=False,
                    )

                    new_activity = AllActivity.objects.create(
                        subject="Payment Due Reminder",
                        body='Hello ' + user_payment_schedule.group_user.user.full_name + ', You are reminded to make your payment for ' + group.group_name + " by the end of today.",
                    )
                    new_activity.save()


@shared_task
def send_payment_due_notification_due_after():
    for group in SusuGroup.objects.all():
        for susu_user in group.susu_group_users.all():
            user_payment_schedule = PaymentSchedule.objects.all().filter(group_user=susu_user).filter(
                cycle_number=group.cycle_number).filter(rotation_number=group.rotation_number).first()
            if user_payment_schedule.status == "PAID":
                print("User paid already")
                print(user_payment_schedule.group_user.user.email)
                print(user_payment_schedule.status)
            elif user_payment_schedule.status == "PAY NOW":
                if user_payment_schedule.due_date.date() < timezone.now().date():
                    print("PAY NOWWWWWWWW")
                    print(user_payment_schedule.group_user.user.email)
                    print(user_payment_schedule.status)

                    send_mail(
                        'PAY NOW  REMINDER',
                        'Hello ' + user_payment_schedule.group_user.user.full_name + ', You are reminded to make your payment for ' + group.group_name + " NOW!!.",
                        'no-reply@teamalfy.co.uk',
                        [user_payment_schedule.group_user.user.email.lower()],
                        fail_silently=False,
                    )

                    new_activity = AllActivity.objects.create(
                        subject="PAY NOW  REMINDER",
                        body='Hello ' + user_payment_schedule.group_user.user.full_name + ', You are reminded to make your payment for ' + group.group_name + "NOW!!.",
                    )
                    new_activity.save()


@api_view(['POST', ])
@permission_classes([])
@authentication_classes([])
def set_next_rotation_in_cycle(request):
    payload = {}
    data = {}

    group_id = request.data.get('group_id', '0')

    # group = SusuGroup.objects.get(group_id=group_id)

    all_confirmed = []
    for group in SusuGroup.objects.all():
        confirm_pay_schedules = PaymentSchedule.objects.filter(user_susu_group=group).filter(
            cycle_number=group.cycle_number).filter(status="CONFIRM PAID")
        if confirm_pay_schedules.count() == int(group.number_of_people):
            print("CONFIRMED EQUALS")

            group.rotation_number = int(group.rotation_number) + 1
            group.save()

        elif confirm_pay_schedules.count() != int(group.number_of_people):
            print("NOT CONFIRMED EQUALS")

    payload['message'] = "Successful"
    payload['data'] = data

    return Response(payload, status=status.HTTP_200_OK)
