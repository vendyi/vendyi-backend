from django.contrib import admin
from .models import *
# Register your models here.
class ProductColorInline(admin.TabularInline):
    model = ProductColor
    extra = 1  # Number of extra forms to display

# Inline admin for ProductSize
class ProductSizeInline(admin.TabularInline):
    model = ProductSize
    extra = 1
@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    '''Admin View for Product'''
    inlines = [ProductColorInline, ProductSizeInline] 
    list_display = ('title','price','category','vendor', 'in_stock')
    list_filter = ('vendor','price','category','in_stock')
    search_fields = ('title','vendor', 'category')

@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    '''Admin View for Category'''
    prepopulated_fields = {'slug': ('title',)}
    list_display = ('title','slug','image')
    search_fields = ('title',)

# Admin model for Product 
admin.site.register([ColorOption, SizeOption, ProductComment, CommentReply, Wishlist, ProductColor, ProductSize])
