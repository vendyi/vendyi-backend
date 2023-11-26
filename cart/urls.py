from django.urls import path
from .views import *

urlpatterns = [
    # Other URL patterns
    path('add/', AddToCartView.as_view(), name='add-to-cart'),
    path('promo-code/', ApplyPromoCodeView.as_view(), name='apply-promo-code'),
    path('remove/<int:product_id>/', RemoveFromCartView.as_view(), name='remove-from-cart'),
    path('delete/<int:product_id>/', DeleteFromCartView.as_view(), name='delete-from-cart'),
    path('', CartView.as_view(), name='view-cart'),
]
