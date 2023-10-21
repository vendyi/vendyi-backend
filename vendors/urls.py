from django.urls import path
from .views import *

urlpatterns = [
    # Your other URL patterns
    path('create-vendor/', CreateVendor.as_view(), name='create-vendor'),
    path('create-product/', CreateProductView.as_view(), name='create-product'),
]
