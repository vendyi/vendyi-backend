from django.db import models
from django.core.validators import URLValidator, validate_image_file_extension
from account.models import User
from django.db.models.signals import post_save
from django.dispatch import receiver

class ActiveVendorManager(models.Manager):
    def get_queryset(self):
        return super().get_queryset().filter(is_active=True)

class Vendor(models.Model):
    '''Model definition for Vendor.'''
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    shop_name = models.CharField(max_length=255)
    description = models.TextField(max_length=500)
    location = models.CharField(max_length=255)
    phone_number = models.CharField(max_length=50)
    website = models.URLField(validators=[URLValidator()])
    ID_card = models.ImageField(upload_to='media/vendors/ID_cards', null=True, blank=True, validators=[validate_image_file_extension])
    is_active = models.BooleanField(default=False)
    date_joined = models.DateTimeField(auto_now_add= True)

    active_vendors = ActiveVendorManager()  # custom manager

    class Meta:
        '''Meta definition for Vendor.'''
        verbose_name = 'Vendor'
        verbose_name_plural = 'Vendors'

    def __str__(self):
        return self.user.username
    
class VendorProfile(models.Model):
    vendor = models.OneToOneField(Vendor, on_delete=models.CASCADE)
    image = models.ImageField(upload_to='media/vendors/profiles', default='media/profile.jpeg', validators=[validate_image_file_extension])
    header_image = models.ImageField(upload_to='media/vendors/headers', validators=[validate_image_file_extension])
    followers = models.ManyToManyField(User, related_name='following', default='media/profile.jpeg',)

    def __str__(self):
        return self.vendor.shop_name
    
#this signal automatically creates a vendor profile when a vendor is created.
@receiver(post_save, sender=Vendor)
def create_vendor_profile(sender, instance, created, **kwargs):
    if created and not hasattr(instance, 'VendorProfile'):
        VendorProfile.objects.create(vendor=instance)
    