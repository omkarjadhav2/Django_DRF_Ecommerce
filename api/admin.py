from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .models import CustomUser , CustomerProfile , Note , Product , ProductImage , Address , Cart, CartItem


   
    
class CartItemInline(admin.TabularInline):
    model = CartItem
    extra = 1
    
class AddressInline(admin.TabularInline):
    model = Address
    extra = 1
    
@admin.register(CustomUser)
class CustomUserAdmin(UserAdmin):
    model = CustomUser
    list_display = ['username', 'email', 'is_customer', 'is_staff']
    inlines = [AddressInline]
    
@admin.register(Cart)
class CartAdmin(admin.ModelAdmin):
    model = Cart
    inlines = [CartItemInline]


    

    
@admin.register(CustomerProfile)
class CustomerProfileAdmin(admin.ModelAdmin):
    list_display = ['first_name', 'last_name', 'contact']
   
    

    

@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    list_display = ['name', 'brand', 'stock','newprice']
    
    
        
admin.site.register(Note)
admin.site.register(ProductImage)
admin.site.register(Address)
admin.site.register(CartItem)
