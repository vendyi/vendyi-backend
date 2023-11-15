from rest_framework import serializers
from .models import *
from vendors.serializers import VendorSerializer
from product.models import RecentlyViewed

class ProductColorSerializer(serializers.ModelSerializer):
    color = serializers.StringRelatedField()
    class Meta:
        model = ProductColor
        fields = ['color', 'is_in_stock']

class ProductSizeSerializer(serializers.ModelSerializer):
    size = serializers.StringRelatedField()
    class Meta:
        model = ProductSize
        fields = ['size', 'is_in_stock']
        
class ProductListSerializer(serializers.ModelSerializer):
    category = serializers.StringRelatedField()
    vendor = serializers.StringRelatedField()
    colors = ProductColorSerializer(source='productcolor_set', many=True)
    sizes = ProductSizeSerializer(source='productsize_set', many=True)
    class Meta:
        model = Product
        fields = "__all__"

class ProductCategorySerializer(serializers.ModelSerializer):
    category = serializers.StringRelatedField()
    vendor = serializers.StringRelatedField()
    colors = serializers.StringRelatedField(many=True, required=False)
    sizes = serializers.StringRelatedField(many=True, required=False)
    class Meta:
        model = Product
        fields = "__all__"

class ProductDetailSerializer(serializers.ModelSerializer):
    category = serializers.StringRelatedField()
    vendor = VendorSerializer()
    colors = ProductColorSerializer(source='productcolor_set', many=True)
    sizes = ProductSizeSerializer(source='productsize_set', many=True)
    class Meta:
        model = Product
        fields = '__all__'
       
class CategorySerializer(serializers.ModelSerializer):
    class Meta:
        model = Category
        fields = '__all__'

class DiscountSerializer(serializers.Serializer):
    product_id = serializers.IntegerField(required=False)
    category_id = serializers.IntegerField(required=False)
    discount_percentage = serializers.DecimalField(max_digits=5, decimal_places=2)
    discount_start_date = serializers.DateField(required=False)
    discount_end_date = serializers.DateField(required=False)
    
class TerminateDiscountSerializer(serializers.Serializer):
    product_id = serializers.IntegerField(required=False)
    category_id = serializers.IntegerField(required=False)

class RecentlyViewedSerializer(serializers.Serializer):
    product = serializers.StringRelatedField()
    class Meta:
        model = RecentlyViewed
        fields = '__all__'

class CommentReplySerializer(serializers.ModelSerializer):
    class Meta:
        model = CommentReply
        fields = '__all__'

class ProductCommentSerializer(serializers.ModelSerializer):
    replies = CommentReplySerializer(many=True, read_only=True)
    
    class Meta:
        model = ProductComment
        fields = '__all__'

class ProductCommentListSerializer(serializers.ModelSerializer):
    user = serializers.StringRelatedField()
    product = serializers.StringRelatedField()
    class Meta:
        model = ProductComment
        fields = "__all__"
        
class CommentReplyListSerializer(serializers.ModelSerializer):
    user = serializers.StringRelatedField()
    class Meta:
        model = ProductComment
        fields = ['id', 'user', 'text', 'is_vendor_comment']

class WishlistSerializer(serializers.ModelSerializer):
    
    class Meta:
        model = Wishlist
        fields = '__all__'
        
class SearchSerializer(serializers.Serializer):
    keyword = serializers.CharField(required=False)