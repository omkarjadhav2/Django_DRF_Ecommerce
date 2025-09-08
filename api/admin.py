from django.contrib import admin
from .models import CustomUser
from django.contrib.auth.admin import UserAdmin
from .models import CustomUser , CustomerProfile , Note , Product , ProductImage , ProductSize


@admin.register(CustomUser)
class CustomUserAdmin(UserAdmin):
    model = CustomUser
    list_display = ['username', 'email', 'is_customer', 'is_staff']
    fieldsets = UserAdmin.fieldsets + (
        ('User Type', {'fields': ('is_seller', 'is_customer')}),
    )
    

    
@admin.register(CustomerProfile)
class SellerProfileAdmin(admin.ModelAdmin):
    list_display = ['first_name', 'last_name', 'contact']
    
    
admin.site.register(Note)
admin.site.register(Product)
admin.site.register(ProductImage)
admin.site.register(ProductSize)