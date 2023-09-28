from rest_framework import serializers
from .models import CartItem

class CartItemSerializer(serializers.ModelSerializer):
    color = serializers.CharField(required=False)
    size = serializers.CharField(required=False)
    class Meta:
        model = CartItem
        fields = ['product', 'quantity', 'color', 'size']
