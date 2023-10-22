from django.urls import path
from .views import *

urlpatterns = [
    # Your other URL patterns
    path('create-vendor/', CreateVendor.as_view(), name='create-vendor'),
    path('create-product/', CreateProductView.as_view(), name='create-product'),
    path('list-products', ListVendorProducts.as_view(), name='list-products'),
    path('product/update/<int:pk>/', UpdateProductView.as_view(), name='update-product'),
    path('product/delete/<int:pk>/', DeleteProductView.as_view(), name='delete-product'),
]
