from rest_framework import serializers
from .models import CustomUser,CustomerProfile,SellerProfile

class CustomerRegisterSerializer(serializers.ModelSerializer):
    password2 = serializers.CharField(write_only=True)
    first_name = serializers.CharField(write_only=True, required=False)
    last_name = serializers.CharField(write_only=True, required=False)
    contact = serializers.CharField(write_only=True, required=False)

    class Meta:
        model = CustomUser
        fields = ['username', 'email', 'password', 'password2','first_name', 'last_name','contact']
        extra_kwargs = {
            'password': {'write_only': True}
        }

    def validate(self, data):
        if data['password'] != data['password2']:
            raise serializers.ValidationError('Passwords do not match')
        return data

    def create(self, validated_data):
        validated_data.pop('password2') 
        first_name = validated_data.pop('first_name', '')
        last_name = validated_data.pop('last_name', '')
        contact = validated_data.pop('contact', '')
        
        user = CustomUser.objects.create_user(
            username=validated_data['username'],
            email=validated_data['email'],
            password=validated_data['password'],
            is_customer = True
            
        )
        CustomerProfile.objects.create(user=user ,first_name=first_name,
            last_name=last_name , contact = contact)
        return user
    
class SellerRegisterSerializer(serializers.ModelSerializer):
    password2 = serializers.CharField(write_only=True)
    first_name = serializers.CharField(write_only=True, required=False)
    last_name = serializers.CharField(write_only=True, required=False)
    contact = serializers.CharField(write_only=True, required=False)
    store_name = serializers.CharField(write_only=True, required=False)
    gst_number = serializers.CharField(write_only=True, required=False)    

    class Meta:
        model = CustomUser
        fields = ['username', 'email', 'password', 'password2','first_name', 'last_name','contact' , 'store_name','gst_number']
        extra_kwargs = {
            'password': {'write_only': True}
        }

    def validate(self, data):
        if data['password'] != data['password2']:
            raise serializers.ValidationError('Passwords do not match')
        return data

    def create(self, validated_data):
        validated_data.pop('password2') 
        first_name = validated_data.pop('first_name', '')
        last_name = validated_data.pop('last_name', '')
        contact = validated_data.pop('contact', '')
        store_name = validated_data.pop('store_name', '')
        gst_number = validated_data.pop('gst_number', '')
        
        user = CustomUser.objects.create_user(
            username=validated_data['username'],
            email=validated_data['email'],
            password=validated_data['password'],
            is_seller = True
            
        )
        SellerProfile.objects.create(user=user ,first_name=first_name,
            last_name=last_name , contact = contact , store_name = store_name , gst_number = gst_number)
        return user
