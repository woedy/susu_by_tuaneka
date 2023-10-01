from django.urls import path

from user_profile.api.views import get_user_profile_view, update_user_profile_view

app_name = 'user_profile'

urlpatterns = [
    path('display-user-profile', get_user_profile_view, name="get_user_profile_view"),
    path('update-user-profile', update_user_profile_view, name="update_user_profile_view"),
]
