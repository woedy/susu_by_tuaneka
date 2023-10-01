from django.urls import path

from home_page.api.views.views import susu_user_home

app_name = 'home_page'

urlpatterns = [
    # CLIENT URLS
    path('susu-user-home', susu_user_home, name="susu_user_home"),

]
