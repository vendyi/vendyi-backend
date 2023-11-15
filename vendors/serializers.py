from rest_framework import serializers
from .models import *
from product.models import Product, ProductColor, ProductSize

class ProductColorSerializer(serializers.ModelSerializer):
    class Meta:
        model = ProductColor
        fields = ['color', 'is_in_stock']

class ProductSizeSerializer(serializers.ModelSerializer):
    class Meta:
        model = ProductSize
        fields = ['size', 'is_in_stock']
        
class VendorSerializer(serializers.ModelSerializer):
    number_of_products = serializers.SerializerMethodField()
    momo_type = serializers.CharField(source='get_momo_type_display')
    number_of_followers = serializers.SerializerMethodField()
    class Meta:
        model = Vendor
        fields = [
            'id', 'shop_name', 'product_or_service', 'description', 'website', 
            'momo_number', 'momo_type', 'number_of_products', 'is_active', 
            'date_joined', 'email', 'phone_number', 'location', 'number_of_followers',
        ]
        read_only_fields = ['is_active', 'number_of_products']
    def get_number_of_followers(self, obj):
        return VendorProfile.objects.get(vendor=obj).followers.count()
    def get_number_of_products(self, obj):
        return Product.objects.filter(vendor=obj).count()

class VendorProfileSerializer(serializers.ModelSerializer):
    vendor = VendorSerializer()
    class Meta:
        model = VendorProfile
        fields = '__all__'

class VendorProfileUpdateSerializer(serializers.ModelSerializer):
    class Meta:
        model = VendorProfile
        fields = '__all__'

class ProductCreateSerializer(serializers.ModelSerializer):
    colors = ProductColorSerializer(source='productcolor_set', many=True)
    sizes = ProductSizeSerializer(source='productsize_set', many=True)
    main_image = serializers.ImageField(required=False)
    class Meta:
        model = Product
        fields = '__all__'
        read_only_fields = ["vendor","likes","discount_percentage","discount_start_date","discount_end_date","in_stock","vendor_price"]
        
    def create(self, validated_data):
        colors_data = validated_data.pop('productcolor_set')
        sizes_data = validated_data.pop('productsize_set')
        product = Product.objects.create(**validated_data)
        for color_data in colors_data:
            ProductColor.objects.create(product=product, **color_data)
        for size_data in sizes_data:
            ProductSize.objects.create(product=product, **size_data)
        return product
    
class VendorActiveHoursSerializer(serializers.ModelSerializer):
    class Meta:
        model = VendorActiveHours
        fields = ['id', 'vendor', 'day_of_week', 'start_time', 'end_time', 'is_active']  

class VendorActiveHoursListSerializer(serializers.ModelSerializer):
    vendor = serializers.StringRelatedField()
    day_of_week = serializers.CharField(source='get_day_of_week_display')
    class Meta:
        model = VendorActiveHours
        fields = ['id', 'vendor', 'day_of_week', 'start_time', 'end_time', 'is_active']  
        
class PromoCodeSerializer(serializers.Serializer):
    code = serializers.CharField(max_length=255)
    discount_percentage = serializers.DecimalField(max_digits=5, decimal_places=2)
    discount_start_date = serializers.DateField(required=False)
    discount_end_date = serializers.DateField(required=False)

class PromocodeListSerializer(serializers.ModelSerializer):
    class Meta:
        model = Promo_Code
        fields = '__all__'
        read_only_fields = ['vendor']

class VendorFollowersSerializer(serializers.ModelSerializer):
    followers = serializers.SerializerMethodField()
    class Meta:
        model = VendorProfile
        fields = ['followers']
    def get_followers(self, obj):
        return[user.username for user in obj.followers.all()]

class ProductUpdateSerializer(serializers.ModelSerializer):
    title = serializers.CharField(required=False)
    price = serializers.DecimalField(max_digits=10, decimal_places=2, required=False)
    main_image = serializers.ImageField(required=False)
    additional_images = serializers.JSONField(required=False)  # If using PostgreSQL
    description = serializers.CharField(required=False)
    vendor_price = serializers.DecimalField(max_digits=10, decimal_places=2, required=False)
    colors = ProductColorSerializer(many=True, required=False)
    sizes = ProductSizeSerializer(many=True, required=False)
    class Meta:
        model = Product
        fields = '__all__'
        read_only_fields = ['vendor','vendor_price','likes','discount_percentage','discount_start_date','discount_end_date']
    
    
    def update(self, instance, validated_data):
        colors_data = validated_data.pop('colors', [])
        sizes_data = validated_data.pop('sizes', [])

        if 'final_price' in self.context:
            validated_data['price'] = self.context['final_price']

        # Update the non-relationship fields
        for attr, value in validated_data.items():
            setattr(instance, attr, value)
        instance.save()

        # Update colors
        for color_data in colors_data:
            color_id = color_data.get('color').id
            is_in_stock = color_data.get('is_in_stock')
            product_color, created = ProductColor.objects.update_or_create(
                product=instance, color_id=color_id, defaults={'is_in_stock': is_in_stock})

        # Update sizes
        for size_data in sizes_data:
            size_id = size_data.get('size').id
            is_in_stock = size_data.get('is_in_stock')
            product_size, created = ProductSize.objects.update_or_create(
                product=instance, size_id=size_id, defaults={'is_in_stock': is_in_stock})
        
        return instance

class VendorUpdateSerializer(serializers.ModelSerializer):
    shop_name = serializers.CharField(required=False)
    product_or_service = serializers.CharField(required=False)
    description = serializers.CharField(required=False)
    website = serializers.CharField(required=False)
    momo_number = serializers.CharField(required=False)
    momo_type = serializers.ChoiceField(choices=Vendor.momo_choices, required=False)
    email = serializers.EmailField(required=False)
    phone_number = serializers.CharField(required=False)
    location = serializers.CharField(required=False)
    security_question = serializers.CharField(required=False)
    pin = serializers.CharField(required=False)
    security_answer = serializers.CharField(required=False)
    full_name = serializers.CharField(required=False)
    date_of_birth = serializers.DateField(required=False)
    class Meta:
        model = Vendor
        fields = '__all__'
        read_only_fields = ['is_active', 'date_joined']
 
class VerifyVendorPinSerializer(serializers.Serializer):
    pin = serializers.CharField(max_length=5)
    
class TransactionSerializer(serializers.ModelSerializer):
    class Meta:
        model = Transaction
        fields = '__all__'
        read_only_fields = ['vendor']