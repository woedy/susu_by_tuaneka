"""
Django settings for mysite project.

Generated by 'django-admin startproject' using Django 4.2.

For more information on this file, see
https://docs.djangoproject.com/en/4.2/topics/settings/

For the full list of settings and their values, see
https://docs.djangoproject.com/en/4.2/ref/settings/
"""
import os
from pathlib import Path

# Build paths inside the project like this: BASE_DIR / 'subdir'.
BASE_DIR = Path(__file__).resolve().parent.parent


# Quick-start development settings - unsuitable for production
# See https://docs.djangoproject.com/en/4.2/howto/deployment/checklist/

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = "django-insecure-yqtg!ao!*dcu9rlw8%aei49(j)=9$=fe@+=fb!6$mgkvd489j9"

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = True

ALLOWED_HOSTS = ["*"]

EMAIL_BACKEND = 'django.core.mail.backends.smtp.EmailBackend'
EMAIL_HOST = 'box.teamalfy.co.uk'
EMAIL_PORT = 465
EMAIL_USE_SSL = True
EMAIL_HOST_USER = 'no-reply@teamalfy.co.uk'
EMAIL_HOST_PASSWORD = 'gYgG2GwiJq'
DEFAULT_FROM_EMAIL = 'no-reply@teamalfy.co.uk'


BASE_URL = '0.0.0.0:80'


# MAIL_HOST="box.teamalfy.co.uk"
# MAIL_PORT=465
# MAIL_USERNAME="no-reply@teamalfy.co.uk"
# MAIL_PASSWORD="gYgG2GwiJq"
# MAIL_ENCRYPTION="tls"
# MAIL_FROM_ADDRESS="no-reply@teamalfy.co.uk"


AUTH_USER_MODEL = 'accounts.User'


# Application definition

INSTALLED_APPS = [
    "channels",
    "django.contrib.admin",
    "django.contrib.auth",
    "django.contrib.contenttypes",
    "django.contrib.sessions",
    "django.contrib.messages",
    "django.contrib.staticfiles",
    'rest_framework',
    'rest_framework.authtoken',

    "accounts",
    "user_profile",
    "susu_groups",
    "payments",
    "notifications",
    "all_activities",
    "home_page"
]

MIDDLEWARE = [
    "django.middleware.security.SecurityMiddleware",
    "django.contrib.sessions.middleware.SessionMiddleware",
    "django.middleware.common.CommonMiddleware",
    "django.middleware.csrf.CsrfViewMiddleware",
    "django.contrib.auth.middleware.AuthenticationMiddleware",
    "django.contrib.messages.middleware.MessageMiddleware",
    "django.middleware.clickjacking.XFrameOptionsMiddleware",
]

ROOT_URLCONF = "mysite.urls"

ASGI_APPLICATION = "mysite.asgi.application"

CHANNEL_LAYERS = {
    "default": {
        "BACKEND": "channels_redis.core.RedisChannelLayer",
        "CONFIG": {
            "hosts": [("redis://redis:6379")],
        },
    },
}



TEMPLATES = [
    {
        "BACKEND": "django.template.backends.django.DjangoTemplates",
        "DIRS": [os.path.join(BASE_DIR, 'templates')],

        "APP_DIRS": True,
        "OPTIONS": {
            "context_processors": [
                "django.template.context_processors.debug",
                "django.template.context_processors.request",
                "django.contrib.auth.context_processors.auth",
                "django.contrib.messages.context_processors.messages",
            ],
        },
    },
]

WSGI_APPLICATION = "mysite.wsgi.application"


# Database
# https://docs.djangoproject.com/en/4.2/ref/settings/#databases

DATABASES = {
    "default": {
        "ENGINE": "django.db.backends.sqlite3",
        "NAME": BASE_DIR / "db.sqlite3",
    }
}


# DATABASES = {
#     'default': {
#         'ENGINE': 'django.db.backends.postgresql',
#         'NAME': 'postgres',
#         'USER': 'postgres',
#         'PASSWORD': 'postgres',
#         'HOST': 'db',
#         'PORT': 5432,
#     }
# }


CELERY_BROKER_URL = "redis://redis:6379"
CELERY_RESULT_BACKEND = "redis://redis:6379"

# Password validation
# https://docs.djangoproject.com/en/4.2/ref/settings/#auth-password-validators

AUTH_PASSWORD_VALIDATORS = [
    {
        "NAME": "django.contrib.auth.password_validation.UserAttributeSimilarityValidator",
    },
    {
        "NAME": "django.contrib.auth.password_validation.MinimumLengthValidator",
    },
    {
        "NAME": "django.contrib.auth.password_validation.CommonPasswordValidator",
    },
    {
        "NAME": "django.contrib.auth.password_validation.NumericPasswordValidator",
    },
]


# Internationalization
# https://docs.djangoproject.com/en/4.2/topics/i18n/

LANGUAGE_CODE = "en-us"

TIME_ZONE = "UTC"

USE_I18N = True

USE_TZ = True


# Static files (CSS, JavaScript, Images)
# https://docs.djangoproject.com/en/4.2/howto/static-files/

STATIC_URL = "static/"

STATICFILES_DIRS = [
    os.path.join(BASE_DIR, "static_my_proj")
]

STATIC_ROOT = os.path.join(BASE_DIR, "static_cdn", "static_root")

MEDIA_URL = '/media/'
MEDIA_ROOT = os.path.join(BASE_DIR, "static_cdn", 'media_root')


HOST_SCHEME = "http://"

# Default primary key field type
# https://docs.djangoproject.com/en/4.2/ref/settings/#default-auto-field

DEFAULT_AUTO_FIELD = "django.db.models.BigAutoField"


FCM_SERVER_KEY = 'AAAAxOQuav4:APA91bGO5BfxGqVOvfop7ZyrFW1RePVALmhotBv4VMk67KD_IP_9aJfLnBVYQmoJpJw3ho2sKBELLcnMRFhHRl-Ri312kySP7eOLcYJgI0XmyrNZ9CR9fu28bnZn7u5W53dV8Q-4W6oU'

