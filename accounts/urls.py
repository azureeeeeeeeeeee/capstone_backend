from django.urls import path
from . import views
from .views import CustomTokenObtainPairView, admin_reset_password, user_change_password
from rest_framework_simplejwt.views import TokenRefreshView
# accounts/urls.py

urlpatterns = [
    path("login/", CustomTokenObtainPairView.as_view(), name="token_obtain_pair"),  # <-- custom serializer
    path("refresh/", TokenRefreshView.as_view(), name="token_refresh"),
    path("register/", views.register, name="register"),
    path("password/reset/<str:user_id>/", admin_reset_password),
    path("password/change/", user_change_password),
]
