from rest_framework import generics
from rest_framework import status
from rest_framework.response import Response
from django.shortcuts import get_object_or_404
from product.models import Product
from cart.models import Cart, CartItem
from rest_framework.authentication import TokenAuthentication,SessionAuthentication
from .models import SavedPayment, Order, OrderItem
from vendors.models import Wallet, Transaction
from .serializers import SavedPaymentSerializer, PaymentSerializer
from rest_framework.permissions import IsAuthenticated
from django.db import transaction

class StockIssueException(Exception):
    pass

class PaymentFailureException(Exception):
    pass
#Payment Function
def process_payment():
    return True

class SavedPaymentCreateView(generics.CreateAPIView):
    serializer_class = SavedPaymentSerializer
    permission_classes = [IsAuthenticated]
    authentication_classes = [SessionAuthentication, TokenAuthentication]
    def create(self, request, *args, **kwargs):
        data = request.data
        momo = data.get('momo')
        card_number = data.get('card_number')
        card_exp = data.get('card_exp')
        card_type = data.get('card_type')

        if momo:
            momo_number = data.get('momo_number')
            momo_type = data.get('momo_type')
            if not (momo_number and momo_type):
                return Response({'error': 'Incomplete data for Momo payment.'}, status=status.HTTP_400_BAD_REQUEST)
        else:
            if not (card_number and card_exp and card_type):
                return Response({'error': 'Incomplete data for card payment.'}, status=status.HTTP_400_BAD_REQUEST)

        # If the data is valid, pass it to the serializer for saving
        serializer = self.get_serializer(data=data)
        serializer.is_valid(raise_exception=True)
        self.perform_create(serializer)
        headers = self.get_success_headers(serializer.data)
        return Response(serializer.data, status=status.HTTP_201_CREATED, headers=headers)

class SavedPaymentListView(generics.ListAPIView):
    serializer_class = SavedPaymentSerializer
    permission_classes = [IsAuthenticated]
    authentication_classes = [SessionAuthentication, TokenAuthentication]
    def get_queryset(self):
        # Filter the queryset to retrieve the saved payments of the authenticated user
        return SavedPayment.objects.filter(user=self.request.user)
    def get(self, request, *args, **kwargs):
        queryset = self.get_queryset()
        if not queryset.exists():
            return Response({"message": "User has no saved Payments"}, status=404)
        else:
            return self.list(request, *args, **kwargs)

class SavedPaymentDeleteView(generics.DestroyAPIView):
    serializer_class = SavedPaymentSerializer
    permission_classes = [IsAuthenticated]
    authentication_classes = [SessionAuthentication, TokenAuthentication]

    def get_queryset(self):
        # Filter the queryset to retrieve the saved payments of the authenticated user
        return SavedPayment.objects.filter(user=self.request.user)
    
class SavedPaymentUpdateView(generics.UpdateAPIView):
    serializer_class = SavedPaymentSerializer
    permission_classes = [IsAuthenticated]
    authentication_classes = [SessionAuthentication, TokenAuthentication]

    def get_queryset(self):
        # Filter the queryset to retrieve the saved payments of the authenticated user
        return SavedPayment.objects.filter(user=self.request.user)
    
class PaymentCreateAPIView(generics.CreateAPIView):
    serializer_class = PaymentSerializer
    authentication_classes = [SessionAuthentication, TokenAuthentication]
    permission_classes = [IsAuthenticated]
    def get_serializer_context(self):
        context = super(PaymentCreateAPIView, self).get_serializer_context()
        context.update({"request": self.request})
        return context
    def perform_create(self, serializer):
        user = self.request.user
        amount = serializer.validated_data.get('amount')
        order_items_data = serializer.validated_data.get('order_items')
        
        order = Order.objects.create(
            customer=user, 
            total_price=amount, 
            status=0  # assuming 'PENDING' is a valid status
        )

        # Check stock for all items
        for item_data in order_items_data:
            product = get_object_or_404(Product, pk=item_data['product'].pk)
            if not product.in_stock or product.amount_in_stock < item_data['quantity']:
                raise StockIssueException("Mot enough stock")

        if not order.paid:
            with transaction.atomic():
                if process_payment():
                    order.paid = True
                    order.save()

                    for item_data in order_items_data:
                        product = Product.objects.get(pk=item_data['product'].pk)
                        order_item = OrderItem.objects.create(
                            order=order,
                            product=item_data['product'],
                            quantity=item_data['quantity'],
                            price=product.vendor_price
                        )
                        if item_data.get('color'):
                            order_item.color = item_data['color']
                        if item_data.get('size'):
                            order_item.size = item_data['size']
                        order_item.save()

                        # Update stock
                        
                        if product.amount_in_stock > 0:
                            product.amount_in_stock -= item_data['quantity']
                            product.save()
                        
                        vendor = item_data['product'].vendor
                        wallet, created = Wallet.objects.get_or_create(vendor=vendor)
                        transaction_amount = amount
                        wallet.add_pending_balance(transaction_amount)
                        Transaction.objects.create(
                            vendor=vendor,
                            amount=transaction_amount,
                            transaction_type=Transaction.CREDIT,
                            status=Transaction.PENDING
                        )

                    # Clear the user's cart
                    CartItem.objects.filter(cart__user=user).delete()
                    
                    return order
                else:
                    raise PaymentFailureException("Payment failed")
        else:
            raise PaymentFailureException("Order Already Paid for")


    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        try:
            instance = self.perform_create(serializer)
            headers = self.get_success_headers(serializer.data)
            return Response(serializer.data, status=status.HTTP_201_CREATED, headers=headers)
        except StockIssueException as e:
            return Response({"message": str(e)}, status=status.HTTP_400_BAD_REQUEST)
        except PaymentFailureException as e:
            return Response({"message": str(e)}, status=status.HTTP_400_BAD_REQUEST)
        except Exception as e:
            # Log this exception for debugging
            return Response({"message": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
