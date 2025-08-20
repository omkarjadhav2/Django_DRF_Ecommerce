from django.contrib.auth.models import AbstractUser
from django.db import models


class CustomUser(AbstractUser):
    is_seller = models.BooleanField(default=False)
    is_customer = models.BooleanField(default=False)

class CustomerProfile(models.Model):
    user = models.OneToOneField(CustomUser, on_delete=models.CASCADE , related_name="customer_profile")
    first_name = models.CharField(max_length=255, blank=True)
    last_name = models.CharField(max_length=255, blank=True)
    contact = models.CharField(max_length=15, blank=True)
    
    def __str__(self):
        return f"Customer: {self.user.username}"
    
class SellerProfile(models.Model):
    user = models.OneToOneField(CustomUser, on_delete=models.CASCADE , related_name="seller_profile")
    first_name = models.CharField(max_length=255, blank=True)
    last_name = models.CharField(max_length=255, blank=True)
    contact = models.CharField(max_length=15, blank=True)
    store_name = models.CharField(max_length=150)
    gst_number = models.CharField(max_length=30, blank=True, null=True)
    verified = models.BooleanField(default=False)
    
    def __str__(self):
        return f"Seller: {self.store_name} ({self.user.username})"
    
    


