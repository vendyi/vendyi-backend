from rest_framework import serializers
from .models import CartItem
from vendors.models import Promo_Code

class CartItemSerializer(serializers.ModelSerializer):
    color = serializers.CharField(required=False)
    size = serializers.CharField(required=False)
    class Meta:
        model = CartItem
        fields = ['product', 'quantity', 'color', 'size']

class PromoCodeApplySerializer(serializers.Serializer):
    promo_code = serializers.CharField(max_length=255)

    def validate_promo_code(self, value):
        try:
            promo_code = Promo_Code.objects.get(code=value)
        except Promo_Code.DoesNotExist:
            raise serializers.ValidationError("Invalid promo code")
        return promo_code