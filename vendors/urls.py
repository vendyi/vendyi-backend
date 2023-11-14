from django.urls import path
from .views import *

urlpatterns = [
    # Your other URL patterns
    path('list/', VendorListView.as_view(), name='list-vendors'),
    path('create-vendor/', CreateVendor.as_view(), name='create-vendor'),
    path('create/promo-code/', CreatePromoCode.as_view(), name='create-promo'),
    path('create-product/', CreateProductView.as_view(), name='create-product'),
    path('list-products/', ListVendorProducts.as_view(), name='list-products'),
    path('product/update/<int:pk>/', UpdateProductView.as_view(), name='update-product'),
    path('product/delete/<int:pk>/', DeleteProductView.as_view(), name='delete-product'),
    path('promo-codes/<int:pk>/terminate/', TerminatePromoCode.as_view(), name='terminate_promo_code'),
    path('promo-codes/list/', ListVendorPromoCodes.as_view(), name='list_promo_codes'),
    path("<int:pk>/", VendorDetailView.as_view(), name="vendor-detail"),
    path("update/", VendorUpdateView.as_view(), name="vendor-update"),
    path("update-profile/", VendorProfileUpdateView.as_view(), name="update-profile"),
    path("add-follower/<int:pk>/", VendorAddFollowersView.as_view(), name="add-follower"),
    path("remove-follower/<int:pk>/", VendorRemoveFollowersView.as_view(), name="remove-follower"),
    path("followers/<int:pk>/", VendorFollowersView.as_view(), name="followers"),
    path("verify-pin/", VerifyVendorPinView.as_view(), name="verify-pin"),
    path('active-hours/create/', VendorActiveHoursCreateView.as_view(), name='vendor-active-hours-list-create'),
    path('active-hours/<int:pk>/', VendorActiveHoursListView.as_view(), name='vendor-active-hours-list'),
    path('active-hours/modify/<int:pk>/', VendorActiveHoursRetrieveUpdateDestroyView.as_view(), name='vendor-active-hours-detail'),
    path('analytics/', VendorAnalyticsView.as_view(), name='vendor_analytics'),
    path('wallet/', VendorWalletView.as_view(), name='vendor_wallet'),
    path('products/low-stock/', VendorLowStockProductsView.as_view(), name='low_stock_products'),
    path('orders/', VendorOrdersView.as_view(), name='vendor_orders'),
    path('transactions/', VendorTransactionListView.as_view(), name='vendor_transactions'),
]
