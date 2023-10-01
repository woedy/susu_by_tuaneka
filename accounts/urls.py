from django.urls import path, include, re_path

from accounts.views import AccountEmailActivateView

app_name = "accounts"

urlpatterns = [




    #path("account_activation_done/", account_activation_done_page, name="account_activation_done"),

    re_path(r'^email/confirm/(?P<key>[0-9A-Za-z]+)/$',
        AccountEmailActivateView.as_view(),
        name='email-activate'),
    re_path(r'^email/resend-activation/$',
        AccountEmailActivateView.as_view(),
        name='resend-activation'),

]
