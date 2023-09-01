from rest_framework import generics, status
from rest_framework.response import Response
from .models import *
from account.models import *
from .serializers import *
from rest_framework.permissions import IsAuthenticated
from .permissions import IsVendor
from rest_framework.authentication import TokenAuthentication,SessionAuthentication
from rest_framework.generics import get_object_or_404

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
    
    def get(self, request, *args, **kwargs):
        product_id = kwargs['id']
        try:
            product = Product.objects.get(pk=product_id)
        except Product.DoesNotExist:
            return Response({"message": "This product does not exist"}, status=status.HTTP_404_NOT_FOUND)
        
        # Add recently viewed item to the user's profile if authenticated
        if request.user.is_authenticated:
            recently_viewed_item, created = RecentlyViewed.objects.get_or_create(
                user=request.user,
                product=product
            )
            try:
                request.user.userprofile.recently_viewed.add(recently_viewed_item)
            except:
                user_profile = UserProfile.objects.create(user=request.user)
                request.user.userprofile.recently_viewed.add(recently_viewed_item)
        
        serializer = self.get_serializer(product)
        return Response(serializer.data)
    
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

class ProductLikeView(generics.CreateAPIView):
    queryset = Product.objects.all()
    permission_classes = [IsAuthenticated]
    authentication_classes = [SessionAuthentication, TokenAuthentication]
    def create(self, request, *args, **kwargs):
        product = self.get_product_object()
        product.increment_likes()  # Increment the likes count
        return Response({"total_likes": product.likes}, status=status.HTTP_200_OK)
    
    def get_product_object(self):
        product_id = self.kwargs.get('product_id')
        return get_object_or_404(Product, pk=product_id)
    
class ProductDislikeView(generics.CreateAPIView):
    queryset = Product.objects.all()
    permission_classes = [IsAuthenticated]
    authentication_classes = [SessionAuthentication, TokenAuthentication]
    def create(self, request, *args, **kwargs):
        product = self.get_product_object()
        product.decrement_likes()  # Increment the likes count
        return Response({"total_likes": product.likes}, status=status.HTTP_200_OK)
    
    def get_product_object(self):
        product_id = self.kwargs.get('product_id')
        return get_object_or_404(Product, pk=product_id)
   
class RecentlyViewedListView(generics.ListAPIView):
    serializer_class = RecentlyViewedSerializer
    permission_classes = [IsAuthenticated]
    authentication_classes = [SessionAuthentication, TokenAuthentication]
    
    def get_queryset(self):
        if self.request.user.is_authenticated:
            return RecentlyViewed.objects.filter(user=self.request.user)
        else:
            return RecentlyViewed.objects.none() 

class ProductCommentCreateView(generics.CreateAPIView):
    serializer_class = ProductCommentSerializer
    permission_classes = [IsAuthenticated]
    authentication_classes = [SessionAuthentication, TokenAuthentication]
    def create(self, request, *args, **kwargs):
        product_id = request.data.get('product')
        text = request.data.get('text')
        
        try:
            product = Product.objects.get(pk=product_id)
        except Product.DoesNotExist:
            return Response({"message": "Product does not exist", "produvt":product_id}, status=status.HTTP_404_NOT_FOUND)
        vendor = product.vendor
        vendor_user = vendor.user
        if request.user.is_vendor and request.user == vendor_user:
            is_vendor_comment = True # Check if user is the vendor of the product
        else:
            is_vendor_comment = False
        comment = ProductComment.objects.create(user=request.user, product=product, text=text, is_vendor_comment=is_vendor_comment)
        serializer = ProductCommentSerializer(comment)
        return Response(serializer.data, status=status.HTTP_201_CREATED)

class CommentReplyCreateView(generics.CreateAPIView):
    serializer_class = CommentReplySerializer
    permission_classes = [IsAuthenticated]
    authentication_classes = [SessionAuthentication, TokenAuthentication]
    def create(self, request, *args, **kwargs):
        comment_id = request.data.get('comment_id')
        text = request.data.get('text')
        
        try:
            comment = ProductComment.objects.get(pk=comment_id)
        except ProductComment.DoesNotExist:
            return Response({"message": "Comment does not exist"}, status=status.HTTP_404_NOT_FOUND)
        is_vendor_comment = request.user == comment.product.vendor
        reply = CommentReply.objects.create(user=request.user, comment=comment, text=text, is_vendor_comment=is_vendor_comment)
        serializer = CommentReplySerializer(reply)
        return Response(serializer.data, status=status.HTTP_201_CREATED)