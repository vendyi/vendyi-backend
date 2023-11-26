from rest_framework import status, generics
from rest_framework.response import Response
from product.models import Product
from product.serializers import *
from .serializers import *
from accounts.models import User
from rest_framework.views import APIView
from accounts.serializers import *
from rest_framework.exceptions import PermissionDenied
from decimal import Decimal
from rest_framework.permissions import IsAuthenticated
from product.permissions import IsVendor
from rest_framework.authentication import TokenAuthentication,SessionAuthentication
import string
import secrets
from .analytics import get_total_sales_for_vendor, get_most_sold_items_for_vendor, get_repeat_customers_for_vendor, get_least_sold_items_for_vendor
from payment.models import Order, OrderItem
from payment.serializers import OrderSerializer

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

class VendorListView(generics.ListAPIView):
    authentication_classes = [SessionAuthentication, TokenAuthentication]
    serializer_class = VendorProfileSerializer
    permission_classes = [IsAuthenticated]
    queryset = VendorProfile.objects.all()
    def list(self, request, *args, **kwargs):
        queryset = self.get_queryset()
        if not queryset.exists():
            return Response({"message": "No vendors found"}, status=status.HTTP_400_BAD_REQUEST)
        else:
            return super().list(request, *args, **kwargs)

class VendorUpdateView(generics.UpdateAPIView):
    serializer_class = VendorUpdateSerializer
    permission_classes = [IsAuthenticated, IsVendor]
    authentication_classes = [SessionAuthentication, TokenAuthentication]
    def get_object(self):
        vendor = Vendor.objects.get(user=self.request.user)
        return vendor
    def update(self, request, *args, **kwargs):
        instance = self.get_object()
        serializer = self.get_serializer(instance, data=request.data)
        serializer.is_valid(raise_exception=True)
        id_card = request.data.get('ID_card', None)
        if id_card:
            serializer.save(is_active=True)
        else:
            serializer.save()
        return Response({"message": "Vendor updated successfully"}, status=status.HTTP_200_OK)
  
class CreateProductView(generics.CreateAPIView):
    queryset = Product.objects.all()
    serializer_class = ProductCreateSerializer
    permission_classes = [IsAuthenticated, IsVendor]
    authentication_classes = [SessionAuthentication, TokenAuthentication]
    
    def calculate_profit(self, price):
        # Convert string to Decimal if it's not already
        price = Decimal(str(price))
        
        # Define price ranges and their corresponding additional fees
        price_ranges = [
            (Decimal('0'), Decimal('100'), Decimal('0.5')),  # (Min price, Max price, Additional fee)
            (Decimal('100'), Decimal('500'), Decimal('1')),
            (Decimal('500'), Decimal('1000'), Decimal('1.5')),
            (Decimal('1000'), Decimal('100000'), Decimal('2')),
            # Add more ranges if needed
        ]
        
        # Determine the additional fee based on the price range
        additional_fee = Decimal('0')
        for min_price, max_price, fee in price_ranges:
            if min_price <= price < max_price:
                additional_fee = fee
                break
        
        # If the price is above all defined ranges, apply the maximum additional fee
        if price >= price_ranges[-1][1]:
            additional_fee = price_ranges[-1][2]

        # Calculate the total price including the dynamic additional fee
        total_price = price + additional_fee
        return total_price
    
    def perform_create(self, serializer):
        price = serializer.validated_data['price']
        adjusted_price = self.calculate_profit(price)
        serializer.validated_data['price'] = adjusted_price
        serializer.validated_data['vendor_price'] = price
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
    serializer_class = ProductUpdateSerializer
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
        
    def calculate_profit(self, price):
        # Convert string to Decimal if it's not already
        price = Decimal(str(price))
        
        # Define price ranges and their corresponding additional fees
        price_ranges = [
            (Decimal('0'), Decimal('100'), Decimal('0.5')),  # (Min price, Max price, Additional fee)
            (Decimal('100'), Decimal('500'), Decimal('1')),
            (Decimal('500'), Decimal('1000'), Decimal('1.5')),
            (Decimal('1000'), Decimal('100000'), Decimal('2')),
            # Add more ranges if needed
        ]
        
        # Determine the additional fee based on the price range
        additional_fee = Decimal('0')
        for min_price, max_price, fee in price_ranges:
            if min_price <= price < max_price:
                additional_fee = fee
                break
        
        # If the price is above all defined ranges, apply the maximum additional fee
        if price >= price_ranges[-1][1]:
            additional_fee = price_ranges[-1][2]

        # Calculate the total price including the dynamic additional fee
        total_price = price + additional_fee
        return total_price
    
    def check_vendor(self, product, user):
        try:
            vendor = Vendor.objects.get(user=user)
        except Vendor.DoesNotExist:
            raise PermissionDenied("Vendor not found")

        if product.vendor != vendor:
            raise PermissionDenied("You do not have permission to edit this product.")
        
    def update(self, request, *args, **kwargs):
        product = self.get_object()
        self.check_vendor(product, self.request.user)

        price = self.request.data.get('price')
        if price is not None and price != '':
            try:
                final_price = self.calculate_profit(price)
                product.vendor_price = price
                product.price=final_price# Set the vendor_price to the calculated final price
            except ValidationError as e:
                raise ValidationError({"price": str(e)})

        product.vendor = Vendor.objects.get(user=self.request.user)
        # Set the product's vendor to the request's user's vendor
        product.save()

        # Instead of modifying request.data, pass the modified price as context to the serializer
        serializer_context = {
            'request': request,
            'format': self.format_kwarg,
            'view': self,
            'final_price': final_price
        }

        # Get the serializer instance
        serializer = self.get_serializer(product, data=request.data, context=serializer_context, partial=kwargs.pop('partial', False))

        # Check if the serializer is valid
        serializer.is_valid(raise_exception=True)

        # Perform the update
        self.perform_update(serializer)

        # Return the response
        return Response(serializer.data)

class DeleteProductView(generics.DestroyAPIView):
    permission_classes = [IsAuthenticated, IsVendor]
    authentication_classes = [SessionAuthentication, TokenAuthentication]
    queryset = Product.objects.all()
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
        return Response({"message": "Promo code terminated successfully"}, status=status.HTTP_200_OK)

class ListVendorPromoCodes(generics.ListAPIView):
    authentication_classes = [SessionAuthentication, TokenAuthentication]
    serializer_class = PromocodeListSerializer
    permission_classes = [IsAuthenticated, IsVendor]
    
    def get_queryset(self):
        # Get the authenticated user's vendor
        vendor = Vendor.objects.get(user=self.request.user)
        # Filter promo codes by the vendor
        return Promo_Code.objects.filter(vendor=vendor)
    
    def list(self, request, *args, **kwargs):
        
        queryset = self.get_queryset()
        if not queryset.exists():
            return Response({"message": "No Promo Codes by this vendor"}, status=status.HTTP_400_BAD_REQUEST)
        else:
            return super().list(request, *args, **kwargs)
        
class VendorDetailView(generics.RetrieveAPIView):
    authentication_classes = [SessionAuthentication, TokenAuthentication]
    serializer_class = VendorProfileSerializer
    permission_classes = [IsAuthenticated, IsVendor]
    def get_object(self):
        # Get the authenticated user's vendor
        pk = self.kwargs['pk']
        vendor = Vendor.objects.get(pk=pk)
        # Get the vendor's profile
        vendor_profile = VendorProfile.objects.get(vendor=vendor)
        return vendor_profile
    def retrieve(self, request, *args, **kwargs):
        instance = self.get_object()
        serializer = self.get_serializer(instance)
        amount_of_followers = instance.followers.count()
        return Response({"data":serializer.data, "Total Followers": amount_of_followers}, status=status.HTTP_200_OK)

class VendorProfileUpdateView(generics.UpdateAPIView):
    serializer_class = VendorProfileUpdateSerializer
    permission_classes = [IsAuthenticated, IsVendor]
    authentication_classes = [SessionAuthentication, TokenAuthentication]
    def get_object(self):
        # Get the authenticated user's vendor
        vendor = Vendor.objects.get(user=self.request.user)
        # Get the vendor's profile
        vendor_profile = VendorProfile.objects.get(vendor=vendor)
        return vendor_profile
    def update(self, request, *args, **kwargs):
        instance = self.get_object()
        serializer = self.get_serializer(instance, data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response({"message": "Vendor profile updated successfully"}, status=status.HTTP_200_OK)
    
class VendorAddFollowersView(generics.CreateAPIView):
    serializer_class = VendorProfileUpdateSerializer
    permission_classes = [IsAuthenticated]
    authentication_classes = [SessionAuthentication, TokenAuthentication]
    def get_object(self):
        # Get the authenticated user's vendor
        user = pk=self.kwargs['pk']
        vendor = Vendor.objects.get(pk=user)
        # Get the vendor's profile
        vendor_profile = VendorProfile.objects.get(vendor=vendor)
        return vendor_profile
    def create(self, request, *args, **kwargs):
        instance = self.get_object()
        user = User.objects.get(pk=request.user.id)
        instance.followers.add(user)
        instance.save()
        return Response({"message": "User added successfully"}, status=status.HTTP_200_OK)

class VendorRemoveFollowersView(generics.CreateAPIView):
    serializer_class = VendorProfileUpdateSerializer
    permission_classes = [IsAuthenticated]
    authentication_classes = [SessionAuthentication, TokenAuthentication]
    def get_object(self):
        # Get the authenticated user's vendor
        user = pk=self.kwargs['pk']
        vendor = Vendor.objects.get(pk=user)
        # Get the vendor's profile
        vendor_profile = VendorProfile.objects.get(vendor=vendor)
        return vendor_profile
    def create(self, request, *args, **kwargs):
        instance = self.get_object()
        user = User.objects.get(pk=request.user.id)
        instance.followers.remove(user)
        instance.save()
        return Response({"message": "User removed successfully"}, status=status.HTTP_200_OK)

class VendorFollowersView(generics.ListAPIView):
    authentication_classes = [SessionAuthentication, TokenAuthentication]
    serializer_class = VendorFollowersSerializer
    permission_classes = [IsAuthenticated]
    def get_queryset(self):
        # Get the authenticated user's vendor
        user = self.kwargs['pk']  # Corrected line
        vendor = Vendor.objects.get(pk=user)
        # Get the vendor's profile
        vendor_profile = VendorProfile.objects.filter(vendor=vendor)  # Corrected line
        return vendor_profile

    
    def list(self, request, *args, **kwargs):
        queryset = self.get_queryset()
        if not queryset.exists():
            return Response({"message": "No followers for this vendor"}, status=status.HTTP_200_OK)
        
        followers_list = []
        for user in queryset[0].followers.all():
            user_profile = User.objects.get(email=user)
            serializer = FullUserSerializer(user_profile, context={'request': request})
            followers_list.append(serializer.data)

        number_of_followers = len(followers_list)
        
        return Response({
            "Total Followers": number_of_followers, 
            "Followers": followers_list
        }, status=status.HTTP_200_OK)

class VerifyVendorPinView(generics.CreateAPIView):
    serializer_class = VerifyVendorPinSerializer
    permission_classes = [IsAuthenticated]
    authentication_classes = [SessionAuthentication, TokenAuthentication]
    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        
        pin = serializer.validated_data['pin']
        vendor = Vendor.objects.get(user=request.user)
        if vendor.pin == pin:
            return Response({"message": "Pin is correct"}, status=status.HTTP_200_OK)
        else:
            return Response({"message": "Pin is incorrect"}, status=status.HTTP_400_BAD_REQUEST)

class VendorActiveHoursCreateView(generics.CreateAPIView):
    permission_classes = [IsAuthenticated, IsVendor]
    authentication_classes = [SessionAuthentication, TokenAuthentication]
    queryset = VendorActiveHours.objects.all()
    serializer_class = VendorActiveHoursSerializer

    def perform_create(self, serializer):
        # You can add additional logic here if needed
        if serializer.validated_data['start_time'] >= serializer.validated_data['end_time']:
            raise serializers.ValidationError("Start time must be earlier than end time.")
        serializer.save()

class VendorActiveHoursListView(generics.ListAPIView):
    queryset = VendorActiveHours.objects.all()
    serializer_class = VendorActiveHoursListSerializer
    
    def get_queryset(self):
        # Get the authenticated user's vendor
        pk = self.kwargs['pk']
        vendor = Vendor.objects.get(pk=pk)
        # Filter active hours by the vendor
        return VendorActiveHours.objects.filter(vendor=vendor)

class VendorActiveHoursRetrieveUpdateDestroyView(generics.RetrieveUpdateDestroyAPIView):
    permission_classes = [IsAuthenticated, IsVendor]
    authentication_classes = [SessionAuthentication, TokenAuthentication]
    queryset = VendorActiveHours.objects.all()
    serializer_class = VendorActiveHoursSerializer

class VendorAnalyticsView(APIView):
    permission_classes = [IsAuthenticated, IsVendor]
    authentication_classes = [SessionAuthentication, TokenAuthentication]
    def get(self, request, format=None):
        vendor_id = Vendor.objects.get(user=request.user).id

        analytics_data = {
            'total_sales': get_total_sales_for_vendor(vendor_id),
            'most_sold_items': get_most_sold_items_for_vendor(vendor_id),
            'repeat_customers': get_repeat_customers_for_vendor(vendor_id),
            'least_sold_items': get_least_sold_items_for_vendor(vendor_id),
            # Add more analytics data as needed
        }
        return Response(analytics_data)

class VendorWalletView(APIView):
    permission_classes = [IsAuthenticated, IsVendor]
    authentication_classes = [SessionAuthentication, TokenAuthentication]
    def get(self, request, format=None):
        vendor = Vendor.objects.get(user=request.user)
        wallet, created = Wallet.objects.get_or_create(vendor=vendor)
        wallet_data = {
            'total_balance': wallet.total_balance,
            'available_balance': wallet.available_balance,
            'pending_balance': wallet.pending_balance,
        }
        return Response(wallet_data)

class VendorLowStockProductsView(generics.ListAPIView):
    permission_classes = [IsAuthenticated, IsVendor]
    authentication_classes = [SessionAuthentication, TokenAuthentication]
    serializer_class = ProductListSerializer
    def get_queryset(self):
        # Get the authenticated user's vendor
        vendor = Vendor.objects.get(user=self.request.user)
        # Filter products by the vendor
        return Product.objects.filter(vendor=vendor, amount_in_stock__lte=5)

class VendorOrdersView(generics.ListAPIView):
    permission_classes = [IsAuthenticated, IsVendor]
    authentication_classes = [SessionAuthentication, TokenAuthentication]
    serializer_class = OrderSerializer
    def get_queryset(self):
        # Get the authenticated user's vendor
        vendor = Vendor.objects.get(user=self.request.user)
        # Filter orders by the vendor
        return Order.objects.filter(items__product__vendor=vendor).distinct()

class VendorTransactionListView(generics.ListAPIView):
    permission_classes = [IsAuthenticated, IsVendor]
    authentication_classes = [SessionAuthentication, TokenAuthentication]
    serializer_class = TransactionSerializer
    def get_queryset(self):
        # Get the authenticated user's vendor
        vendor = Vendor.objects.get(user=self.request.user)
        # Filter transactions by the vendor
        return Transaction.objects.filter(vendor=vendor).order_by('-created_at')