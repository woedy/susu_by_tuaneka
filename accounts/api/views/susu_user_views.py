import base64
import binascii
import io
import json
import os
import re

import requests
from PIL import Image

from django.conf import settings
from django.contrib.auth import get_user_model, authenticate
from django.contrib.auth.decorators import login_required
from django.contrib.auth.hashers import check_password
from django.contrib.auth.password_validation import validate_password
from django.core.files.base import ContentFile
from django.core.mail import send_mail
from django.template.loader import get_template
from rest_framework import status, generics
from rest_framework.authentication import TokenAuthentication
from rest_framework.authtoken.models import Token
from rest_framework.decorators import api_view, permission_classes, authentication_classes
from rest_framework.permissions import IsAuthenticated, AllowAny
from rest_framework.response import Response
from rest_framework.views import APIView

from accounts.api.serializers import SusuUserRegistrationSerializer, PasswordResetSerializer
from accounts.models import EmailActivation
from all_activities.models import AllActivity
from mysite.utils import generate_random_otp_code, generate_email_token, base64_file
from user_profile.models import PersonalInfo, Wallet

User = get_user_model()



#####################################################################
#
#
# SUSU USER VIEWS
#
#
#####################################################################


# Login Susu user


default_image_path = os.path.join(settings.MEDIA_ROOT, 'defaults/default_profile_image.png')

@api_view(['POST', ])
@permission_classes([])
@authentication_classes([])
def susu_user_registration_view(request):
    payload = {}
    data = {}
    errors = {}
    email_errors = []
    password_errors = []
    full_name_errors = []
    phone_errors = []

    payment_method_errors = []
    momo_reference_errors = []

    register_errors = []

    image_file = open(default_image_path, 'rb')



    email = request.data.get('email', '0').lower()
    full_name = request.data.get('full_name', '0')
    password = request.data.get('password', '0')
    password2 = request.data.get('password2', '0')
    phone = request.data.get('phone', '0')


    print(email)
    print(full_name)
    print(password)
    print(password2)
    print(phone)

    if not email:
        email_errors.append('Email is required.')
        if email_errors:
            errors['email'] = email_errors
            payload['message'] = "Error"
            payload['errors'] = errors
            return Response(payload, status=status.HTTP_404_NOT_FOUND)

    if not full_name:
        full_name_errors.append('Full name required.')
        if full_name_errors:
            errors['full_name'] = full_name_errors
            payload['message'] = "Error"
            payload['errors'] = errors
            return Response(payload, status=status.HTTP_404_NOT_FOUND)

    if not password:
        password_errors.append('Password required.')
        if password_errors:
            errors['password'] = password_errors
            payload['message'] = "Error"
            payload['errors'] = errors
            return Response(payload, status=status.HTTP_404_NOT_FOUND)

    if password != password2:
        password_errors.append('Password don\'t match.')
        if password_errors:
            errors['password'] = password_errors
            payload['message'] = "Error"
            payload['errors'] = errors
            return Response(payload, status=status.HTTP_404_NOT_FOUND)

    if not phone:
        phone_errors.append('Phone number required.')
        if phone_errors:
            errors['phone'] = phone_errors
            payload['message'] = "Error"
            payload['errors'] = errors
            return Response(payload, status=status.HTTP_404_NOT_FOUND)





    if check_email_exist(email):
        email_errors.append('Email already exist in our Susu database.')
        if email_errors:
            errors['email'] = email_errors
            payload['message'] = "Error"
            payload['errors'] = errors
            return Response(payload, status=status.HTTP_404_NOT_FOUND)

    if check_phone_exist(phone):
        email_errors.append('Phone number already exist in our Susu database.')
        if email_errors:
            errors['email'] = email_errors
            payload['message'] = "Error"
            payload['errors'] = errors
            return Response(payload, status=status.HTTP_404_NOT_FOUND)



    #Login User

    susu_data = {
        'email': email,
        'password': password
    }

    json_data = json.dumps(susu_data)
    url = 'https://dev.tuaneka.com/api/v1/login'

    headers = {
        # 'Authorization': 'Bearer <your_access_token>',
        'Content-Type': 'application/json',
        'Accept': 'application/json'
    }


    try:
        response = requests.post(url, data=json_data, headers=headers)
        if response.status_code == 200:
            if response.content:
                response_text = response.content.decode('utf-8')
                response_json = json.loads(response_text)
                print("#################### 200")

                print(response_json)

                serializer = SusuUserRegistrationSerializer(data=request.data)
                if serializer.is_valid():
                    user = serializer.save()
                    data['email'] = user.email
                    data['full_name'] = user.full_name
                    personal_info = PersonalInfo.objects.create(
                        user=user,
                        phone=phone,


                    )
                    personal_info.save()
                    data['phone'] = personal_info.phone

                wallet = Wallet.objects.create(
                    user=user,
                )

                token = Token.objects.get(user=user).key
                data['token'] = token

                email_token = generate_email_token()

                user = User.objects.get(email=email)
                user.email_token = email_token
                user.save()

                context = {
                    'email_token': email_token,
                    'email': user.email,
                    'full_name': user.full_name
                }

                txt_ = get_template("registration/emails/verify.txt").render(context)
                html_ = get_template("registration/emails/verify.html").render(context)

                subject = 'EMAIL CONFIRMATION CODE'
                from_email = settings.DEFAULT_FROM_EMAIL
                recipient_list = [user.email]

                sent_mail = send_mail(
                    subject,
                    txt_,
                    from_email,
                    recipient_list,
                    html_message=html_,
                    fail_silently=False
                )

                new_activity = AllActivity.objects.create(
                    user=user,
                    subject="User Registration",
                    body=user.email + " Just created an account."
                )
                new_activity.save()

        elif response.status_code == 422:

            #Login Error response.
            if response.content:
                response_text = response.content.decode('utf-8')
                response_json = json.loads(response_text)

                print("#################### 422")
                print(response_json)

                if response_json['message'] == "The given data was invalid.":

                    #Register the user in TUANEKA first
                    print("###############")
                    print("Register the user in TUANEKA first")




                    try:
                        tuaneka_data = {
                            'email': email,
                            'name': full_name,
                            'phone': phone,
                            'password': password,
                            'password_confirmation': password,


                        }

                        # json_data = json.dumps(tuaneka_data)
                        json_data = json.dumps(tuaneka_data)
                        reg_url = 'https://dev.tuaneka.com/api/v1/register'

                        headers = {
                            # 'Authorization': 'Bearer <your_access_token>',
                            #'Content-Type': 'application/json',
                            'Accept': 'application/json'
                        }

                        image_file = image_file
                        files = {'image': image_file}  # Pass the file-like object in the form data
                        response = requests.post(reg_url, files=files, data=tuaneka_data, headers=headers)



                        if response.status_code == 201:
                            if response.content:
                                response_text = response.content.decode('utf-8')
                                response_json = json.loads(response_text)

                                if response_json['message'] == "User registered successfully":
                                    print("TUANEKA #################### 201")
                                    print(response_json)

                                    print("#############################")
                                    print("WE ARE SUCCESSFUL REGISTER TO SUSU NOW")

                                    serializer = SusuUserRegistrationSerializer(data=request.data)
                                    if serializer.is_valid():
                                        user = serializer.save()
                                        data['email'] = user.email
                                        data['full_name'] = user.full_name
                                        personal_info = PersonalInfo.objects.create(
                                            user=user,
                                            phone=phone,


                                        )
                                        personal_info.save()
                                        data['phone'] = personal_info.phone

                                    wallet = Wallet.objects.create(
                                        user=user,
                                    )

                                    token = Token.objects.get(user=user).key
                                    data['token'] = token

                                    email_token = generate_email_token()

                                    user = User.objects.get(email=email)
                                    user.email_token = email_token
                                    user.save()

                                    context = {
                                        'email_token': email_token,
                                        'email': user.email,
                                        'full_name': user.full_name
                                    }

                                    txt_ = get_template("registration/emails/verify.txt").render(context)
                                    html_ = get_template("registration/emails/verify.html").render(context)

                                    subject = 'EMAIL CONFIRMATION CODE'
                                    from_email = settings.DEFAULT_FROM_EMAIL
                                    recipient_list = [user.email]

                                    sent_mail = send_mail(
                                        subject,
                                        txt_,
                                        from_email,
                                        recipient_list,
                                        html_message=html_,
                                        fail_silently=False
                                    )

                                    new_activity = AllActivity.objects.create(
                                        user=user,
                                        subject="User Registration",
                                        body=user.email + " Just created an account."
                                    )
                                    new_activity.save()




                        elif response.status_code == 422:
                            # Login Error response.
                            if response.content:
                                response_text = response.content.decode('utf-8')
                                response_json = json.loads(response_text)

                                print("TUANEKA #################### 422")
                                print(response_json)
                                t_errors = response_json.get('errors', {})

                                t_email_errors = t_errors.get('email', [])
                                for error in t_email_errors:
                                    # Perform actions for each email error
                                    # For example, log the errors or notify the user
                                    print("Email Error:", error)
                                    if error == "The email has already been taken.":
                                        print("####################")
                                        print("EMAIL TAKEN")

                                        # email_errors.append('Email available in Tuaneka database')
                                        # if email_errors:
                                        #     errors['email'] = email_errors
                                        #     payload['message'] = "Error"
                                        #     payload['errors'] = errors
                                        #     return Response(payload, status=status.HTTP_404_NOT_FOUND)

                                        serializer = SusuUserRegistrationSerializer(data=request.data)
                                        if serializer.is_valid():
                                            user = serializer.save()
                                            data['email'] = user.email
                                            data['full_name'] = user.full_name
                                            personal_info = PersonalInfo.objects.create(
                                                user=user,
                                                phone=phone,

                                            )
                                            personal_info.save()
                                            data['phone'] = personal_info.phone

                                        wallet = Wallet.objects.create(
                                            user=user,
                                        )

                                        token = Token.objects.get(user=user).key
                                        data['token'] = token

                                        email_token = generate_email_token()

                                        user = User.objects.get(email=email)
                                        user.email_token = email_token
                                        user.save()

                                        context = {
                                            'email_token': email_token,
                                            'email': user.email,
                                            'full_name': user.full_name
                                        }

                                        txt_ = get_template("registration/emails/verify.txt").render(context)
                                        html_ = get_template("registration/emails/verify.html").render(context)

                                        subject = 'EMAIL CONFIRMATION CODE'
                                        from_email = settings.DEFAULT_FROM_EMAIL
                                        recipient_list = [user.email]

                                        sent_mail = send_mail(
                                            subject,
                                            txt_,
                                            from_email,
                                            recipient_list,
                                            html_message=html_,
                                            fail_silently=False
                                        )

                                        new_activity = AllActivity.objects.create(
                                            user=user,
                                            subject="User Registration",
                                            body=user.email + " Just created an account."
                                        )
                                        new_activity.save()

                                t_phone_errors = t_errors.get('phone', [])
                                for error in t_phone_errors:
                                    # Perform actions for each phone error
                                    # For example, log the errors or notify the user
                                    print("Phone Error:", error)
                                    if error == "The phone has already been taken.":
                                        phone_errors.append('The phone has already been taken in Tauaneka database.')
                                        if phone_errors:
                                            errors['phone'] = phone_errors
                                            payload['message'] = "Error"
                                            payload['errors'] = errors
                                            return Response(payload, status=status.HTTP_404_NOT_FOUND)
                                    if error == "The phone must be in international format. Example +233248000000.":
                                        phone_errors.append('The phone must be in international format. Example +233248000000.')
                                        if phone_errors:
                                            errors['phone'] = phone_errors
                                            payload['message'] = "Error"
                                            payload['errors'] = errors
                                            return Response(payload, status=status.HTTP_404_NOT_FOUND)

                                t_password_errors = t_errors.get('password', [])
                                for error in t_password_errors:
                                    # Perform actions for each phone error
                                    # For example, log the errors or notify the user
                                    print("Password Error:", error)
                                    if error == "The password must contain at least one symbol.":
                                        password_errors.append('The password must contain at least one symbol.')
                                        if password_errors:
                                            errors['password'] = password_errors
                                            payload['message'] = "Error"
                                            payload['errors'] = errors
                                            return Response(payload, status=status.HTTP_404_NOT_FOUND)

                                t_image_errors = t_errors.get('image', [])
                                for error in t_image_errors:
                                    # Perform actions for each image error
                                    # For example, log the errors or notify the user
                                    print("Image Error:", error)





                    except requests.HTTPError as err:
                        if response.status_code == 422:
                            print(response.status_code)
                            print("42222222")





    except requests.HTTPError as err:
        if response.status_code == 422:
            print(response.status_code)
            print("42222222")
            print(err)
        print("Errooorrrrrr")

    payload['message'] = "Successful"
    payload['data'] = data

    image_file.close()

    return Response(payload, status=status.HTTP_200_OK)


def check_email_exist(email):

    qs = User.objects.filter(email=email)
    if qs.exists():
        return True
    else:
        return False


def check_phone_exist(phone):

    qs = PersonalInfo.objects.all().filter(phone=phone)
    if qs.exists():
        return True
    else:
        return False






@api_view(['POST', ])
@permission_classes([IsAuthenticated, ])
@authentication_classes([TokenAuthentication, ])
def register_update_profile_view(request):
    payload = {}
    data = {}
    user_data = {}

    user_id = request.data.get('user_id', '0').lower()


    photo = request.data.get('photo', '0')
    payment_method = request.data.get('payment_method', '0')
    momo_reference = request.data.get('momo_reference', '0')


    user = User.objects.get(user_id=user_id)


    personal_info = PersonalInfo.objects.get(user=user)
    personal_info.photo = base64_file(photo)
    personal_info.payment_method = payment_method
    personal_info.momo_reference = momo_reference

    personal_info.save()


    data['email'] = user.email
    data['full_name'] = user.full_name
    payload['message'] = "Successful"
    payload['data'] = data

    return Response(payload, status=status.HTTP_200_OK)





class SusuUserLogin(APIView):
    authentication_classes = []
    permission_classes = []

    def post(self, request):
        payload = {}
        data = {}

        email = request.data.get('email', '0')
        password = request.data.get('password', '0')
        fcm_token = request.data.get('fcm_token', '0')

        errors = {}
        email_errors = []
        password_errors = []
        fcm_token_errors = []

        print(email)
        print(password)
        print(fcm_token)

        if not email:
            email_errors.append('Email is required.')
        if email_errors:
            errors['email'] = email_errors
            payload['message'] = "Error"
            payload['errors'] = errors
            return Response(payload, status=status.HTTP_404_NOT_FOUND)


        if not password:
            password_errors.append('Password is required.')
        if password_errors:
            errors['password'] = password_errors
            payload['message'] = "Error"
            payload['errors'] = errors
            return Response(payload, status=status.HTTP_404_NOT_FOUND)

        if not fcm_token:
            fcm_token_errors.append('FCM device token required.')
        if fcm_token_errors:
            errors['fcm_token'] = fcm_token_errors
            payload['message'] = "Error"
            payload['errors'] = errors
            return Response(payload, status=status.HTTP_404_NOT_FOUND)


        qs = User.objects.filter(email=email)
        if qs.exists():
            not_active = qs.filter(email_verified=False)
            if not_active:
                reconfirm_msg = "resend confirmation email."
                msg1 = "Please check your email to confirm your account or " + reconfirm_msg.lower()
                email_errors.append(msg1)
            if email_errors:
                errors['email'] = email_errors
                payload['message'] = "Error"
                payload['errors'] = errors
                return Response(payload, status=status.HTTP_404_NOT_FOUND)

        if not check_password(email, password):
            email_errors.append('Invalid Credentials')
            if email_errors:
                errors['email'] = email_errors
                payload['message'] = "Error"
                payload['errors'] = errors
                return Response(payload, status=status.HTTP_404_NOT_FOUND)

        user = authenticate(email=email, password=password)
        if not user:
            email_errors.append('Invalid Credentials')
            if email_errors:
                errors['email'] = email_errors
                payload['message'] = "Error"
                payload['errors'] = errors
            return Response(payload, status=status.HTTP_404_NOT_FOUND)

        else:
            try:
                token = Token.objects.get(user=user)
            except Token.DoesNotExist:
                token = Token.objects.create(user=user)

            try:
                user_personal_info = PersonalInfo.objects.get(user=user)
            except PersonalInfo.DoesNotExist:
                user_personal_info = PersonalInfo.objects.create(user=user)

            user_personal_info.active = True

            user_personal_info.save()

            user.fcm_token = fcm_token
            user.save()




            data["user_id"] = user.user_id
            data["email"] = user.email
            data["full_name"] = user.full_name
            data["token"] = token.key
            data["first_login"] = user.first_login

            payload['message'] = "Successful"
            payload['data'] = data

            new_activity = AllActivity.objects.create(
                user=user,
                subject="User Login",
                body=user.email + " Just logged in."
            )
            new_activity.save()

            if user.first_login is True:
                user.first_login = False
                user.save()

        return Response(payload, status=status.HTTP_200_OK)




def check_password(email, password):
    try:
        user = User.objects.get(email=email)
        return user.check_password(password)
    except User.DoesNotExist:
        return False





@api_view(['POST', ])
@permission_classes([])
@authentication_classes([])
def susu_user_registration_view_LIGIT(request):
    payload = {}
    data = {}
    errors = {}
    email_errors = []
    password_errors = []
    full_name_errors = []
    phone_errors = []
    photo_errors = []

    url = 'https://dev.tuaneka.com/api/v1/login'

    email = request.data.get('email', '0').lower()
    full_name = request.data.get('full_name', '0')
    password = request.data.get('password', '0')
    password2 = request.data.get('password2', '0')
    phone = request.data.get('phone', '0')


    # CHECK PASSWORD FIRST
    if validate_password(password) == "Password is too weak. It should be at least 5 characters long.":
        password_errors.append('Password is too weak. It should be at least 5 characters long.')
        if password_errors:
            errors['password'] = password_errors
            payload['message'] = "Error"
            payload['errors'] = errors
            return Response(payload, status=status.HTTP_404_NOT_FOUND)


    susu_data = {
        'email': email,
        'password': password
    }

    json_data = json.dumps(susu_data)

    headers = {
        # 'Authorization': 'Bearer <your_access_token>',
        'Content-Type': 'application/json',
    }

    try:
        response = requests.post(url, data=json_data, headers=headers)
        if response.status_code == 200:
            if response.content:
                try:
                    # Decode the response content to a string
                    response_text = response.content.decode('utf-8')
                    # Deserialize the JSON content
                    response_json = json.loads(response_text)
                    print(response_json)  # Assumes the response is in JSON format

                    if not email:
                        email_errors.append('Email is required.')
                        if email_errors:
                            errors['email'] = email_errors
                            payload['message'] = "Error"
                            payload['errors'] = errors
                            return Response(payload, status=status.HTTP_404_NOT_FOUND)

                    qs = User.objects.filter(email=email)
                    if qs.exists():
                        email_errors.append('Email is already exists.')
                        if email_errors:
                            errors['email'] = email_errors
                            payload['message'] = "Error"
                            payload['errors'] = errors
                            return Response(payload, status=status.HTTP_404_NOT_FOUND)

                    if not full_name:
                        full_name_errors.append('Full name required.')
                        if full_name_errors:
                            errors['full_name'] = full_name_errors
                            payload['message'] = "Error"
                            payload['errors'] = errors
                            return Response(payload, status=status.HTTP_404_NOT_FOUND)

                    if not password:
                        password_errors.append('Password required.')
                        if password_errors:
                            errors['password'] = password_errors
                            payload['message'] = "Error"
                            payload['errors'] = errors
                            return Response(payload, status=status.HTTP_404_NOT_FOUND)

                    if password != password2:
                        password_errors.append('Password don\'t match.')
                        if password_errors:
                            errors['password'] = password_errors
                            payload['message'] = "Error"
                            payload['errors'] = errors
                            return Response(payload, status=status.HTTP_404_NOT_FOUND)



                    if not phone:
                        phone_errors.append('Phone number required.')
                        if phone_errors:
                            errors['phone'] = phone_errors
                            payload['message'] = "Error"
                            payload['errors'] = errors
                            return Response(payload, status=status.HTTP_404_NOT_FOUND)


                    serializer = SusuUserRegistrationSerializer(data=request.data)
                    if serializer.is_valid():
                        user = serializer.save()
                        data['email'] = user.email
                        data['full_name'] = user.full_name
                        personal_info = PersonalInfo.objects.create(
                            user=user,
                            phone=phone,
                        )
                        personal_info.save()
                        data['phone'] = personal_info.phone


                        wallet = Wallet.objects.create(
                            user=user,
                        )

                        token = Token.objects.get(user=user).key
                        data['token'] = token

                        email_token = generate_email_token()

                        user = User.objects.get(email=email)
                        user.email_token = email_token
                        user.save()

                        context = {
                            'email_token': email_token,
                            'email': user.email,
                            'full_name': user.full_name
                        }

                        txt_ = get_template("registration/emails/verify.txt").render(context)
                        html_ = get_template("registration/emails/verify.html").render(context)

                        subject = 'EMAIL CONFIRMATION CODE'
                        from_email = settings.DEFAULT_FROM_EMAIL
                        recipient_list = [user.email]

                        sent_mail = send_mail(
                            subject,
                            txt_,
                            from_email,
                            recipient_list,
                            html_message=html_,
                            fail_silently=False
                        )

                        new_activity = AllActivity.objects.create(
                            user=user,
                            subject="User Registration",
                            body=user.email + " Just created an account."
                        )
                        new_activity.save()




                except json.JSONDecodeError as e:

                    email_errors.append('Invalid Credentials in Tuaneka database.')
                    email_errors.append('Insert the correct Tuaneka credentials if you already have an account or click Create New Tuaneka User.')
                    if email_errors:
                        errors['email'] = email_errors
                        payload['message'] = "Error"
                        payload['errors'] = errors
                        return Response(payload, status=status.HTTP_404_NOT_FOUND)

                    print('Error decoding response JSON:', e)
            else:
                print('Response content is empty')
    except requests.HTTPError as err:
        if response.status_code == 404:
            print("4044444444444")
            print(err)


    payload['message'] = "Successful"
    payload['data'] = data

    return Response(payload, status=status.HTTP_200_OK)



@api_view(['POST', ])
@permission_classes([])
@authentication_classes([])
def susu_user_registration_tuaneka_view(request):
    payload = {}
    data = {}
    errors = {}
    email_errors = []
    password_errors = []
    full_name_errors = []
    phone_errors = []

    register_errors = []


    url = 'https://dev.tuaneka.com/api/v1/register'

    email = request.data.get('email', '0').lower()
    full_name = request.data.get('full_name', '0')
    password = request.data.get('password', '0')
    password2 = request.data.get('password2', '0')
    phone = request.data.get('phone', '0')


    # CHECK PASSWORD FIRST
    if validate_password(password) == "Password is too weak. It should be at least 5 characters long.":
        password_errors.append('Password is too weak. It should be at least 5 characters long.')
        if password_errors:
            errors['password'] = password_errors
            payload['message'] = "Error"
            payload['errors'] = errors
            return Response(payload, status=status.HTTP_404_NOT_FOUND)


    susu_data = {
        'name': full_name,
        'email': email,
        'password': password,
        'password_confirmation': password2,
        'phone': phone
    }

    json_data = json.dumps(susu_data)
    #print(json_data)

    headers = {
        # 'Authorization': 'Bearer <your_access_token>',
        'Content-Type': 'application/json',
    }

    try:
        response = requests.post(url, data=json_data, headers=headers)
        if response.status_code == 200:
            if response.content:
                try:
                    # Decode the response content to a string
                    response_text = response.content.decode('utf-8')
                    # Deserialize the JSON content
                    response_json = json.loads(response_text)
                    print(response_json)
                except json.JSONDecodeError as e:
                    register_errors.append('Error registering user in Tuaneka database. Try again. Make sure you dont already have an account in the Tuaneka database.')
                    if register_errors:
                        errors['register_errors'] = register_errors
                        payload['message'] = "Error"
                        payload['errors'] = errors

                    return Response(payload, status=status.HTTP_404_NOT_FOUND)

    except requests.HTTPError as err:
        if response.status_code == 404:
            print("4044444444444")
            print(err)


    payload['message'] = "Successful"
    payload['data'] = data

    return Response(payload, status=status.HTTP_200_OK)


def validate_password(password):
    if len(password) < 5:
        return "Password is too weak. It should be at least 5 characters long."

    # Check for at least one lowercase letter, one uppercase letter, and one digit
    if not re.search(r'[a-z]', password) or not re.search(r'[A-Z]', password) or not re.search(r'\d', password):
        return "Password is too weak. It should contain a mix of lowercase letters, uppercase letters, and numbers."

    # Evaluate password strength
    strength = 0
    if len(password) >= 8:
        strength += 1
    if re.search(r'[!@#$%^&*(),.?":{}|<>]', password):
        strength += 1
    if re.search(r'[A-Za-z0-9]*([A-Za-z][0-9]|[0-9][A-Za-z])[A-Za-z0-9]*', password):
        strength += 1

    if strength < 2:
        return "Password is weak. Try adding more complexity."
    elif strength < 3:
        return "Password is moderate in strength."
    else:
        return "Password is strong."




@api_view(['POST', ])
@permission_classes([])
@authentication_classes([])
def susu_user_registration_viewOLDD(request):

    payload = {}
    errors = []
    data = {}

    url = 'https://dev.tuaneka.com/api/v1/login'

    susu_data = {
        'email': 'devnaledi@gmail.co',
        'password': 'Ocho252Ocho_',
    }


    # Convert the data to JSON string
    json_data = json.dumps(susu_data)


    headers = {
         #'Authorization': 'Bearer <your_access_token>',
         'Content-Type': 'application/json',
    }

    response = requests.post(url, data=json_data, headers=headers)

    # Check if the request was successful (status code 200)
    if response.status_code == 200:
        # Check if the response content is not empty
        if response.content:
            try:
                # Decode the response content to a string
                response_text = response.content.decode('utf-8')
                # Deserialize the JSON content
                response_json = json.loads(response_text)
                print(response_json)  # Assumes the response is in JSON format
            except json.JSONDecodeError as e:
                print('Error decoding response JSON:', e)
        else:
            print('Response content is empty')
    # Check if the response has a status code of 422 Unprocessable Entity
    elif response.status_code == 422:
        # Print the response content as is, assuming it contains error data
        print('Error data:', response.content.decode('utf-8'))
    else:
        print('Request failed with status code:', response.status_code)



    if errors:
        payload['errors'] = errors
        return Response(payload, status=status.HTTP_404_NOT_FOUND)

    payload['message'] = "Successful"
    payload['data'] = data

    return Response(payload, status=status.HTTP_200_OK)



@api_view(['POST', ])
@permission_classes([])
@authentication_classes([])
def susu_user_registration_viewWORKING(email, full_name, password, password2, phone):

    request_data = {
      'email': email,
      'full_name': full_name,
      'password': password,
      'password2': password2,
      'phone': phone,
    }


    payload = {}
    data = {}
    errors = {}
    email_errors = []
    password_errors = []
    full_name_errors = []
    phone_errors = []

    # email = request.data.get('email', '0').lower()
    # full_name = request.data.get('full_name', '0')
    # password = request.data.get('password', '0')
    # password2 = request.data.get('password2', '0')
    # phone = request.data.get('phone', '0')


    if not email:
        email_errors.append('Email is required.')
        if email_errors:
            errors['email'] = email_errors
            payload['message'] = "Error"
            payload['errors'] = errors
            return Response(payload, status=status.HTTP_404_NOT_FOUND)

    qs = User.objects.filter(email=email)
    if qs.exists():
        email_errors.append('Email is already exists.')
        if email_errors:
            errors['email'] = email_errors
            payload['message'] = "Error"
            payload['errors'] = errors
            return Response(payload, status=status.HTTP_404_NOT_FOUND)


    if not full_name:
        full_name_errors.append('Full name required.')
        if full_name_errors:
            errors['full_name'] = full_name_errors
            payload['message'] = "Error"
            payload['errors'] = errors
            return Response(payload, status=status.HTTP_404_NOT_FOUND)

    if not password:
        password_errors.append('Password required.')
        if password_errors:
            errors['password'] = password_errors
            payload['message'] = "Error"
            payload['errors'] = errors
            return Response(payload, status=status.HTTP_404_NOT_FOUND)

    if password != password2:
        password_errors.append('Password don\'t match.')
        if password_errors:
            errors['password'] = password_errors
            payload['message'] = "Error"
            payload['errors'] = errors
            return Response(payload, status=status.HTTP_404_NOT_FOUND)


    if not phone:
        phone_errors.append('Phone number required.')
        if phone_errors:
            errors['phone'] = phone_errors
            payload['message'] = "Error"
            payload['errors'] = errors
            return Response(payload, status=status.HTTP_404_NOT_FOUND)

    serializer = SusuUserRegistrationSerializer(data=request_data)
    if serializer.is_valid():
        user = serializer.save()
        data['email'] = user.email
        data['full_name'] = user.full_name
        personal_info = PersonalInfo.objects.create(
            user=user,
            phone=phone,
        )
        personal_info.save()
        data['phone'] = personal_info.phone

        token = Token.objects.get(user=user).key
        data['token'] = token

        email_token = generate_email_token()

        user = User.objects.get(email=email)
        user.email_token = email_token
        user.save()

        context = {
            'email_token': email_token,
            'email': user.email,
            'full_name': user.full_name
        }

        txt_ = get_template("registration/emails/verify.txt").render(context)
        html_ = get_template("registration/emails/verify.html").render(context)

        subject = 'EMAIL CONFIRMATION CODE'
        from_email = settings.DEFAULT_FROM_EMAIL
        recipient_list = [user.email]

        sent_mail = send_mail(
            subject,
            txt_,
            from_email,
            recipient_list,
            html_message=html_,
            fail_silently=False
        )

        new_activity = AllActivity.objects.create(
            user=user,
            subject="User Registration",
            verb=user.email + " Just created an account."
        )
        new_activity.save()

        payload['message'] = "Successful"
        payload['data'] = data

    return Response(payload, status=status.HTTP_200_OK)


@api_view(['POST', ])
@permission_classes([])
@authentication_classes([])
def verify_susu_user_email(request):
    payload = {}
    data = {}
    errors = {}
    email_errors = []
    token_errors = []
    password_errors = []

    email = request.data.get('email', '0').lower()
    email_token = request.data.get('email_token', '0')

    if not email:
        email_errors.append('Email is required.')
    if email_errors:
        errors['email'] = email_errors
        payload['message'] = "Error"
        payload['errors'] = errors
        return Response(payload, status=status.HTTP_404_NOT_FOUND)

    qs = User.objects.filter(email=email)
    if not qs.exists():
        email_errors.append('Email does not exist.')
        if email_errors:
            errors['email'] = email_errors
            payload['message'] = "Error"
            payload['errors'] = errors
            return Response(payload, status=status.HTTP_404_NOT_FOUND)

    if not email_token:
        token_errors.append('Token is required.')
        if token_errors:
            errors['token'] = token_errors
            payload['message'] = "Error"
            payload['errors'] = errors
            return Response(payload, status=status.HTTP_404_NOT_FOUND)

    user = User.objects.get(email=email)
    if email_token != user.email_token:
        token_errors.append('Invalid Token.')
        if token_errors:
            errors['token'] = token_errors
            payload['message'] = "Error"
            payload['errors'] = errors
            return Response(payload, status=status.HTTP_404_NOT_FOUND)

    try:
        user_personal_info = PersonalInfo.objects.get(user=user)
    except PersonalInfo.DoesNotExist:
        user_personal_info = PersonalInfo.objects.create(user=user)

    try:
        token = Token.objects.get(user=user)
    except Token.DoesNotExist:
        token = Token.objects.create(user=user)

    user.is_active = True
    user.email_verified = True
    user.save()


    data["user_id"] = user.user_id
    data["email"] = user.email
    data["full_name"] = user.full_name
    data["token"] = token.key

    payload['message'] = "Successful"
    payload['data'] = data

    new_activity = AllActivity.objects.create(
        user=user,
        subject="Verify Email",
        body=user.email + " just verified their email",
    )
    new_activity.save()

    return Response(payload, status=status.HTTP_200_OK)



class PasswordResetView(generics.GenericAPIView):
    serializer_class = PasswordResetSerializer



    def post(self, request, *args, **kwargs):
        payload = {}
        data = {}
        errors = {}
        email_errors = []

        email = request.data.get('email', '0').lower()

        if not email:
            email_errors.append('Email is required.')
        if email_errors:
            errors['email'] = email_errors
            payload['message'] = "Error"
            payload['errors'] = errors
            return Response(payload, status=status.HTTP_404_NOT_FOUND)

        qs = User.objects.filter(email=email)
        if not qs.exists():
            email_errors.append('Email does not exist.')
            if email_errors:
                errors['email'] = email_errors
                payload['message'] = "Error"
                payload['errors'] = errors
                return Response(payload, status=status.HTTP_404_NOT_FOUND)


        user = User.objects.filter(email=email).first()
        otp_code = generate_random_otp_code()
        user.otp_code = otp_code
        user.save()

        context = {
            'otp_code': otp_code,
            'email': user.email,
            'full_name': user.full_name
        }

        txt_ = get_template("registration/emails/send_otp.txt").render(context)
        html_ = get_template("registration/emails/send_otp.html").render(context)

        subject = 'OTP CODE'
        from_email = settings.DEFAULT_FROM_EMAIL
        recipient_list = [user.email]

        sent_mail = send_mail(
            subject,
            txt_,
            from_email,
            recipient_list,
            html_message=html_,
            fail_silently=False
        )
        data["otp_code"] = otp_code
        data["emai"] = user.email
        data["user_id"] = user.user_id

        new_activity = AllActivity.objects.create(
            user=user,
            subject="Reset Password",
            body="OTP sent to " + user.email,
        )
        new_activity.save()

        payload['message'] = "Successful"
        payload['data'] = data

        return Response(payload, status=status.HTTP_200_OK)



# Confirm OTP


@api_view(['POST', ])
@permission_classes([])
@authentication_classes([])
def confirm_otp_view(request):
    payload = {}
    data = {}
    errors = {}
    email_errors = []
    otp_errors = []

    email = request.data.get('email', '0')
    otp_code = request.data.get('otp_code', '0')

    if not email:
        email_errors.append('Email is required.')
    if email_errors:
        errors['email'] = email_errors
        payload['message'] = "Error"
        payload['errors'] = errors
        return Response(payload, status=status.HTTP_404_NOT_FOUND)

    if not otp_code:
        otp_errors.append('OTP code is required.')
    if otp_errors:
        errors['otp_code'] = otp_errors
        payload['message'] = "Error"
        payload['errors'] = errors
        return Response(payload, status=status.HTTP_404_NOT_FOUND)

    user = User.objects.filter(email=email).first()

    if user is None:
        email_errors.append('Email does not exist.')
    if email_errors:
        errors['email'] = email_errors
        payload['message'] = "Error"
        payload['errors'] = errors
        return Response(payload, status=status.HTTP_404_NOT_FOUND)


    client_otp = user.otp_code

    if client_otp != otp_code:
        otp_errors.append('Invalid Code.')
    if otp_errors:
        errors['otp_code'] = otp_errors
        payload['message'] = "Error"
        payload['errors'] = errors
        return Response(payload, status=status.HTTP_404_NOT_FOUND)



    data['email'] = user.email
    data['user_id'] = user.user_id

    payload['message'] = "Successful"
    payload['data'] = data
    return Response(payload, status=status.HTTP_200_OK)



@api_view(['POST', ])
@permission_classes([AllowAny])
@authentication_classes([])
def new_password_reset_view(request):
    payload = {}
    data = {}
    errors = {}
    email_errors = []
    password_errors = []

    email = request.data.get('email', '0')
    new_password = request.data.get('new_password')
    new_password2 = request.data.get('new_password2')



    if not email:
        email_errors.append('Email is required.')
        if email_errors:
            errors['email'] = email_errors
            payload['message'] = "Error"
            payload['errors'] = errors
            return Response(payload, status=status.HTTP_404_NOT_FOUND)

    qs = User.objects.filter(email=email)
    if not qs.exists():
        email_errors.append('Email does not exists.')
        if email_errors:
            errors['email'] = email_errors
            payload['message'] = "Error"
            payload['errors'] = errors
            return Response(payload, status=status.HTTP_404_NOT_FOUND)


    if not new_password:
        password_errors.append('Password required.')
        if password_errors:
            errors['password'] = password_errors
            payload['message'] = "Error"
            payload['errors'] = errors
            return Response(payload, status=status.HTTP_404_NOT_FOUND)


    if new_password != new_password2:
        password_errors.append('Password don\'t match.')
        if password_errors:
            errors['password'] = password_errors
            payload['message'] = "Error"
            payload['errors'] = errors
            return Response(payload, status=status.HTTP_404_NOT_FOUND)

    user = User.objects.filter(email=email).first()
    user.set_password(new_password)
    user.save()

    data['email'] = user.email
    data['user_id'] = user.user_id


    payload['message'] = "Successful, Password reset successfully."
    payload['data'] = data

    return Response(payload, status=status.HTTP_200_OK)


@api_view(['POST', ])
@permission_classes([AllowAny])
@authentication_classes([])
def resend_email_verification(request):
    payload = {}
    data = {}
    errors = {}
    email_errors = []


    email = request.data.get('email', '0')

    if not email:
        email_errors.append('Email is required.')
    if email_errors:
        errors['email'] = email_errors
        payload['message'] = "Error"
        payload['errors'] = errors
        return Response(payload, status=status.HTTP_404_NOT_FOUND)

    qs = User.objects.filter(email=email)
    if not qs.exists():
        email_errors.append('Email does not exist.')
        if email_errors:
            errors['email'] = email_errors
            payload['message'] = "Error"
            payload['errors'] = errors
            return Response(payload, status=status.HTTP_404_NOT_FOUND)

    user = User.objects.filter(email=email).first()
    otp_code = generate_random_otp_code()
    user.otp_code = otp_code
    user.save()

    context = {
        'otp_code': otp_code,
        'email': user.email,
        'full_name': user.full_name
    }

    txt_ = get_template("registration/emails/send_otp.txt").render(context)
    html_ = get_template("registration/emails/send_otp.html").render(context)

    subject = 'OTP CODE'
    from_email = settings.DEFAULT_FROM_EMAIL
    recipient_list = [user.email]

    sent_mail = send_mail(
        subject,
        txt_,
        from_email,
        recipient_list,
        html_message=html_,
        fail_silently=False
    )
    data["otp_code"] = otp_code
    data["emai"] = user.email
    data["user_id"] = user.user_id

    new_activity = AllActivity.objects.create(
        user=user,
        subject="Email verification sent",
        body="Email verification sent to " + user.email,
    )
    new_activity.save()

    payload['message'] = "Successful"
    payload['data'] = data

    return Response(payload, status=status.HTTP_200_OK)










