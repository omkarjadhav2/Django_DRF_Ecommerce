from django.urls import path
from .views import *
from rest_framework_simplejwt.views import (
    TokenObtainPairView,
    TokenRefreshView,
)
urlpatterns = [
    path("auth/register/customer/", CustomerRegisterView.as_view(), name="customer-register"),
    path("auth/login/", TokenObtainPairView.as_view(), name="token_obtain_pair"),
    path("auth/token/refresh/", TokenRefreshView.as_view(), name="token_refresh"),
    path("auth/logout/", LogoutView.as_view(), name="logout"),
    path('notes/', get_notes),
    path('profile/', ProfileView.as_view()),
    path('authenticated/', is_logged_in),
    path('upload/', ProductUploadView.as_view() ,  name="upload products"),

]
