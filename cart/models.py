from django.db import models
from accounts.models import User
from product.models import Product
class Cart(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True)
    total_price = models.DecimalField(max_digits=10, decimal_places=2, default=0.00)
    def __str__(self):
        return f"Cart for {self.user.username}"

class CartItem(models.Model):
    cart = models.ForeignKey(Cart, on_delete=models.CASCADE)
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    quantity = models.PositiveIntegerField(default=1)
    color = models.CharField( max_length=50, blank=True, null=True)
    size = models.CharField( max_length=50, blank=True, null=True)
    def __str__(self):
        return f"{self.quantity} x {self.product.title}"