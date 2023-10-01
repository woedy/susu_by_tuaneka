from django.contrib.auth import get_user_model
from django.db import models
from django.db.models.signals import pre_save

from mysite.utils import unique_group_id_generator

User = get_user_model()

PAYMENT_OPTIONS_CHOICES = (
    ('Mobile Wallet', 'Mobile Wallet'),
    ('Bank Transfer', 'Bank Transfer'),
    ('Payangel Wallet', 'Payangel Wallet'),

)

VACANT = 'vacant'
OCCUPIED = 'occupied'
STATE_CHOICES = [
    (VACANT, 'Vacant'),
    (OCCUPIED, 'Occupied')
]


class Payout(models.Model):
    susu_user = models.ForeignKey('SusuGroupUser', on_delete=models.CASCADE, null=True, blank=True)
    group = models.ForeignKey('SusuGroup', on_delete=models.CASCADE)
    amount = models.CharField(max_length=100, blank=True, null=True)

    rotation_number = models.IntegerField(default=1, blank=True, null=True)
    cycle_number = models.IntegerField(default=0, blank=True, null=True)

    active = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)


class Contribution(models.Model):
    susu_user = models.ForeignKey('SusuGroupUser', on_delete=models.CASCADE, null=True, blank=True)
    group = models.ForeignKey('SusuGroup', on_delete=models.CASCADE)
    amount = models.CharField(max_length=100, blank=True, null=True)

    rotation_number = models.IntegerField(default=1, blank=True, null=True)
    cycle_number = models.IntegerField(default=0, blank=True, null=True)

    active = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)


class SusuPosition(models.Model):
    position = models.IntegerField()
    state = models.CharField(choices=STATE_CHOICES, max_length=10)
    susu_user = models.ForeignKey('SusuGroupUser', on_delete=models.CASCADE, null=True, blank=True)

    rotation_number = models.IntegerField(default=1, blank=True, null=True)
    cycle_number = models.IntegerField(default=0, blank=True, null=True)

    group = models.ForeignKey('SusuGroup', on_delete=models.CASCADE)


class SusuGroupUserReminders(models.Model):
    susu_user = models.ForeignKey('SusuGroupUser', on_delete=models.CASCADE, null=True, blank=True)
    send_reminder_on = models.DateTimeField(null=True, blank=True)
    reminder_sent = models.BooleanField(default=False)

    rotation_number = models.IntegerField(default=1, blank=True, null=True)
    cycle_number = models.IntegerField(default=0, blank=True, null=True)

    subject = models.CharField(max_length=100, blank=True, null=True)
    body = models.TextField(blank=True, null=True)


class SusuGroupUser(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='susu_group_user')

    group_id = models.CharField(max_length=120, unique=True, blank=True, null=True)


    payment_option = models.CharField(max_length=100, choices=PAYMENT_OPTIONS_CHOICES, blank=True, null=True)
    payment_number = models.CharField(max_length=100, blank=True, null=True)

    is_turn = models.BooleanField(default=False)

    paid = models.BooleanField(default=False)
    paid_amount = models.CharField(max_length=100, blank=True, null=True)
    paid_on = models.DateTimeField(null=True, blank=True)
    momo_reference = models.CharField(max_length=100, blank=True, null=True)
    confirm_payment = models.BooleanField(default=False)

    received = models.BooleanField(default=False)
    receiving_amount = models.CharField(max_length=100, blank=True, null=True)
    receiving_date = models.DateTimeField(null=True, blank=True)

    rotation_number = models.IntegerField(default=1, blank=True, null=True)
    cycle_number = models.IntegerField(default=0, blank=True, null=True)

    active = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)


PAYMENT_CYCLE_CHOICES = (
    ('Weekly', 'Weekly'),
    ('Monthly', 'Monthly'),
    ('Yearly', 'Yearly'),

)

GROUP_TYPE_CHOICES = (
    ('Private', 'Private'),
    ('Public', 'Public'),

)


class InvitedMember(models.Model):
    email = models.CharField(max_length=120, blank=True, null=True)
    group = models.ForeignKey('SusuGroup', on_delete=models.CASCADE)
    invitation_sent = models.BooleanField(default=False)
    invitation_accepted = models.BooleanField(default=False)


class SusuGroup(models.Model):
    group_id = models.CharField(max_length=120, unique=True, blank=True, null=True)
    group_name = models.CharField(max_length=120, blank=True, null=True)
    capacity = models.CharField(max_length=120, blank=True, null=True)
    number_of_people = models.IntegerField(default=0, blank=True, null=True)
    slots_left = models.IntegerField(default=0, blank=True, null=True)
    group_description = models.TextField(blank=True, null=True)
    payment_cycle = models.CharField(max_length=100, choices=PAYMENT_CYCLE_CHOICES, blank=True, null=True)

    rotation_number = models.IntegerField(default=1, blank=True, null=True)
    cycle_number = models.IntegerField(default=1, blank=True, null=True)
    cycle_started = models.BooleanField(default=False)

    group_type = models.CharField(max_length=100, choices=GROUP_TYPE_CHOICES, blank=True, null=True)
    group_code = models.CharField(max_length=100, blank=True, null=True)
    target_amount = models.IntegerField(default=0, blank=True, null=True)
    susu_group_users = models.ManyToManyField(SusuGroupUser, blank=True, related_name="susu_group_users")
    start_date = models.DateField(null=True, blank=True)

    days_left = models.IntegerField(default=0, blank=True, null=True)
    group_creator = models.ForeignKey(User, on_delete=models.CASCADE, related_name='group_creator')

    active = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)


def pre_save_group_id_receiver(sender, instance, *args, **kwargs):
    if not instance.group_id:
        instance.group_id = unique_group_id_generator(instance)


pre_save.connect(pre_save_group_id_receiver, sender=SusuGroup)

PAY_SCHEDULE_CHOICES = (
    ('PAY NOW', 'PAY NOW'),
    ('PAID', 'PAID'),
    ('CONFIRM PAID', 'CONFIRM PAID'),
    ('RECEIVE', 'RECEIVE'),

)


class PaymentSchedule(models.Model):
    group_user = models.ForeignKey(SusuGroupUser, on_delete=models.CASCADE, related_name='user_pay_schedule')
    user_susu_group = models.ForeignKey(SusuGroup, on_delete=models.SET_NULL, null=True,
                                        related_name='pay_schedule_susu_group')
    status = models.CharField(default="PAY NOW", max_length=100, choices=PAY_SCHEDULE_CHOICES, blank=True, null=True)
    due_date = models.DateTimeField(null=True, blank=True)
    payment_for = models.CharField(max_length=120, blank=True, null=True)
    amount = models.CharField(max_length=120, blank=True, null=True)
    days_left = models.IntegerField(default=0, blank=True, null=True)

    rotation_number = models.IntegerField(default=1, blank=True, null=True)
    cycle_number = models.IntegerField(default=0, blank=True, null=True)

    active = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)


