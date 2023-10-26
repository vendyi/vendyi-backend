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
import string
import secrets

def generate_promo_code(length=8):
    """Generate a random promo code of the specified length."""
    alphabet = string.ascii_uppercase + string.digits
    return ''.join(secrets.choice(alphabet) for _ in range(length))

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
    authentication_classes = [SessionAuthentication, TokenAuthentication]
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
    authentication_classes = [SessionAuthentication, TokenAuthentication]
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
    authentication_classes = [SessionAuthentication, TokenAuthentication]

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
        
class CreatePromoCode(generics.CreateAPIView):
    serializer_class = PromoCodeSerializer
    permission_classes = [IsAuthenticated, IsVendor]
    authentication_classes = [SessionAuthentication, TokenAuthentication]
    
    def create(self, request, *args, **kwargs):
        vendor = Vendor.objects.get(user=self.request.user)  # Get the authenticated vendor
        code = request.data.get('code')  # Get the promo code from the request data
        if code:
            pass
        else:
            code = generate_promo_code()  # Generate a unique promo code
        discount_percentage = request.data.get('discount_percentage')  # Get the discount percentage from the request data
        discount_start_date = request.data.get('discount_start_date')  # Get the discount start date from the request data
        discount_end_date = request.data.get('discount_end_date')   # Get the discount end date from the request data
        if discount_end_date and discount_start_date:
            promo_code = Promo_Code.objects.create(vendor=vendor, code=code, discount_percentage=discount_percentage, discount_start_date=discount_start_date, discount_end_date=discount_end_date)  # Create a new Promo_Code object with the provided data
        else:
            promo_code = Promo_Code.objects.create(vendor=vendor, code=code, discount_percentage=discount_percentage)
        return Response({"message": "Promo code created successfully", "promo_code_id": promo_code.id, "promo_code":promo_code.code}, status=status.HTTP_201_CREATED)
    
class TerminatePromoCode(generics.UpdateAPIView):
    permission_classes = [IsAuthenticated, IsVendor]
    authentication_classes = [SessionAuthentication, TokenAuthentication]
    queryset = Promo_Code.objects.all()
    serializer_class = PromoCodeSerializer

    def update(self, request, *args, **kwargs):
        instance = self.get_object()
        vendor = Vendor.objects.get(user=self.request.user)
        if instance.vendor != vendor:
            raise PermissionDenied("You do not have permission to terminate this promo code.")
        instance.is_active = False
        instance.save()
        serializer = self.get_serializer(instance)
        return Response(serializer.data,{"message": "Promo code terminated successfully"}, status=status.HTTP_200_OK)