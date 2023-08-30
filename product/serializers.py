from rest_framework import serializers
from .models import Product, Category, ColorOption, SizeOption

class ProductListSerializer(serializers.ModelSerializer):
    class Meta:
        model = Product
        fields = ['id', 'title', 'price', 'main_image']

class ProductCategorySerializer(serializers.ModelSerializer):
    category = serializers.StringRelatedField()

    class Meta:
        model = Product
        fields = ['id', 'title', 'price', 'main_image', 'category']

class ProductDetailSerializer(serializers.ModelSerializer):
    category = serializers.StringRelatedField()
    vendor = serializers.StringRelatedField()
    colors = serializers.StringRelatedField(many=True)
    sizes = serializers.StringRelatedField(many=True)

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
    product_id = serializers.IntegerField()

