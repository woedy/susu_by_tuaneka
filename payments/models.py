from django.contrib.auth import get_user_model
from django.db import models

from susu_groups.models import SusuGroup

User = get_user_model()

class PaymentManager():
    pass

PAYMENT_METHOD_CHOICES = (
    ('Credit/Debit cards', 'Credit/Debit cards'),
    ('Apple Pay', 'Apple Pay'),
    ('Bank Transfer', 'Bank Transfer'),
    ('Mobile Money', 'Mobile Money'),

)


PAYMENT_TYPE_CHOICES = (
    ('Payout', 'Payout'),
    ('Contribution', 'Contribution'),

)

class Payment(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='user_payments')
    amount = models.DecimalField(default=0, max_digits=30, decimal_places=2, null=True, blank=True)
    virtual_account_number = models.CharField(max_length=255, null=True, blank=True)
    notes = models.TextField(null=True, blank=True)

    rotation_number = models.IntegerField(default=1, blank=True, null=True)
    cycle_number = models.IntegerField(default=0, blank=True, null=True)

    group = models.ForeignKey(SusuGroup, on_delete=models.SET_NULL, null=True)
    payment_method = models.CharField(max_length=100, choices=PAYMENT_METHOD_CHOICES, blank=True, null=True)
    payment_type = models.CharField(max_length=100, choices=PAYMENT_TYPE_CHOICES, blank=True, null=True)
    payment_for = models.CharField(max_length=120, blank=True, null=True)

    refund = models.BooleanField(default=False)

    active = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    objects = PaymentManager()


class Bank(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='user_banks')
    bank_name = models.CharField(max_length=255, null=True, blank=True)
    bank_branch = models.CharField(max_length=255, null=True, blank=True)
    account_holder_name = models.CharField(max_length=255, null=True, blank=True)

    active = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)



