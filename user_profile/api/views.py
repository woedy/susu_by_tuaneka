from django.contrib.auth import get_user_model
from rest_framework import status
from rest_framework.authentication import TokenAuthentication
from rest_framework.decorators import permission_classes, api_view, authentication_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response

from mysite.utils import base64_file
from susu_groups.models import SusuGroup
from user_profile.models import PersonalInfo

User = get_user_model()


@api_view(['GET', ])
@permission_classes([IsAuthenticated, ])
@authentication_classes([TokenAuthentication, ])
def get_user_profile_view(request):
    payload = {}
    data = {}
    user_data = {}

    user_id = request.query_params.get('user_id', None)

    user = User.objects.get(user_id=user_id)
    personal_info = PersonalInfo.objects.get(user=user)

    user_data['user_id'] = user.user_id
    user_data['email'] = user.email
    user_data['full_name'] = user.full_name

    user_data['photo'] = personal_info.photo.url
    user_data['phone'] = personal_info.phone
    user_data['gender'] = personal_info.gender
    user_data['verified'] = personal_info.verified
    user_data['about_me'] = personal_info.about_me
    user_data['payment_method'] = personal_info.payment_method
    user_data['momo_reference'] = personal_info.momo_reference
    user_data['credit_ranking'] = personal_info.credit_ranking
    user_data['payment_count'] = personal_info.payment_count

    data['user_data'] = user_data


    groups = SusuGroup.objects.all()

    user_groups = []

    all_user_groups = []

    for group in groups:
        for user in group.susu_group_users.all():
            if user.user.user_id == user_id:
                print(user.user.full_name)
                print(group.group_name)
                user_groups.append(group)


    for group in user_groups:
        _data = {
            "group_id": group.group_id,
            "group_name": group.group_name,
        }
        all_user_groups.append(_data)


    print(all_user_groups)
    data['user_groups'] = all_user_groups

    payload['message'] = "Successful"
    payload['data'] = data

    return Response(payload, status=status.HTTP_200_OK)



@api_view(['POST', ])
@permission_classes([IsAuthenticated, ])
@authentication_classes([TokenAuthentication, ])
def update_user_profile_view(request):
    payload = {}
    data = {}
    user_data = {}

    user_id = request.data.get('user_id', '0').lower()

    email = request.data.get('email', '0').lower()
    full_name = request.data.get('full_name', '0')

    phone = request.data.get('phone', '0')
    photo = request.data.get('photo', '0')
    gender = request.data.get('gender', '0')
    about_me = request.data.get('about_me', '0')

    user = User.objects.get(user_id=user_id)
    user.email = email
    user.full_name = full_name
    user.save()

    personal_info = PersonalInfo.objects.get(user=user)
    personal_info.phone = phone
    personal_info.photo = base64_file(photo)
    personal_info.gender = gender
    personal_info.about_me = about_me
    personal_info.save()


    data['email'] = user.email
    data['full_name'] = user.full_name

    data['phone'] = personal_info.phone
    data['photo'] = personal_info.photo.url
    data['gender'] = personal_info.gender
    data['about_me'] = personal_info.about_me



    payload['message'] = "Successful"
    payload['data'] = data

    return Response(payload, status=status.HTTP_200_OK)