from django_filters import rest_framework as filters
from .models import Product

class ProductFilter(filters.FilterSet):
    price_min = filters.NumberFilter(field_name="price", lookup_expr='gte')
    price_max = filters.NumberFilter(field_name="price", lookup_expr='lte')
    color = filters.CharFilter(field_name="colors", lookup_expr='icontains')
    size = filters.CharFilter(field_name="sizes", lookup_expr='icontains')
    vendor_location = filters.CharFilter(field_name="vendor__location", lookup_expr='icontains')

    class Meta:
        model = Product
        fields = ['price_min', 'price_max', 'color', 'size', 'vendor_location']