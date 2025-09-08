from django.contrib.auth.models import AbstractUser
from django.db import models


class CustomUser(AbstractUser):
    is_customer = models.BooleanField(default=False)

class CustomerProfile(models.Model):
    user = models.OneToOneField(CustomUser, on_delete=models.CASCADE , related_name="customer_profile")
    first_name = models.CharField(max_length=255, blank=True)
    last_name = models.CharField(max_length=255, blank=True)
    contact = models.CharField(max_length=15, blank=True)
    
    def __str__(self):
        return f"Customer: {self.user.username}"
    
    

class Note(models.Model):
    description = models.CharField(max_length=300)
    user = models.ForeignKey(CustomUser , on_delete=models.CASCADE , related_name="notes")
    def __str__(self):
        return f"Notes of : {self.user}"

class Product(models.Model):
    name = models.CharField(max_length=255)
    brand = models.CharField(max_length=100)
    prevprice = models.DecimalField(max_digits=10, decimal_places=2)
    newprice = models.DecimalField(max_digits=10, decimal_places=2)
    material = models.CharField(max_length=100, blank=True, null=True)
    color = models.CharField(max_length=50, blank=True, null=True)
    stock = models.PositiveIntegerField(default=0)
    category = models.CharField(max_length=100)
    subCategory = models.CharField(max_length=100, blank=True, null=True)
    description = models.TextField(blank=True, null=True)
    date = models.DateTimeField(auto_now_add=True)
    bestseller = models.BooleanField(default=False)
    
    def __str__(self):
        return f"{self.name}"

class ProductImage(models.Model):
    product = models.ForeignKey(Product, related_name="images", on_delete=models.CASCADE)
    url = models.URLField()
    def __str__(self):
        return f"url for {self.product}"

class ProductSize(models.Model):
    product = models.ForeignKey(Product, related_name="sizes", on_delete=models.CASCADE)
    size = models.IntegerField()
