from rest_framework import generics, status
from rest_framework.response import Response
from .models import *
from accounts.models import *
from .serializers import *
from vendors.serializers import VendorSerializer
from rest_framework.permissions import IsAuthenticated
from .permissions import IsVendor
from vendors.models import Vendor
from rest_framework.authentication import TokenAuthentication,SessionAuthentication
from rest_framework.generics import get_object_or_404
from django.db.models import Count
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
        category = get_object_or_404(Category, slug=category_slug)
        queryset = Product.objects.filter(category=category)
        return queryset
        
    def list(self, request, *args, **kwargs):
        queryset = self.get_queryset()
        if not queryset.exists():
            return Response({"message": "No Products in the category"}, status=status.HTTP_400_BAD_REQUEST)
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
            
        
        serializer = self.get_serializer(product)
        return Response(serializer.data)

class CategoryListView(generics.ListAPIView):
    serializer_class = CategorySerializer

    def get_queryset(self):
        categories = Category.objects.annotate(num_products=Count('product'))
        queryset = categories.filter(num_products__gt=0)
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

        product_id = serializer.validated_data.get('product_id')
        category_id = serializer.validated_data.get('category_id')

        if product_id and category_id:
            return Response({"message": "You must select only one option"}, status=status.HTTP_400_BAD_REQUEST)
        elif product_id:
            try:
                product = Product.objects.get(pk=product_id)
                # Terminate the discount for the specified product
                if product.discount_percentage > 0:
                    product.price = (product.price /(1- product.discount_percentage / 100))
                    product.discount_percentage = 0
                    product.discount_start_date = None
                    product.discount_end_date = None
                    product.save()
                else:
                    return Response({"message": "Product has no discount"}, status=status.HTTP_200_OK)
            except Product.DoesNotExist:
                return Response({"message": "Product Does not Exist"}, status=status.HTTP_400_BAD_REQUEST)
        elif category_id:
            try:
                category = Category.objects.get(pk=category_id)
                products_in_category = Product.objects.filter(category=category)
                exemption_message = []  # To collect exempted product messages
                for product in products_in_category:
                    if product.discount_percentage > 0:
                        product.price = (product.price /(1- product.discount_percentage / 100))
                        product.discount_percentage = 0
                        product.discount_start_date = None
                        product.discount_end_date = None
                        product.save()
                    else:
                        exemption_message.append(f'Product with Id-{product.pk} has no active discounts')

                if exemption_message:
                    if len(products_in_category) == len(exemption_message):
                        return Response({"message": "All products have no active discounts"},
                                        status=status.HTTP_400_BAD_REQUEST)
                    else:
                        return Response({"message": "Discount terminated successfully for some products",
                                         "exemption_message": exemption_message}, status=status.HTTP_200_OK)
            except Category.DoesNotExist:
                return Response({"message": "Category Does not Exist"}, status=status.HTTP_400_BAD_REQUEST)

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
            return Response({"message": "Product does not exist", "product":product_id}, status=status.HTTP_404_NOT_FOUND)
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
        comment_id = request.data.get('comment')
        text = request.data.get('text')
    
        try:
            comment = ProductComment.objects.get(pk=comment_id)
        except ProductComment.DoesNotExist:
            return Response({"message": "Comment does not exist"}, status=status.HTTP_404_NOT_FOUND)
        vendor = comment.product.vendor
        vendor_user = vendor.user
        if request.user.is_vendor and request.user == vendor_user:
            is_vendor_comment = True # Check if user is the vendor of the product
        else:
            is_vendor_comment = False
        reply = CommentReply.objects.create(user=request.user, comment=comment, text=text, is_vendor_comment=is_vendor_comment)
        serializer = CommentReplySerializer(reply)
        return Response(serializer.data, status=status.HTTP_201_CREATED)

class ProductCommentListView(generics.ListAPIView):
    serializer_class = ProductCommentListSerializer
    
    def get_queryset(self):
        product_id = self.kwargs['id']
        try:# Assuming you pass the product_id in the URL
            queryset = ProductComment.objects.filter(product_id=product_id)
            return queryset
        except:
            return ProductComment.objects.none()
    
    def get(self, request, *args, **kwargs):
        queryset = self.get_queryset()
        if not queryset.exists():
            return Response({"message": "No Comments"}, status=400)
        else:
            return self.list(request, *args, **kwargs)

class CommentReplyListView(generics.ListAPIView):
    serializer_class = CommentReplyListSerializer
    
    def get_queryset(self):
        product_id = self.kwargs['id']
        try:# Assuming you pass the product_id in the URL
            queryset = CommentReply.objects.filter(comment_id=product_id)
            return queryset
        except:
            return ProductComment.objects.none()
    
    def get(self, request, *args, **kwargs):
        queryset = self.get_queryset()
        if not queryset.exists():
            return Response({"message": "No Replies"}, status=400)
        else:
            return self.list(request, *args, **kwargs)

class WishlistDetailView(generics.RetrieveAPIView):
    
    serializer_class = WishlistSerializer
    lookup_field = 'username'
    
    def get(self, request, *args, **kwargs):
        username = kwargs['username']
        
        try:
            user = User.objects.get(username=username)
    
        except User.DoesNotExist:
            return Response({"message": "Incorrect username"}, status=400)

        try:
            wishlist = Wishlist.objects.get(user=user)
        except Wishlist.DoesNotExist:
            return Response({"message": "User has no wishlist"}, status=404)

        serializer = self.get_serializer(wishlist)
        return Response(serializer.data)

class WishlistCreateView(generics.CreateAPIView):
    queryset = Wishlist.objects.all()
    serializer_class = WishlistSerializer
    permission_classes = [IsAuthenticated]
    authentication_classes = [SessionAuthentication, TokenAuthentication]

    def create(self, request, *args, **kwargs):
        user = request.user
        wishlist, created = Wishlist.objects.get_or_create(user=user)
        product_ids = request.data.get('products')
        for id in product_ids:
            try:
                product = Product.objects.get(pk=id)
            except Product.DoesNotExist:
                return Response({"message":"Product Does not exist"}, status=404)
        wishlist.products.add(*product_ids)
        wishlist.save()
        serializer = self.get_serializer(wishlist)
        return Response(serializer.data, status=status.HTTP_201_CREATED)

class WishlistRemoveView(generics.CreateAPIView):
    queryset = Wishlist.objects.all()
    serializer_class = WishlistSerializer
    permission_classes = [IsAuthenticated]
    authentication_classes = [SessionAuthentication, TokenAuthentication]

    def create(self, request, *args, **kwargs):
        user = request.user
        wishlist, created = Wishlist.objects.get_or_create(user=user)
        product_ids = request.data.get('products')
        wishlist.products.remove(*product_ids)
        wishlist.save()
        serializer = self.get_serializer(wishlist)
        return Response(serializer.data, status=status.HTTP_201_CREATED)

class SearchView(generics.CreateAPIView):
    serializer_class = SearchSerializer

    def get_queryset(self):
        
        keyword = self.request.data.get('keyword')
        if keyword[0] == "@":
            queryset = Vendor.objects.filter(shop_name__icontains=keyword[1:])
           
        else:
            queryset = Product.objects.filter(title__icontains=keyword)
        return queryset

    def post(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        keyword = serializer.validated_data.get('keyword')
        queryset = self.get_queryset()
        if queryset.exists():
            if keyword[0] == "@":
                serialized_data = VendorSerializer(queryset, many=True).data
            else:
                serialized_data = ProductListSerializer(queryset, many=True).data
            return Response(serialized_data)
        
        else:
            return Response({"message": "No Products"}, status=404)
        