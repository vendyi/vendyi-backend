from django.contrib import admin
from .models import *
# Register your models here.
admin.site.register([VendorProfile, Promo_Code, Wallet, Transaction])
@admin.register(Vendor)
class VendorAdmin(admin.ModelAdmin):
    def pin_display(self, obj):
        return "****"  # or any other placeholder
    pin_display.short_description = 'PIN'

    list_display = ('shop_name', 'pin_display', 'location', 'is_active')
@admin.register(VendorActiveHours)
class VendorActiveHoursAdmin(admin.ModelAdmin):
    list_display = ['vendor', 'day_of_week', 'start_time', 'end_time', 'is_active']
