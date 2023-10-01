from django.urls import path

from payments.api.views import my_payments_view, my_payment_schedule_view

app_name = 'payments'

urlpatterns = [
    path('my-payments', my_payments_view, name="my_payments_view"),
    path('my-payment-schedules', my_payment_schedule_view, name="my_payment_schedule_view"),
]
