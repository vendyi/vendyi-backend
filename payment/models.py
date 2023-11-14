from django.db import models
from .utils import generate_order_number
from product.models import *
from django.conf import settings
from product.models import Product
class Order(models.Model):
    # Assuming you have a User model for customers
    # Choices for order status
    ORDER_STATUS_CHOICES = [
        (0, 'Pending'),
        (1, 'Shipped'),
        (2, 'Delivered'),
        (3, 'Cancelled'),
    ]
    customer = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    total_price = models.DecimalField(max_digits=10, decimal_places=2)
    status = models.IntegerField(choices=ORDER_STATUS_CHOICES, default=0)
    paid = models.BooleanField(default=False)
    # Add more fields as needed, such as shipping address, payment details, etc.
    order_number = models.CharField(max_length=50,unique=True)
    def save(self, *args, **kwargs):
        if not self.order_number:
            # Generate order number only if it doesn't exist
            self.order_number = generate_order_number()
        super(Order, self).save(*args, **kwargs)
    def __str__(self):
        return f"Order {self.id} by {self.customer}"

class OrderItem(models.Model):
    order = models.ForeignKey(Order, related_name='items', on_delete=models.CASCADE)
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    color = models.CharField(max_length=50, blank=True, null=True)
    size = models.CharField(max_length=50, blank=True, null=True)
    quantity = models.IntegerField()
    price = models.DecimalField(max_digits=10, decimal_places=2)

    def __str__(self):
        return f"{self.quantity} of {self.product.title}"


class SavedPayment(models.Model):
    Card_choices = ((0,"Visa Card"),(1,'Mastercard'), (2,"Gh-Link"), (3,"Other"))
    momo_choices = ((0,"MTN"),(1,'Vodafone'), (2,"Airtel-Tigo"), (3,"Other"))
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='payment_user')
    card = models.BooleanField(default=False)
    momo = models.BooleanField(default=False)
    card_number = models.CharField(max_length=50, blank=True, null=True)
    card_exp = models.CharField(max_length=50, blank=True, null=True)
    card_type = models.IntegerField(choices=Card_choices, blank=True, null=True)
    momo_type = models.IntegerField(choices=momo_choices, blank=True, null=True)
    momo_number = models.CharField(max_length=50, blank=True, null=True)
    def __str__(self):
        return f'{self.user}'