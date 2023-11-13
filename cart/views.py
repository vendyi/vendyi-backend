from django.shortcuts import get_object_or_404
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework import generics
from .models import *
from product.models import Product
from rest_framework.permissions import IsAuthenticated
from rest_framework.authentication import TokenAuthentication,SessionAuthentication
from .serializers import CartItemSerializer, PromoCodeApplySerializer
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
        color = request.data.get('color')
        size = request.data.get('size')
        product = get_object_or_404(Product, pk=product_id)
        user = self.request.user

        # Check if the user has an existing cart
        cart, created = Cart.objects.get_or_create(user=user)
        
        # Check if the product is already in the cart
        cart_item, item_created = CartItem.objects.get_or_create(cart=cart, product=product)
        if not item_created:
            cart_item.quantity += int(quantity)
            if size is not None:
                cart_item.size = size

            if color is not None:
                cart_item.color = color
            cart_item.save()
            
            cart.total_price += product.price * int(quantity)
            
        else:
            cart_item.quantity = int(quantity)
            cart_item.save()
            if cart.total_price == 0:
                cart.total_price = product.price * int(quantity)
            else:
                cart.total_price += product.price * int(quantity)
        cart.save()
            
        if size is not None:
            cart_item.size = size

        if color is not None:
            cart_item.color = color

        cart_item.save()
        
        
        # If the item already exists in the cart, increase the quantity
        
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
                cart.total_price -= product.price
                cart.save()
            else:
                cart_item.delete()
                cart.total_price -= product.price
                cart.save()
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
            
            return Response({"cart_data": cart_data, "total_price": cart.total_price}, status=status.HTTP_200_OK)
        except Cart.DoesNotExist:
            return Response({"message": "User does not have a cart"}, status=status.HTTP_400_BAD_REQUEST)

class ApplyPromoCodeView(generics.CreateAPIView):
    permission_classes = [IsAuthenticated]
    authentication_classes = [SessionAuthentication, TokenAuthentication]
    serializer_class = PromoCodeApplySerializer

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        promo_code = serializer.validated_data['promo_code']
        cart = Cart.objects.get(user=request.user)
        cart_items = CartItem.objects.filter(cart=cart)
        total_price = Decimal(0)
        for item in cart_items:
            if item.product.vendor == promo_code.vendor and promo_code.is_active:  # Check if the product belongs to the vendor, the promo code is valid, and the promo code is active
                cart.total_price -= item.product.price * item.quantity
                cart.save()
                cart.total_price += item.product.price * item.quantity * (1 - promo_code.discount_percentage / 100)
                cart.save()
            elif promo_code.is_active != True:
                return Response({"message": "Promo code is not active"}, status=status.HTTP_400_BAD_REQUEST)
            else:
                total_price += item.product.price * item.quantity
        response_data = {"promo_code": promo_code.code, "total_price": cart.total_price}
        return Response(response_data, status=status.HTTP_200_OK)