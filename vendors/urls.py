from django.urls import path
from .views import *

urlpatterns = [
    # Your other URL patterns
    path('create-vendor/', CreateVendor.as_view(), name='create-vendor'),
    path('create/promo-code/', CreatePromoCode.as_view(), name='create-promo'),
    path('create-product/', CreateProductView.as_view(), name='create-product'),
    path('list-products', ListVendorProducts.as_view(), name='list-products'),
    path('product/update/<int:pk>/', UpdateProductView.as_view(), name='update-product'),
    path('product/delete/<int:pk>/', DeleteProductView.as_view(), name='delete-product'),
    path('promo-codes/<int:pk>/terminate/', TerminatePromoCode.as_view(), name='terminate_promo_code'),
    path('promo-codes/list/', ListVendorPromoCodes.as_view(), name='list_promo_codes'),
    path("", VendorDetailView.as_view(), name="vendor-detail"),
    path("update-profile/", VendorProfileUpdateView.as_view(), name="update-profile"),
    path("add-follower/<int:pk>/", VendorAddFollowersView.as_view(), name="add-follower"),
]
