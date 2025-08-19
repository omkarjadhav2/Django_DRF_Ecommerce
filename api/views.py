from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import authentication , permissions
from .models import CustomUser , CustomerProfile , SellerProfile
from .serializers import CustomerRegisterSerializer ,SellerRegisterSerializer
from rest_framework import status
from django.shortcuts import get_object_or_404
from rest_framework_simplejwt.tokens import RefreshToken
from django.contrib.auth import authenticate
from rest_framework.permissions import IsAuthenticated , AllowAny



class RegisterCustomerView(APIView):
    permission_classes = [AllowAny]
    def post(self , request):
        data = request.data
        serializer = CustomerRegisterSerializer(data = data)
        if serializer.is_valid():
            user = serializer.save()
            return Response({"message":"User created successfully" ,"status":True , 
                             "data" : serializer.data},status= status.HTTP_201_CREATED)
        return Response(serializer.errors , status=status.HTTP_400_BAD_REQUEST)


class RegisterSellerView(APIView):
    permission_classes = [AllowAny]
    def post(self , request):
        data = request.data
        serializer = SellerRegisterSerializer(data = data)
        if serializer.is_valid():
            user = serializer.save()
            return Response({"message":"Seller created successfully" ,"status":True , 
                             "data" : serializer.data},status= status.HTTP_201_CREATED)
        return Response(serializer.errors , status=status.HTTP_400_BAD_REQUEST)
    
    
class LoginView(APIView):
    permission_classes = [AllowAny]
    def post(self, request):
        username = request.data.get('username')
        password = request.data.get('password')

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
    def get(self , request):
        user = request.user
        serializer = CustomerRegisterSerializer(user)
        return Response(serializer.data)


