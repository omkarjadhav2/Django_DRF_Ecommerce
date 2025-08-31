from rest_framework import serializers
from .models import CustomUser,CustomerProfile,SellerProfile , Note
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


class SellerRegisterSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True)
    first_name = serializers.CharField(write_only=True, required=False)
    last_name = serializers.CharField(write_only=True, required=False)
    contact = serializers.CharField(write_only=True, required=False)
    store_name = serializers.CharField(write_only=True)   # extra field
    gst_number = serializers.CharField(write_only=True, required=False, allow_blank=True, allow_null=True)

    class Meta:
        model = User
        fields = (
            "username",
            "email",
            "password",
            "first_name",
            "last_name",
            "contact",
            "store_name",
            "gst_number",
        )

    def create(self, validated_data):
        password = validated_data.pop("password")
        store_name = validated_data.pop("store_name")
        gst_number = validated_data.pop("gst_number", "")
        first_name = validated_data.pop("first_name", "")
        last_name = validated_data.pop("last_name", "")
        contact = validated_data.pop("contact", "")

        user = User.objects.create_user(
            username=validated_data["username"],
            email=validated_data["email"],
            password=password,
            is_seller=True,
        )

        SellerProfile.objects.create(
            user=user,
            first_name=first_name,
            last_name=last_name,
            contact=contact,
            store_name=store_name,
            gst_number=gst_number,
        )
        return user


class UserProfileSerializer(serializers.ModelSerializer):
    class Meta:
        model = CustomUser
        fields = ['id', 'username', 'email', 'is_customer', 'is_seller']
        

class NoteSerializer(serializers.ModelSerializer):
    class Meta:
        model = Note
        fields = ['id', 'description']
        