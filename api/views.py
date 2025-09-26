from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework.permissions import IsAuthenticated, AllowAny , IsAdminUser
from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework.decorators import api_view , permission_classes
from django.contrib.auth import authenticate, get_user_model
from .serializers import  CustomerRegisterSerializer,UserProfileSerializer , NoteSerializer , ProductSerializer, AddressSerializer , CartItemSerializer , CartSerializer , OrderSerializer , PaymentSerializer
from .models import Note , Product , Address , Cart , CartItem
import razorpay
from decimal import Decimal
from django.conf import settings

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
        serializer = CartSerializer(cart)   # cart + nested items
        return Response(serializer.data, status=status.HTTP_200_OK)

    def post(self, request):
        cart, _ = Cart.objects.get_or_create(user=request.user)  # ✅ ensures cart exists
        serializer = CartItemSerializer(data=request.data)
        if serializer.is_valid():
            cart_item = serializer.save(cart=cart)
        # return updated cart so frontend can re-render from canonical source
            cart_ser = CartSerializer(cart)
            return Response(cart_ser.data, status=status.HTTP_201_CREATED)
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
            cart_ser = CartSerializer(cart)
            return Response(
                {"message": "Item removed from cart", "cart": cart_ser.data},
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
                cart_ser = CartSerializer(cart)
                return Response(
                    {"message": "Item removed from cart", "cart": cart_ser.data},
                    status=status.HTTP_200_OK,
                )

            # Update quantity
            item.quantity = int(quantity)
            item.save()

            cart_ser = CartSerializer(cart)
            return Response(
                {"message": "Cart updated successfully", "cart": cart_ser.data},
                status=status.HTTP_200_OK,
            )

        except Cart.DoesNotExist:
            return Response(
                {"error": "Cart not found"}, status=status.HTTP_404_NOT_FOUND
            )
            
# api/views.py  (add these imports at top of file)


# existing imports/models already in your file
from .models import Cart, CartItem, Address, Order, OrderItem, Payment

# Create Razorpay order (returns razorpay_order_id + amount + key_id)
class CreateRazorpayOrderView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        # get address_id from frontend (so we can attach when verifying)
        address_id = request.data.get("address_id")
        if not address_id:
            return Response({"error": "address_id is required"}, status=status.HTTP_400_BAD_REQUEST)

        try:
            cart = Cart.objects.get(user=request.user)
        except Cart.DoesNotExist:
            return Response({"error": "Cart not found"}, status=status.HTTP_404_NOT_FOUND)

        cart_items = CartItem.objects.filter(cart=cart)
        if not cart_items.exists():
            return Response({"error": "Cart is empty"}, status=status.HTTP_400_BAD_REQUEST)

        # compute total amount (use Decimal)
        total = Decimal("0")
        for item in cart_items:
            total += item.product.newprice * item.quantity

        # razorpay wants amount in paise (integer)
        amount_paise = int(total * 100)

        # create razorpay client
        client = razorpay.Client(auth=(settings.RAZORPAY_KEY_ID, settings.RAZORPAY_KEY_SECRET))

        # create razorpay order
        razorpay_order = client.order.create({
            "amount": amount_paise,
            "currency": "INR",
            "receipt": f"receipt_{request.user.id}_{cart.id}",
            "payment_capture": 1,   # 1 => auto capture
        })

        return Response({
            "razorpay_order_id": razorpay_order.get("id"),
            "amount": amount_paise,
            "currency": "INR",
            "key": settings.RAZORPAY_KEY_ID,
        }, status=status.HTTP_200_OK)


class VerifyRazorpayPaymentView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        data = request.data
        razorpay_payment_id = data.get("razorpay_payment_id")
        razorpay_order_id = data.get("razorpay_order_id")
        razorpay_signature = data.get("razorpay_signature")
        address_id = data.get("address_id")

        if not (razorpay_payment_id and razorpay_order_id and razorpay_signature and address_id):
            return Response({"error": "Missing required fields"}, status=status.HTTP_400_BAD_REQUEST)

        try:
            address = Address.objects.get(id=address_id, user=request.user)
        except Address.DoesNotExist:
            return Response({"error": "Address not found"}, status=status.HTTP_404_NOT_FOUND)

        client = razorpay.Client(auth=(settings.RAZORPAY_KEY_ID, settings.RAZORPAY_KEY_SECRET))

        try:
            client.utility.verify_payment_signature({
                'razorpay_order_id': razorpay_order_id,
                'razorpay_payment_id': razorpay_payment_id,
                'razorpay_signature': razorpay_signature
            })
        except razorpay.errors.SignatureVerificationError:
            return Response({"error": "Signature verification failed"}, status=status.HTTP_400_BAD_REQUEST)

        try:
            cart = Cart.objects.get(user=request.user)
        except Cart.DoesNotExist:
            return Response({"error": "Cart not found"}, status=status.HTTP_404_NOT_FOUND)

        cart_items = CartItem.objects.filter(cart=cart)
        if not cart_items.exists():
            return Response({"error": "Cart empty"}, status=status.HTTP_400_BAD_REQUEST)

        total = Decimal("0")
        for item in cart_items:
            total += item.product.newprice * item.quantity

        order = Order.objects.create(
            user=request.user,
            address=address,
            total_amount=total,
            payment_method="razorpay",
            payment_status="paid",
            order_status="processing",
        )

        for item in cart_items:
            OrderItem.objects.create(
                order=order,
                product=item.product,
                quantity=item.quantity,
                price_at_purchase=item.product.newprice,
            )

        payment = Payment.objects.create(
            order=order,
            transaction_id=razorpay_payment_id,
            payment_gateway="razorpay",
            amount=total,
            status="success",
            paid_at=None
        )

        # clear cart
        cart_items.delete()

        # use serializers to return canonical representations
        order_data = OrderSerializer(order).data
        payment_data = PaymentSerializer(payment).data

        return Response({
            "message": "Payment verified & order created",
            "order": order_data,
            "payment": payment_data
        }, status=status.HTTP_201_CREATED)



class orderView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        orders = Order.objects.filter(user=request.user)
        serializer = OrderSerializer(orders, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)
