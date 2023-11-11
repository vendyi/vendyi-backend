from vendors.models import Vendor
from accounts.models import User
from django.db import models
from django.utils.text import slugify

class ColorOption(models.Model):
    color = models.CharField(max_length=50)

    def __str__(self):
        return self.color
    
class SizeOption(models.Model):
    size = models.CharField(max_length=50)

    def __str__(self):
        return self.size

class Category(models.Model):
    title = models.CharField(max_length=100)
    slug = models.SlugField(unique=True)
    image = models.ImageField(upload_to='media/category/', null=True, blank=True)
    
    class Meta:
        verbose_name_plural = 'Categories'

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.title)
        super().save(*args, **kwargs)

    def __str__(self):
        return self.title

class Product(models.Model):
    title = models.CharField(max_length=100)
    price = models.DecimalField(max_digits=10, decimal_places=2)
    main_image = models.ImageField(upload_to='media/products/')
    additional_images = models.JSONField(null=True, blank=True)  # If using PostgreSQL
    description = models.TextField()
    category = models.ForeignKey(Category, on_delete=models.CASCADE)
    vendor = models.ForeignKey(Vendor, on_delete=models.CASCADE)
    date_added = models.DateTimeField(auto_now_add=True)
    in_stock = models.BooleanField(default=True)
    amount_in_stock = models.DecimalField(max_digits=5, decimal_places=2, blank=True, null=True)
    discount_percentage = models.DecimalField(default=0,max_digits=5, decimal_places=2, blank=True, null=True)
    discount_start_date = models.DateField(blank=True, null=True)
    discount_end_date = models.DateField(blank=True, null=True)
    colors = models.ManyToManyField(ColorOption, blank=True)
    sizes = models.ManyToManyField(SizeOption, blank=True)
    likes = models.DecimalField(default=0, max_digits=10, decimal_places=2)

    def increment_likes(self):
        self.likes += 1
        self.save()

    def decrement_likes(self):
        if self.likes > 0:
            self.likes -= 1
            self.save()
    
    def __str__(self):
        return self.title

class ProductComment(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    text = models.TextField()
    timestamp = models.DateTimeField(auto_now_add=True)
    is_vendor_comment = models.BooleanField(default=False) 
    
    def __str__(self):
        return self.text
    # Vendor-specific comment

class CommentReply(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    comment = models.ForeignKey(ProductComment, on_delete=models.CASCADE)
    text = models.TextField()
    timestamp = models.DateTimeField(auto_now_add=True)
    is_vendor_comment = models.BooleanField(default=False)
    class Meta:
        verbose_name_plural = 'Comment Replies'
    def __str__(self):
        return self.text

class Wishlist(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    products = models.ManyToManyField(Product, related_name='wishlists')

    def __str__(self):
        return f"Wishlist for {self.user.username}"

class RecentlyViewed(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    timestamp = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ['user', 'product']
    def __str__(self):
        return f'{self.user.username} just viewed {self.product}'