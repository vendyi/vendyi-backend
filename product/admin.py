from django.contrib import admin
from .models import *
# Register your models here.
@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    '''Admin View for Product'''

    list_display = ('title','price','category','vendor', 'main_image')
    list_filter = ('vendor','price','category','in_stock')
    search_fields = ('title','vendor', 'category')

@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    '''Admin View for Category'''

    list_display = ('title','slug','image')
    search_fields = ('title',)
