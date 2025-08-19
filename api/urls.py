from django.urls import path
from .views import *

urlpatterns = [
    path('register/', RegisterCustomerView.as_view()),
    path('login/', LoginView.as_view()),
    path('profile/', ProfileView.as_view()),
    path('registerseller/', RegisterSellerView.as_view())

]
