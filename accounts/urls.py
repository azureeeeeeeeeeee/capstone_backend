from django.urls import path
from . import views
from .views import CustomTokenObtainPairView, RegisterView
from rest_framework_simplejwt.views import TokenRefreshView

urlpatterns = [
    path("register/", RegisterView.as_view(), name="register"),
    path("login/", CustomTokenObtainPairView.as_view(), name="token_obtain_pair"),  # <-- custom serializer
    path("refresh/", TokenRefreshView.as_view(), name="token_refresh"),
]
