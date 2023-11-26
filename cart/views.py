from django.shortcuts import get_object_or_404
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework import generics
from .models import *
from vendors.models import Promo_Code
from product.models import Product
from rest_framework.permissions import IsAuthenticated
from rest_framework.authentication import TokenAuthentication,SessionAuthentication
from .serializers import CartItemSerializer, PromoCodeApplySerializer

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

        try:
            promo = Promo_Code.objects.get(code=promo_code)
        except Promo_Code.DoesNotExist:
            return Response({"message": "Promo code does not exist"}, status=status.HTTP_400_BAD_REQUEST)

        if not promo.is_active:
            return Response({"message": "Promo code is not active"}, status=status.HTTP_400_BAD_REQUEST)

        user = request.user
        if user.promo_code.filter(code=promo_code).exists():
            return Response({"message": "Promo code already applied"}, status=status.HTTP_400_BAD_REQUEST)

        cart = Cart.objects.get(user=user)
        cart_items = CartItem.objects.filter(cart=cart, product__vendor=promo.vendor)

        for item in cart_items:
            cart.total_price -= item.product.price * item.quantity
            cart.total_price += item.product.price * item.quantity * (1 - promo.discount_percentage / 100)
            item.product.price = item.product.price * (1 - promo.discount_percentage / 100)
            item.product.vendor_price = item.product.vendor_price * (1 - promo.discount_percentage / 100)
            item.product.save()
        cart.save()

        user.promo_code.add(promo)
        user.save()

        response_data = {"promo_code": promo.code, "total_price": cart.total_price}
        return Response(response_data, status=status.HTTP_200_OK)

class DeleteFromCartView(generics.DestroyAPIView):
    permission_classes = [IsAuthenticated]
    authentication_classes = [SessionAuthentication, TokenAuthentication]
    serializer_class = CartItemSerializer
    def delete(self, request, product_id):
        product = get_object_or_404(Product, pk=product_id)
        user = request.user

        try:
            cart = Cart.objects.get(user=user)
            cart_item = CartItem.objects.get(cart=cart, product=product)
            cart_item.delete()
            cart.total_price -= product.price * cart_item.quantity
            cart.save()
            return Response({"message": "Item removed from cart"}, status=status.HTTP_200_OK)
        except Cart.DoesNotExist:
            return Response({"message": "User does not have a cart"}, status=status.HTTP_400_BAD_REQUEST)
        except CartItem.DoesNotExist:
            return Response({"message": "Item not found in the cart"}, status=status.HTTP_404_NOT_FOUND)