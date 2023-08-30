from rest_framework import generics, status
from rest_framework.response import Response
from .models import Product, Category
from .serializers import *
from rest_framework.permissions import IsAuthenticated
from .permissions import IsVendor
from rest_framework.authentication import TokenAuthentication,SessionAuthentication
from rest_framework.views import APIView

class ProductListView(generics.ListAPIView):
    serializer_class = ProductListSerializer

    def get_queryset(self):
        queryset = Product.objects.all()
        return queryset

    def get(self, request, *args, **kwargs):
        queryset = self.get_queryset()
        if not queryset.exists():
            return Response({"message": "No Products"})
        else:
            return self.list(request, *args, **kwargs)
        
class ProductsByCategoryView(generics.ListAPIView):
    serializer_class = ProductCategorySerializer

    def get_queryset(self):
        category_slug = self.kwargs['category_slug']
        try:
            category = Category.objects.get(slug=category_slug)
            queryset = Product.objects.filter(category=category)
            return queryset
        except Category.DoesNotExist:
            return Product.objects.none()  # Return an empty queryset
        
    def list(self, request, *args, **kwargs):
        queryset = self.get_queryset()
        if len(queryset) == 0:
            return Response({"message": "No Products in the category"})
        else:
            return super().list(request, *args, **kwargs)
        
class ProductDetailView(generics.RetrieveAPIView):
    serializer_class = ProductDetailSerializer
    lookup_field = 'id'
    def get_queryset(self):
        queryset = Product.objects.all()
        return queryset
    
    def get(self, request, *args, **kwargs):
        queryset = self.get_queryset()
        if not queryset.exists():
            return Response({"message": "This product does not exist"}, status=404)
        else:
            return self.retrieve(request, *args, **kwargs)

class CategoryListView(generics.ListAPIView):
    serializer_class = CategorySerializer

    def get_queryset(self):
        queryset = Category.objects.all()
        return queryset

    def get(self, request, *args, **kwargs):
        queryset = self.get_queryset()
        if not queryset.exists():
            return Response({"message": "No Products"})
        else:
            return self.list(request, *args, **kwargs)
        
class SetDiscountView(generics.CreateAPIView):
    serializer_class = DiscountSerializer
    permission_classes = [IsAuthenticated, IsVendor]
    authentication_classes = [SessionAuthentication, TokenAuthentication]
    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        product_id = serializer.validated_data.get('product_id')
        category_id = serializer.validated_data.get('category_id')
        discount_percentage = serializer.validated_data.get('discount_percentage')
        discount_start_date = serializer.validated_data.get('discount_start_date')
        discount_end_date = serializer.validated_data.get('discount_end_date')

        if product_id and category_id:
            return Response({"message": "You must select only one option"}, status=status.HTTP_400_BAD_REQUEST)
        elif product_id:
            try:
                product = Product.objects.get(pk=product_id)
                product.price -= (product.price * discount_percentage / 100)
                product.discount_percentage += discount_percentage
                product.save()
                if discount_end_date and discount_start_date:
                    product.discount_end_date = discount_end_date
                    product.discount_start_date = discount_start_date
                    product.save()
            except Product.DoesNotExist:
                return Response({"message": "Product Does not Exist"}, status=status.HTTP_400_BAD_REQUEST)

        elif category_id:
            try:
                category = Category.objects.get(pk=category_id)
                products_in_category = Product.objects.filter(category=category)
                for product in products_in_category:
                    product.price -= (product.price * discount_percentage / 100)
                    product.save()
            except Category.DoesNotExist:
                return Response({"message": "Category Does not Exist"}, status=status.HTTP_400_BAD_REQUEST)

        return Response({"message": "Discount applied successfully"}, status=status.HTTP_201_CREATED)
    
class TerminateDiscountView(generics.CreateAPIView):
    serializer_class = TerminateDiscountSerializer
    permission_classes = [IsAuthenticated, IsVendor]
    authentication_classes = [SessionAuthentication, TokenAuthentication]
    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        product_id = serializer.validated_data['product_id']

        try:
            product = Product.objects.get(pk=product_id)
        except Product.DoesNotExist:
            return Response({"message": "Product Does not Exist"}, status=status.HTTP_400_BAD_REQUEST)
        
        # Terminate the discount for the specified product
        product.price = (product.price /(1- product.discount_percentage / 100))
        product.discount_percentage = 0
        product.discount_start_date = None
        product.discount_end_date = None
        product.save()

        return Response({"message": "Discount terminated successfully"}, status=status.HTTP_200_OK)
