from django.db import models
from django.core.validators import URLValidator, validate_image_file_extension
from accounts.models import User
from django.db.models.signals import post_save
from django.dispatch import receiver
from django.utils import timezone
from django.core.exceptions import ValidationError

class Vendor(models.Model):
    '''Model definition for Vendor.'''
    momo_choices = ((0,"MTN"),(1,'Vodafone'), (2,"Airtel-Tigo"), (3,"Other"))
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name="is_vendor")
    #Contact Information
    email = models.EmailField(max_length=255,)
    phone_number = models.CharField(max_length=50)
    location = models.CharField(max_length=255)
    
    #Personal Information
    full_name = models.CharField(max_length=255)
    date_of_birth = models.DateField()
    ID_card = models.ImageField(upload_to='media/vendors/ID_cards', null=True, blank=True, validators=[validate_image_file_extension])
    
    #Shop Information
    shop_name = models.CharField(max_length=255, unique=True)
    product_or_service = models.CharField(max_length=255)
    description = models.TextField(max_length=500)
    website = models.URLField(validators=[URLValidator()], blank=True, null=True)
    
    #Payment Information
    momo_number = models.CharField(max_length=50)
    momo_type = models.IntegerField(choices=momo_choices)
    
    #Security Information
    pin = models.CharField(max_length=5)
    security_question = models.CharField(max_length=255)
    security_answer = models.CharField(max_length=255)
    
    #Other Information
    is_active = models.BooleanField(default=False)
    date_joined = models.DateTimeField(auto_now_add= True)



    class Meta:
        '''Meta definition for Vendor.'''
        verbose_name = 'Vendor'
        verbose_name_plural = 'Vendors'

    def __str__(self):
        return self.shop_name
    
class VendorProfile(models.Model):
    vendor = models.OneToOneField(Vendor, on_delete=models.CASCADE)
    image = models.ImageField(upload_to='media/vendors/profiles', default='media/profile.jpeg', validators=[validate_image_file_extension])
    header_image = models.ImageField(upload_to='media/vendors/headers', validators=[validate_image_file_extension])
    followers = models.ManyToManyField(User, related_name='following', blank=True,)

    def __str__(self):
        return self.vendor.shop_name

class VendorActiveHours(models.Model):

    vendor = models.ForeignKey('Vendor', on_delete=models.CASCADE)
    day_of_week = models.IntegerField(choices=[(0, 'Sunday'), (1, 'Monday'), (2, 'Tuesday'), (3, 'Wednesday'), (4, 'Thursday'), (5, 'Friday'), (6, 'Saturday')])
    start_time = models.TimeField()
    end_time = models.TimeField()
    is_active = models.BooleanField(default=True)

    class Meta:
        unique_together = ('vendor', 'day_of_week', 'start_time', 'end_time')
        
    def clean(self):
        # Validation to ensure start_time is before end_time
        if self.start_time >= self.end_time:
            raise ValidationError("End time must be after start time")

        # Validation to prevent overlapping times
        overlapping_times = VendorActiveHours.objects.filter(
            vendor=self.vendor,
            day_of_week=self.day_of_week,
            start_time__lt=self.end_time,
            end_time__gt=self.start_time
        ).exclude(id=self.id)
        if overlapping_times.exists():
            raise ValidationError("Overlapping active hours for the same day are not allowed.")
    def __str__(self):
        return f"{self.vendor.shop_name} - {self.get_day_of_week_display()} ({self.start_time} to {self.end_time})"
   
#this signal automatically creates a vendor profile when a vendor is created.
@receiver(post_save, sender=Vendor)
def create_vendor_profile(sender, instance, created, **kwargs):
    if created and not hasattr(instance, 'VendorProfile'):
        VendorProfile.objects.create(vendor=instance)
    
class Promo_Code(models.Model):
    vendor = models.ForeignKey(Vendor, on_delete=models.CASCADE)
    code = models.CharField(max_length=255, unique=True)
    discount_percentage = models.DecimalField(max_digits=5, decimal_places=2)
    discount_start_date = models.DateField(blank=True, null=True)
    discount_end_date = models.DateField(blank=True, null=True)
    is_active = models.BooleanField(default=True)  
    date_created = models.DateTimeField(auto_now_add=True)
    def __str__(self):
        return self.code

class Wallet(models.Model):
    vendor = models.OneToOneField(Vendor, on_delete=models.CASCADE, related_name='wallet')
    total_balance = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    available_balance = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    pending_balance = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    def add_pending_balance(self, amount):
        self.pending_balance += amount
        self.total_balance += amount
        self.save()

    def make_balance_available(self, transaction):
        if transaction.status == Transaction.PENDING:
            self.available_balance += transaction.amount
            self.pending_balance -= transaction.amount
            transaction.status = Transaction.AVAILABLE
            transaction.cleared_at = timezone.now()
            transaction.save()
            self.save()
    def __str__(self):
        return f"Wallet for {self.vendor.id} - Total: {self.total_balance}, Available: {self.available_balance}"

class Transaction(models.Model):
    CREDIT = 'credit'
    DEBIT = 'debit'
    TRANSACTION_TYPE_CHOICES = [
        (CREDIT, 'Credit'),
        (DEBIT, 'Debit'),
    ]

    PENDING = 'pending'
    AVAILABLE = 'available'
    COMPLETED = 'completed'
    STATUS_CHOICES = [
        (PENDING, 'Pending'),
        (AVAILABLE, 'Available'),
        (COMPLETED, 'Completed'),
    ]

    vendor = models.ForeignKey(Vendor, on_delete=models.CASCADE, related_name='transactions')
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    transaction_type = models.CharField(max_length=6, choices=TRANSACTION_TYPE_CHOICES)
    status = models.CharField(max_length=9, choices=STATUS_CHOICES, default=PENDING)
    created_at = models.DateTimeField(default=timezone.now)
    cleared_at = models.DateTimeField(null=True, blank=True)

    def __str__(self):
        return f"Transaction {self.id} - {self.transaction_type} - {self.status}"