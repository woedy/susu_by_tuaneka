
from django.contrib.auth import get_user_model
from django.utils.datetime_safe import date
from rest_framework import serializers

from susu_groups.models import SusuGroup, SusuGroupUser, PaymentSchedule

User = get_user_model()



class HomeSusuGroupUserSerializer(serializers.ModelSerializer):
    class Meta:
        model = SusuGroupUser
        fields = [
            'position',
            'is_turn',
            'paid',
            'received',
            'receiving_date',
        ]


class HomeSusuGroupSerializer(serializers.ModelSerializer):
    start_date = serializers.SerializerMethodField()
    days_left = serializers.SerializerMethodField()
    slots_left = serializers.SerializerMethodField()

    def get_start_date(self, obj):
        return obj.start_date.strftime("%d-%m-%y")

    def get_days_left(self, obj):
        today = date.today()
        start_date = obj.start_date  # Convert datetime to date
        delta = start_date - today
        return delta.days

    def get_slots_left(self, obj):
        capacity = int(obj.capacity)
        number_of_people = int(obj.number_of_people)
        slots_left = capacity - number_of_people
        return slots_left

    class Meta:
        model = SusuGroup
        fields = [
            'group_id',
            'group_name',
            'days_left',
            'start_date',
            'capacity',
            'number_of_people',
            'slots_left',
            'target_amount',
        ]

class PayScheduleHomeSusuGroupSerializer(serializers.ModelSerializer):

    #susu_group_users = HomeSusuGroupUserSerializer(many=True)

    class Meta:
        model = SusuGroup
        fields = [
            'group_name',
        ]


class HomePaymentScheduleSerializer(serializers.ModelSerializer):
    user_susu_group = PayScheduleHomeSusuGroupSerializer(many=False)
    due_date = serializers.SerializerMethodField()

    def get_due_date(self, obj):
        return obj.due_date.strftime("%d-%m-%y")


    class Meta:
        model = PaymentSchedule
        fields = [
            'status',
            'payment_for',
            'user_susu_group',
            'due_date',
        ]
