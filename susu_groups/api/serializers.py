from django.contrib.auth import get_user_model
from django.utils.datetime_safe import date
from rest_framework import serializers

from susu_groups.models import SusuGroup, SusuGroupUser, PaymentSchedule
from user_profile.models import PersonalInfo

User = get_user_model()


class PaymentScheduleSerializer(serializers.ModelSerializer):
    due_date = serializers.SerializerMethodField()
    days_left = serializers.SerializerMethodField()

    def get_days_left(self, obj):
        today = date.today()
        due_date = obj.due_date.date()  # Convert datetime to date
        delta = due_date - today
        return delta.days

    def get_due_date(self, obj):
        return obj.due_date.strftime("%d-%m-%y")

    class Meta:
        model = PaymentSchedule
        fields = [
            'status',
            'due_date',
            'payment_for',
            'amount',
            'days_left',
        ]


class SusuPersonalSerializer(serializers.ModelSerializer):

    class Meta:
        model = PersonalInfo
        fields = [
            'photo',

        ]
class SusuUserSerializer(serializers.ModelSerializer):
    personal_info = SusuPersonalSerializer(many=False)

    class Meta:
        model = User
        fields = [
            'email',
            'full_name',
            'personal_info'
        ]
class SusuGroupUserSerializer(serializers.ModelSerializer):
    user = SusuUserSerializer(many=False)

    class Meta:
        model = SusuGroupUser
        fields = [
            'is_turn',
            'paid',
            'received',
            'receiving_date',
            'user'
        ]

class DetailSusuGroupSerializer(serializers.ModelSerializer):

    susu_group_users = SusuGroupUserSerializer(many=True)

    start_date = serializers.SerializerMethodField()
    days_left = serializers.SerializerMethodField()
    slots_left = serializers.SerializerMethodField()

    def get_start_date(self, obj):
        return obj.start_date.strftime("%d-%m-%y")

    def get_days_left(self, obj):
        today = date.today()
        start_date = obj.start_date # Convert datetime to date
        delta = start_date - today
        return delta.days

    def get_slots_left(self, obj):
        capacity = int(obj.capacity)
        number_of_people = int(obj.number_of_people)
        slots_left = capacity - number_of_people
        return slots_left


    group_creator = SusuUserSerializer(many=False)


    class Meta:
        model = SusuGroup
        fields = [
            'group_id',
            'group_name',
            'group_code',
            'group_code',
            'capacity',
            'number_of_people',
            'slots_left',
            'group_description',
            'payment_cycle',
            'group_type',
            'target_amount',
            'susu_group_users',
            'start_date',
            'days_left',
            'group_creator',
        ]



class ListSusuGroupSerializer(serializers.ModelSerializer):
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





