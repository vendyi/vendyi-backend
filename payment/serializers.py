from rest_framework import serializers
from .models import SavedPayment, Order, OrderItem
from product.models import Product

class SavedPaymentSerializer(serializers.ModelSerializer):
    class Meta:
        model = SavedPayment
        fields = '__all__'

class OrderItemSerializer(serializers.ModelSerializer):
    product = serializers.PrimaryKeyRelatedField(queryset=Product.objects.all())

    class Meta:
        model = OrderItem
        fields = ['product', 'quantity', 'price','size','color']

class PaymentSerializer(serializers.Serializer):
    amount = serializers.DecimalField(max_digits=10, decimal_places=2)
    order_items = OrderItemSerializer(many=True)


class OrderSerializer(serializers.ModelSerializer):
    items = OrderItemSerializer(many=True, read_only=True)

    class Meta:
        model = Order
        fields = ['id', 'customer', 'total_price', 'status', 'items']