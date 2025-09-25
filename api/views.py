from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework.permissions import IsAuthenticated, AllowAny , IsAdminUser
from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework.decorators import api_view , permission_classes
from django.contrib.auth import authenticate, get_user_model
from .serializers import  CustomerRegisterSerializer,UserProfileSerializer , NoteSerializer , ProductSerializer, AddressSerializer , CartItemSerializer , CartSerializer
from .models import Note , Product , Address , Cart , CartItem

User = get_user_model()


class CustomerRegisterView(APIView):
    permission_classes = [AllowAny]

    def post(self, request):
        serializer = CustomerRegisterSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response({"message": "Customer registered successfully"}, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class LogoutView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        try:
            refresh_token = request.data.get("refresh")
            token = RefreshToken(refresh_token)
            token.blacklist()
            return Response({"message": "Logged out successfully"}, status=status.HTTP_205_RESET_CONTENT)
        except Exception as e:
            return Response({"error": str(e)}, status=status.HTTP_400_BAD_REQUEST)





class ProfileView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        serializer = UserProfileSerializer(request.user)
        return Response(serializer.data, status=status.HTTP_200_OK)

    
@api_view(['GET'])
@permission_classes([IsAuthenticated])
def get_notes(request):
    user = request.user
    notes = Note.objects.filter(user = user)
    serializer = NoteSerializer(notes , many = True)
    return Response(serializer.data)
    
@api_view(['GET'])
@permission_classes([IsAuthenticated])
def is_logged_in(request):
    serializer = UserProfileSerializer(request.user, many=False)
    return Response(serializer.data)

class ProductUploadView(APIView):
    permission_classes = [IsAdminUser]

    def post(self, request):
        serializer = ProductSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response({"message": "product added succesfully"}, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

class ProductListView(APIView):
    permission_classes = [AllowAny]
    def get(self , request):
        products = Product.objects.all()
        serializer = ProductSerializer(products , many = True)
        return Response(serializer.data)
    
class AddressView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        addresses = Address.objects.filter(user=request.user)
        serializer = AddressSerializer(addresses, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)

    def post(self, request):
        serializer = AddressSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save(user=request.user)
            return Response({"message": "Address added successfully"}, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
class AddToCartView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        cart, _ = Cart.objects.get_or_create(user=request.user)
        items = CartItem.objects.filter(cart=cart)
        serializer = CartItemSerializer(items, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)

    def post(self, request):
        cart = Cart.objects.get(user=request.user)
        serializer = CartItemSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save(cart=cart)
            return Response(
                {"message": "Product added to cart successfully"},
                status=status.HTTP_201_CREATED,
            )
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def delete(self, request):
        product_id = request.data.get("product_id")
        size = request.data.get("size")  # optional, if your cart has size/variant

        if not product_id:
            return Response(
                {"error": "Product ID is required"},
                status=status.HTTP_400_BAD_REQUEST,
            )

        try:
            cart = Cart.objects.get(user=request.user)

            filters = {"cart": cart, "product_id": product_id}
            if size:
                filters["size"] = size

            item = CartItem.objects.filter(**filters).first()
            if not item:
                return Response(
                    {"error": "Item not found in cart"},
                    status=status.HTTP_404_NOT_FOUND,
                )

            item.delete()
            return Response(
                {"message": "Item removed from cart"},
                status=status.HTTP_200_OK,
            )

        except Cart.DoesNotExist:
            return Response(
                {"error": "Cart not found"}, status=status.HTTP_404_NOT_FOUND
            )

    def patch(self, request):
        product_id = request.data.get("product_id")
        size = request.data.get("size")  # optional if variants
        quantity = request.data.get("quantity")

        if not product_id or quantity is None:
            return Response(
                {"error": "Product ID and quantity are required"},
                status=status.HTTP_400_BAD_REQUEST,
            )

        try:
            cart = Cart.objects.get(user=request.user)

            filters = {"cart": cart, "product_id": product_id}
            if size:
                filters["size"] = size

            item = CartItem.objects.filter(**filters).first()
            if not item:
                return Response(
                    {"error": "Item not found in cart"},
                    status=status.HTTP_404_NOT_FOUND,
                )

            # If quantity is 0 or less, remove the item
            if int(quantity) <= 0:
                item.delete()
                return Response(
                    {"message": "Item removed from cart"},
                    status=status.HTTP_200_OK,
                )

            # Update quantity
            item.quantity = int(quantity)
            item.save()

            return Response(
                {"message": "Cart updated successfully"},
                status=status.HTTP_200_OK,
            )

        except Cart.DoesNotExist:
            return Response(
                {"error": "Cart not found"}, status=status.HTTP_404_NOT_FOUND
            )
