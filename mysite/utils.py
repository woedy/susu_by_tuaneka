import base64
import random
import string

from django.core.files.base import ContentFile
from django.core.mail import EmailMessage

from django.utils.text import slugify

def random_string_generator(size=10, chars=string.ascii_lowercase + string.digits):
    return ''.join(random.choice(chars) for _ in range(size))


def generate_random_otp_code():
    code = ''
    for i in range(4):
        code += str(random.randint(0, 9))
    return code



def generate_email_token():
    code = ''
    for i in range(7):
        code += str(random.randint(0, 9))
    return code


def unique_user_id_generator(instance):
    """
    This is for a django project with a user_id field
    """
    size = random.randint(30, 45)
    user_id = random_string_generator(size=size)

    Klass = instance.__class__
    qs_exists = Klass.objects.filter(user_id=user_id).exists()
    if qs_exists:
        return
    return user_id


def unique_group_id_generator(instance):
    """
    This is for a django project with a group_id field
    """
    size = random.randint(20, 25)
    group_id = random_string_generator(size=size)

    Klass = instance.__class__
    qs_exists = Klass.objects.filter(group_id=group_id).exists()
    if qs_exists:
        return
    return group_id


def generate_private_group_code():

    code = ''
    for i in range(5):
        code += str(random.randint(0, 9))
    return code


def unique_key_generator(instance):
    """
    This is for a Django project with an key field
    """
    size = random.randint(30, 45)
    key = random_string_generator(size=size)

    Klass = instance.__class__
    qs_exists = Klass.objects.filter(key=key).exists()
    if qs_exists:
        return unique_slug_generator(instance)
    return key


def unique_slug_generator(instance, new_slug=None):
    """
    This is for a Django project and it assumes your instance
    has a model with a slug field and a title character (char) field.
    """
    if new_slug is not None:
        slug = new_slug
    else:
        slug = slugify(instance.name)

    Klass = instance.__class__
    qs_exists = Klass.objects.filter(slug=slug).exists()
    if qs_exists:
        new_slug = "{slug}-{randstr}".format(
                    slug=slug,
                    randstr=random_string_generator(size=4)
                )
        return unique_slug_generator(instance, new_slug=new_slug)
    return slug




def convert_size(size):
    s_size = 512000
    if size < s_size:
        n_size = round(size / 1000, 2)
        ext = ' kb'
    elif size < s_size * 1000:
        n_size = round(size / 1000000, 2)
        ext = ' Mb'
    else:
        n_size = round(size / 1000000000, 2)
        ext = ' Gb'
    return str(n_size) + ext


import threading


class EmailThread(threading.Thread):

    def __init__(self, email):
        self.email = email
        threading.Thread.__init__(self)

    def run(self):
        self.email.send()

class Util:
    @staticmethod
    def send_email(data):
        email = EmailMessage(
            subject=data['email_subject'], body=data['email_body'], to=[data['to_email']])
        EmailThread(email).start()


def base64_file(data, name="File_name", ext=".jpg"):
    print("############## DAAATAAAAAA")
    file = ContentFile(base64.b64decode(data), name=name + ext)

    return file

























