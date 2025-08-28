from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework.permissions import IsAuthenticated, AllowAny
from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework.decorators import api_view , permission_classes
from django.contrib.auth import authenticate, get_user_model
from .serializers import  CustomerRegisterSerializer, SellerRegisterSerializer,UserProfileSerializer , NoteSerializer
from .models import Note

User = get_user_model()



class RegisterView(APIView):
    permission_classes = [AllowAny]

    def post(self, request):
        user_type = request.data.get('user_type')
        if user_type == 'customer':
            serializer = CustomerRegisterSerializer(data=request.data)
            success_message = "Customer registered successfully"
        elif user_type == 'seller':
            serializer = SellerRegisterSerializer(data=request.data)
            success_message = "Seller registered successfully"
        else:
            return Response({"user_type": ["This field is required and must be 'customer' or 'seller'."]}, status=status.HTTP_400_BAD_REQUEST)

        if serializer.is_valid():
            user = serializer.save()
            return Response({
                "message": success_message,
                "status": True,
                "data": {
                    "username": user.username,
                    "email": user.email,
                }
            }, status=status.HTTP_201_CREATED)
        
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

class LoginView(APIView):
    permission_classes = [AllowAny]

    def post(self, request):
        username = request.data.get('username')
        password = request.data.get('password')

        if username:
            try:
                user = User.objects.get(username=username)  
            except User.DoesNotExist:
                return Response({"message": "Invalid Credentials"}, status=status.HTTP_400_BAD_REQUEST)

        user = authenticate(username=username, password=password)

        if user:
            refresh = RefreshToken.for_user(user)
            return Response({
                "access_token": str(refresh.access_token),
                "refresh_token": str(refresh)
            }, status=status.HTTP_200_OK)

        return Response({"message": "Invalid Credentials"}, status=status.HTTP_400_BAD_REQUEST)


class ProfileView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        serializer = UserProfileSerializer(request.user)
        return Response(serializer.data, status=status.HTTP_200_OK)



        
@api_view(['POST'])
def logout(request):
    try:
        res = Response()
        res.data = {"success":True}
        res.delete_cookie('access_token' , path="/" ,samesite ="None")
        res.delete_cookie('refresh_token' , path="/" ,samesite ="None")
        return res
    
    except:
        return Response({"success":False})
    
    
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