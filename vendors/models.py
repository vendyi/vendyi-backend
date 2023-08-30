from django.db import models
from django.contrib.auth.models import User

# Create your models here.
class Vendor(models.Model):
    '''Model definition for Vendor.'''
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    name = models.CharField(max_length=255)

    class Meta:
        '''Meta definition for Vendor.'''

        verbose_name = 'Vendor'
        verbose_name_plural = 'Vendors'

    def __str__(self):
        return self.user.username