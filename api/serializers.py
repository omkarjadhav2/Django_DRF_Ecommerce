from rest_framework import serializers
from .models import CustomUser,CustomerProfile , Note , Product , ProductSize , ProductImage
from django.contrib.auth import get_user_model

User = get_user_model()

class CustomerRegisterSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True)
    first_name = serializers.CharField(write_only=True, required=False)
    last_name = serializers.CharField(write_only=True, required=False)
    contact = serializers.CharField(write_only=True, required=False)

    class Meta:
        model = User
        fields = ("username", "email", "password", "first_name", "last_name", "contact")

    def create(self, validated_data):
        password = validated_data.pop("password")
        first_name = validated_data.pop("first_name", "")
        last_name = validated_data.pop("last_name", "")
        contact = validated_data.pop("contact", "")

        user = User.objects.create_user(
            username=validated_data["username"],
            email=validated_data["email"],
            password=password,
            is_customer=True,
        )
        CustomerProfile.objects.create(
            user=user,
            first_name=first_name,
            last_name=last_name,
            contact=contact,
        )
        return user



class UserProfileSerializer(serializers.ModelSerializer):
    class Meta:
        model = CustomUser
        fields = ['id', 'username', 'email', 'is_customer']
        

class NoteSerializer(serializers.ModelSerializer):
    class Meta:
        model = Note
        fields = ['id', 'description']

class ImageSerializer(serializers.ModelSerializer):
    class Meta:
        model = ProductImage
        fields = ["url"]

class ProductSerializer(serializers.ModelSerializer):
    images = ImageSerializer(many=True)
    
    class Meta:
        model = Product
        fields = ["id", "name", "brand", "prevprice", "newprice", "category", "images"]
        
    def create(self, validated_data):
        print("before:" , validated_data)
        images_data = validated_data.pop("images", [])
        print("after :" , validated_data)
        product = Product.objects.create(**validated_data)
        for img in images_data:
            ProductImage.objects.create(product=product, **img)
        return product
    
