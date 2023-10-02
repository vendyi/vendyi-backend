from rest_framework import serializers
from .models import SavedPayment

class SavedPaymentSerializer(serializers.ModelSerializer):
    class Meta:
        model = SavedPayment
        fields = '__all__'
