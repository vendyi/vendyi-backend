from django.urls import path
from .views import *

urlpatterns = [
    # Other URL patterns
    path('saved-payment/create/', SavedPaymentCreateView.as_view(), name='saved-payment-create'),
    path('saved-payment/', SavedPaymentListView.as_view(), name='saved-payment-list'),
    path('saved-payment/<int:pk>/delete/', SavedPaymentDeleteView.as_view(), name='saved-payment-delete'),
    path('saved-payment/<int:pk>/update/', SavedPaymentUpdateView.as_view(), name='saved-payment-update'),
    path('', PaymentCreateAPIView.as_view(), name='pay'),

]
