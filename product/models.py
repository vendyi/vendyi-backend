from django.db import models
from vendors.models import Vendor
# Create your models here.
from django.db import models
from django.utils.text import slugify

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
    COLOR_CHOICES = [
        ('red', 'Red'),
        ('blue', 'Blue'),
        ('green', 'Green'),
        ('black', 'Black'),
        # Add more color options as needed
    ]
    
    SIZE_CHOICES = [
        ('small', 'Small'),
        ('medium', 'Medium'),
        ('large', 'Large'),
        ('xl', 'XL'),
        # Add more size options as needed
    ]
    title = models.CharField(max_length=100)
    price = models.DecimalField(max_digits=10, decimal_places=2)
    main_image = models.ImageField(upload_to='media/products/')
    additional_images = models.JSONField(null=True, blank=True)  # If using PostgreSQL
    description = models.TextField()
    category = models.ForeignKey(Category, on_delete=models.CASCADE)
    vendor = models.ForeignKey(Vendor, on_delete=models.CASCADE)
    date_added = models.DateTimeField(auto_now_add=True)
    in_stock = models.BooleanField(default=True)
    colors = models.CharField(max_length=20, choices=COLOR_CHOICES, null=True, blank=True)
    size = models.CharField(max_length=10, choices=SIZE_CHOICES, null=True, blank=True)
    
    def __str__(self):
        return self.title
