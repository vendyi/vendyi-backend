from rest_framework import generics
from rest_framework import status
from rest_framework.response import Response
from rest_framework.authentication import TokenAuthentication,SessionAuthentication
from .models import SavedPayment
from .serializers import SavedPaymentSerializer
from rest_framework.permissions import IsAuthenticated
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