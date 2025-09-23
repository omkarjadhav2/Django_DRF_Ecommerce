from rest_framework import serializers
from .models import CustomUser,CustomerProfile , Note , Product , ProductImage , Size , Address, Product, Cart, CartItem, Order, OrderItem, Payment


class CustomerRegisterSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True)
    first_name = serializers.CharField(write_only=True, required=False)
    last_name = serializers.CharField(write_only=True, required=False)
    contact = serializers.CharField(write_only=True, required=False)

    class Meta:
        model = CustomUser
        fields = ("username", "email", "password", "first_name", "last_name", "contact")

    def create(self, validated_data):
        password = validated_data.pop("password")
        first_name = validated_data.pop("first_name", "")
        last_name = validated_data.pop("last_name", "")
        contact = validated_data.pop("contact", "")

        user = CustomUser.objects.create_user(
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

class CustomerProfileSerializer(serializers.ModelSerializer):
    class Meta:
        model = CustomerProfile
        fields = ['first_name', 'last_name', 'contact']
        

class AddressSerializer(serializers.ModelSerializer):
    class Meta:
        model = Address
        exclude = ["user"]  

    def create(self, validated_data):
        return Address.objects.create(**validated_data)

        
        
class UserProfileSerializer(serializers.ModelSerializer):
    addresses = AddressSerializer(many=True, read_only=True)
    customer_profile = CustomerProfileSerializer(read_only=True)
    class Meta:
        model = CustomUser
        fields = ['id', 'username', 'email', 'is_customer',"customer_profile","addresses"]
        

class NoteSerializer(serializers.ModelSerializer):
    class Meta:
        model = Note
        fields = ['id', 'description']

class ImageSerializer(serializers.ModelSerializer):
    class Meta:
        model = ProductImage
        fields = ["url"]
        
class SizeSerializer(serializers.ModelSerializer):
    class Meta:
        model = Size
        fields = ["id", "value"]
        extra_kwargs = {
            "value": {"validators": []},  
        }

class ProductSerializer(serializers.ModelSerializer):
    images = ImageSerializer(many=True)
    sizes = SizeSerializer(many=True)
    
    class Meta:
        model = Product
        fields = ["id", "name", "brand", "prevprice", "newprice", "category",
                  "images","material","color","stock","subCategory","bestseller","description","sizes"]
        
    def create(self, validated_data):
        print("before:" , validated_data)
        sizes_data = validated_data.pop("sizes", [])

        images_data = validated_data.pop("images", [])
        print("after :" , validated_data)
        product = Product.objects.create(**validated_data)
        
        for size in sizes_data:
            size_obj, _ = Size.objects.get_or_create(value=size["value"])
            product.sizes.add(size_obj)

        for img in images_data:
            ProductImage.objects.create(product=product, **img)
        return product
    

class CartItemSerializer(serializers.ModelSerializer):
    product = ProductSerializer(read_only=True)   # for response
    product_id = serializers.PrimaryKeyRelatedField(
        queryset=Product.objects.all(), write_only=True
    )

    class Meta:
        model = CartItem
        fields = ["id", "product", "product_id", "size", "quantity"]

    def create(self, validated_data):
        product = validated_data.pop("product_id")
        cart_item = CartItem.objects.create(product=product, **validated_data)
        return cart_item



class CartSerializer(serializers.ModelSerializer):
    items = CartItemSerializer(many=True, read_only=True)

    class Meta:
        model = Cart
        fields = ["id", "user", "items", "created_at", "updated_at"]


class OrderItemSerializer(serializers.ModelSerializer):
    product = ProductSerializer(read_only=True)

    class Meta:
        model = OrderItem
        fields = ["id", "product", "quantity", "price_at_purchase"]


class OrderSerializer(serializers.ModelSerializer):
    items = OrderItemSerializer(many=True, read_only=True)
    address = AddressSerializer(read_only=True)

    class Meta:
        model = Order
        fields = [
            "id",
            "user",
            "address",
            "total_amount",
            "payment_method",
            "payment_status",
            "order_status",
            "items",
            "created_at",
            "updated_at",
        ]


class PaymentSerializer(serializers.ModelSerializer):
    order = OrderSerializer(read_only=True)

    class Meta:
        model = Payment
        fields = "__all__"