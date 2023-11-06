from django.contrib import admin
from .models import *
# Register your models here.
admin.site.register([Vendor, VendorProfile, Promo_Code, Wallet, Transaction])