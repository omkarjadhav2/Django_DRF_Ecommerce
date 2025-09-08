from django.contrib import admin
from .models import CustomUser
from django.contrib.auth.admin import UserAdmin
from .models import CustomUser , CustomerProfile , Note , Product , ProductImage , ProductSize


@admin.register(CustomUser)
class CustomUserAdmin(UserAdmin):
    model = CustomUser
    list_display = ['username', 'email', 'is_customer', 'is_staff']
    

    
@admin.register(CustomerProfile)
class CustomerProfileAdmin(admin.ModelAdmin):
    list_display = ['first_name', 'last_name', 'contact']
    

@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    list_display = ['name', 'brand', 'stock','newprice']
    
    
        
admin.site.register(Note)
admin.site.register(ProductImage)
admin.site.register(ProductSize)