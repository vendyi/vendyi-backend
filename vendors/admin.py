from django.contrib import admin
from .models import *
# Register your models here.
admin.site.register([Vendor, VendorProfile, Promo_Code, Wallet, Transaction])

@admin.register(VendorActiveHours)
class VendorActiveHoursAdmin(admin.ModelAdmin):
    list_display = ['vendor', 'day_of_week', 'start_time', 'end_time', 'is_active']
