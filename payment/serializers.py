from rest_framework import serializers
from .models import SavedPayment, Order

class SavedPaymentSerializer(serializers.ModelSerializer):
    class Meta:
        model = SavedPayment
        fields = '__all__'

class PaymentSerializer(serializers.ModelSerializer):
    class Meta:
        model = Order
        fields = '__all__'