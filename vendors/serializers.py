from rest_framework import serializers
from .models import *
from product.models import Product
class VendorSerializer(serializers.ModelSerializer):
    class Meta:
        model = Vendor
        fields = '__all__'
        read_only_fields = ['is_active']

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
    class Meta:
        model = Product
        fields = '__all__'
        read_only_fields = ["vendor"]
    
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
    
    class Meta:
        model = Product
        fields = '__all__'
        read_only_fields = ['vendor']
    
    def update(self, instance, validated_data):
        # Check if final_price is in the context and use it to update the price
        if 'final_price' in self.context:
            validated_data['price'] = self.context['final_price']
        
        # Perform the standard update
        return super().update(instance, validated_data)
  
class VerifyVendorPinSerializer(serializers.Serializer):
    pin = serializers.CharField(max_length=255)