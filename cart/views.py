from django.shortcuts import get_object_or_404
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework import generics
from .models import *
from product.models import Product
from rest_framework.permissions import IsAuthenticated
from rest_framework.authentication import TokenAuthentication,SessionAuthentication
from .serializers import CartItemSerializer
from decimal import Decimal

class AddToCartView(generics.CreateAPIView):
    permission_classes = [IsAuthenticated]
    authentication_classes = [SessionAuthentication, TokenAuthentication]
    serializer_class = CartItemSerializer  # Use the serializer for cart items
    def get(self, request, *args, **kwargs):
        user = self.request.user
        cart, created = Cart.objects.get_or_create(user=user)
        if created:
            return Response({"message": "Cart created"}, status=status.HTTP_200_OK)
        elif cart:
            return Response({"message": "Cart Exists Proceed to post"}, status=status.HTTP_200_OK)

    def create(self, request, *args, **kwargs):
        product_id = request.data.get('product')
        quantity = request.data.get('quantity')
        product = get_object_or_404(Product, pk=product_id)
        user = self.request.user

        # Check if the user has an existing cart
        cart, created = Cart.objects.get_or_create(user=user)

        # Check if the product is already in the cart
        cart_item, item_created = CartItem.objects.get_or_create(cart=cart, product=product)

        # If the item already exists in the cart, increase the quantity
        if not item_created:
            cart_item.quantity += int(quantity)
            cart_item.save()
        return Response({"message": "Item added to cart"}, status=status.HTTP_200_OK)
 
class RemoveFromCartView(generics.DestroyAPIView):
    permission_classes = [IsAuthenticated]
    authentication_classes = [SessionAuthentication, TokenAuthentication]
    serializer_class = CartItemSerializer
    def delete(self, request, product_id):
        product = get_object_or_404(Product, pk=product_id)
        user = request.user

        try:
            cart = Cart.objects.get(user=user)
            cart_item = CartItem.objects.get(cart=cart, product=product)
            if cart_item.quantity > 1:
                cart_item.quantity -= 1
                cart_item.save()
            else:
                cart_item.delete()
            return Response({"message": "Item removed from cart"}, status=status.HTTP_200_OK)
        except Cart.DoesNotExist:
            return Response({"message": "User does not have a cart"}, status=status.HTTP_400_BAD_REQUEST)
        except CartItem.DoesNotExist:
            return Response({"message": "Item not found in the cart"}, status=status.HTTP_404_NOT_FOUND)


class CartView(APIView):
    permission_classes = [IsAuthenticated]
    authentication_classes = [SessionAuthentication, TokenAuthentication]

    def get(self, request):
        user = request.user

        try:
            cart = Cart.objects.get(user=user)
            cart_items = CartItem.objects.filter(cart=cart)
            cart_data = [{"product": item.product.title, "product_id": item.product.pk, "quantity": item.quantity} for item in cart_items]
            
            total_price = Decimal(0)  # Initialize total_price as Decimal
            for item in cart_items:
                total_price += item.product.price * item.quantity  # Accumulate total price

            return Response({"cart_data": cart_data, "total_price": total_price}, status=status.HTTP_200_OK)
        except Cart.DoesNotExist:
            return Response({"message": "User does not have a cart"}, status=status.HTTP_400_BAD_REQUEST)
