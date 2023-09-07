from django.db import models
from django.contrib.auth.models import User
from product.models import Product
from cart.models import Cart
""" 
Modify these and make them work with the user model u may create 
These codes just handle recently viewed items with a basic user profile doe users.
"""
class RecentlyViewed(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    timestamp = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ['user', 'product']
    def __str__(self):
        return f'{self.user.username} just viewed {self.product}'
    
class UserProfile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    recently_viewed = models.ManyToManyField(RecentlyViewed, blank=True)
    cart = models.OneToOneField(Cart, on_delete=models.CASCADE, blank=True, null=True)
    def __str__(self):
        return self.user.username
    
