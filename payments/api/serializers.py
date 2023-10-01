from rest_framework import serializers

from payments.models import Payment
from susu_groups.models import PaymentSchedule


class ListPaymentScheduleSerializer(serializers.ModelSerializer):
    created_at = serializers.SerializerMethodField()

    def get_created_at(self, obj):
        return obj.created_at.strftime("%d-%m-%y")

    class Meta:
        model = PaymentSchedule
        fields = [
            'amount',
            'status',
            'payment_for',
            'due_date',
            'created_at'
        ]



class ListPaymentSerializer(serializers.ModelSerializer):
    created_at = serializers.SerializerMethodField()

    def get_created_at(self, obj):
        return obj.created_at.strftime("%d-%m-%y")

    class Meta:
        model = Payment
        fields = [
            'amount',
            'payment_method',
            'payment_type',
            'notes',
            'refund',
            'created_at'
        ]