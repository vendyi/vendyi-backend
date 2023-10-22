from rest_framework import status, generics
from rest_framework.response import Response
from product.models import Product
from product.serializers import *
from .serializers import *
from rest_framework.exceptions import PermissionDenied
from decimal import Decimal
from rest_framework.permissions import IsAuthenticated
from product.permissions import IsVendor
from rest_framework.authentication import TokenAuthentication,SessionAuthentication
class CreateVendor(generics.CreateAPIView):
    serializer_class = VendorSerializer
    authentication_classes = [TokenAuthentication,SessionAuthentication]
    permission_classes = [IsAuthenticated]
    def perform_create(self, serializer):
        # Check if ID_card is provided in the request data
        id_card = self.request.data.get('ID_card', None)

        if id_card:
            # If ID_card is provided, set is_active to True
            serializer.save(is_active=True)
        else:
            # If ID_card is not provided, set is_active to False
            serializer.save(is_active=False)

    def post(self, request, format=None):
        # The perform_create method handles the creation
        return super(CreateVendor, self).post(request, format)
    
class CreateProductView(generics.CreateAPIView):
    queryset = Product.objects.all()
    serializer_class = ProductCreateSerializer
    permission_classes = [IsAuthenticated, IsVendor]

    def calculate_profit(self, price):
        # Define the standard profit margin (e.g., 5%)
        standard_margin_factor = Decimal('0.05')  # 5%
        # Define the profit margin for prices above $500 but below $10,000 (e.g., 2.5%)
        high_margin_factor = Decimal('0.025')  # 2.5%
        # Define the profit margin for prices at or above $10,000 (e.g., 1.5%)
        highest_margin_factor = Decimal('0.015')  # 1.5%
        # Define the price threshold for applying the high margin (e.g., $500)
        high_price_threshold = Decimal('500')
        # Define the price threshold for applying the highest margin (e.g., $10,000)
        highest_price_threshold = Decimal('10000')

        if price >= highest_price_threshold:
            # For products priced at or above $10,000, use the highest margin factor
            profit = price * highest_margin_factor
        elif price >= high_price_threshold:
            # For products priced between $500 and $10,000, use the high margin factor
            profit = price * high_margin_factor
        else:
            # For all other products, use the standard margin factor
            profit = price * standard_margin_factor

        return price + profit

    def perform_create(self, serializer):
        price = serializer.validated_data['price']
        # Calculate the profit-adjusted price
        adjusted_price = self.calculate_profit(price)
        # Update the product's price with the adjusted price
        serializer.validated_data['price'] = adjusted_price
        # Set the product's vendor to the authenticated vendor
        vendor = Vendor.objects.get(user=self.request.user)
        serializer.validated_data['vendor'] = vendor
        serializer.save()

class ListVendorProducts(generics.ListAPIView):
    
    serializer_class = ProductListSerializer
    permission_classes = [IsAuthenticated, IsVendor]
    
    def get_queryset(self):
        # Get the authenticated user's vendor
        vendor = Vendor.objects.get(user=self.request.user)
        # Filter products by the vendor
        return Product.objects.filter(vendor=vendor)
    
    def list(self, request, *args, **kwargs):
        
        queryset = self.get_queryset()
        if not queryset.exists():
            return Response({"message": "No Products by this vendor"}, status=status.HTTP_400_BAD_REQUEST)
        else:
            return super().list(request, *args, **kwargs)
        
class UpdateProductView(generics.UpdateAPIView):
    serializer_class = ProductCreateSerializer
    permission_classes = [IsAuthenticated]

    def get_object(self):
        # Get the product by its ID
        try:
            product = Product.objects.get(pk=self.kwargs['pk'])
        except:
            return Response({"message":"Product des not exist"}, status=400)
        # Check if the product's vendor matches the authenticated user's vendor
        vendor = Vendor.objects.get(user=self.request.user)
        if product.vendor == vendor:
            return product
        else:
            # Raise a permission denied exception or return an error response
            raise PermissionDenied("You do not have permission to edit this product.")

class DeleteProductView(generics.DestroyAPIView):
    permission_classes = [IsAuthenticated]

    def destroy(self, request, *args, **kwargs):
        product = self.get_object()
        # Check if the product's vendor matches the authenticated user's vendor
        vendor = Vendor.objects.get(user=self.request.user)
        if product.vendor == vendor:
            product.delete()
            return Response({"message": "Product deleted successfully"}, status=status.HTTP_204_NO_CONTENT)
        else:
            raise PermissionDenied("You do not have permission to delete this product.")