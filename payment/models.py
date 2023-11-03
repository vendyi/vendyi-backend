from django.db import models
from vendors.models import Vendor
from product.models import *
from django.conf import settings
# Create your models here.
class Order(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='order_user')
    product = models.ForeignKey(Product,  on_delete=models.CASCADE, blank=True, null=True)
    color = models.CharField(max_length=225,blank=True, null=True)
    amount = models.DecimalField(max_digits=100, decimal_places=2, blank=True, null=True)
    size = models.CharField(max_length=225,blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    paid = models.BooleanField(default=False)
    shipped = models.BooleanField(default=False)
    route = models.BooleanField(default=False)
    delivered = models.BooleanField(default=False)
    vendors = models.ManyToManyField(Vendor, related_name='orders',blank=True)
    
    def __str__(self):
        return f'{self.user.username}-paid:{self.paid}- for {self.product.title}'

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