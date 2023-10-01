from django.urls import path

from accounts.api.views.susu_user_views import SusuUserLogin, susu_user_registration_view, confirm_otp_view, \
    PasswordResetView, new_password_reset_view, verify_susu_user_email, resend_email_verification, \
    susu_user_registration_tuaneka_view, register_update_profile_view

app_name = 'accounts'

urlpatterns = [
    # CLIENT URLS
    path('login-susu-user', SusuUserLogin.as_view(), name="login_susu_user"),
    path('register-susu-user', susu_user_registration_view, name="register_susu_user"),
    path('register-update-user-profile', register_update_profile_view, name="register_update_profile_view"),
    path('register-susu-user-tuaneka', susu_user_registration_tuaneka_view, name="register_susu_user_tuaneka"),
    path('verify-susu-user-email', verify_susu_user_email, name="verify_susu_user_email"),
    path('forgot-user-password', PasswordResetView.as_view(), name="forgot_password"),
    path('confirm-otp', confirm_otp_view, name="confirm_otp_view"),
    path('resend-email-verification', resend_email_verification, name="resend_email_verification"),
    path('new-password-reset-view', new_password_reset_view, name="new_password_reset_view"),
    #path('create-new-password', PasswordChangeView.as_view(), name="create_new_password_view"),

    #path('logout-user', logout_user, name="logout_user"),

]
