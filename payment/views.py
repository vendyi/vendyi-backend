from rest_framework import generics
import requests
from rest_framework import status
from rest_framework.response import Response
from rest_framework.authentication import TokenAuthentication,SessionAuthentication
from .models import SavedPayment, Order
from .serializers import SavedPaymentSerializer, PaymentSerializer
from rest_framework.permissions import IsAuthenticated
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
    
#Actual Payment API
class PaymentCreateAPIView(generics.CreateAPIView):
    serializer_class = PaymentSerializer

    def perform_create(self, serializer):
        # Extract payment-related data from the serializer
        order_id = serializer.validated_data.get('order_id')
        currency = serializer.validated_data.get('currency')
        amount = serializer.validated_data.get('amount')
        product = serializer.validated_data.get('product')
        # Retrieve the order from the database or create a new one
        order, created = Order.objects.get_or_create(user=self.request.user)

        # Ensure the order is not already paid
        if not order.paid:
            # Replace this with your actual payment processing logic
            pay = process_payment()

            if pay:
                # Once payment is processed, update the order and save it
                order.paid = True
                order.shipped = True
                order.product = product
                order.amount = amount
                order.save()

                # Now, you can update the user's cart (assuming you have a Cart model)
                # Replace this with your cart logic
                user = self.request.user  # Assuming you're using authentication
                #user.cart.clear()  # Clear the user's cart

                serializer.save(order=order)  # Save the payment record with the associated order
                return True
            else:
                return False
        else:
            return False

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        if self.perform_create(serializer):
            headers = self.get_success_headers(serializer.data)
            return Response(serializer.data, status=201, headers=headers)
        else:
            return Response({"message": "Payment Failed"}, status=400)
