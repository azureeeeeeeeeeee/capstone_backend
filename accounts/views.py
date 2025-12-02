from rest_framework import generics
from rest_framework.permissions import AllowAny
from rest_framework.response import Response
from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework import status
from rest_framework_simplejwt.views import TokenObtainPairView
from .serializers import CustomTokenObtainPairSerializer, RegisterSerializer, UserSerializer, AdminPasswordResetSerializer, UserChangePasswordSerializer, UserCreationSerializer
from rest_framework.views import APIView    
from rest_framework.permissions import IsAdminUser, IsAuthenticated
from .models import User
from django.contrib.auth import authenticate
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import AllowAny
from rest_framework.response import Response
from rest_framework import status
from drf_yasg.utils import swagger_auto_schema
from drf_yasg import openapi


class CustomTokenObtainPairView(TokenObtainPairView):
    serializer_class = CustomTokenObtainPairSerializer


# class RegisterView(generics.CreateAPIView):
#     queryset = User.objects.all()
#     serializer_class = RegisterSerializer
#     permission_classes = [AllowAny]


# class LoginView(generics.GenericAPIView):
#     permission_classes = [AllowAny]

#     def post(self, request):
#         username = request.data.get("username")
#         password = request.data.get("password")
#         user = authenticate(username=username, password=password)
#         if user:
#             refresh = RefreshToken.for_user(user)
#             return Response(
#                 {
#                     "refresh": str(refresh),
#                     "access": str(refresh.access_token),
#                 }
#             )
#         return Response({"error": "Invalid Credentials"}, status=status.HTTP_401_UNAUTHORIZED)




@swagger_auto_schema(
    method="post",
    tags=['Auth'],
    
    operation_description="Register a new user",
    request_body=openapi.Schema(
        type=openapi.TYPE_OBJECT,
        properties={
            "id": openapi.Schema(type=openapi.TYPE_STRING, description="User ID / Nomor Induk"),
            "username": openapi.Schema(type=openapi.TYPE_STRING, description="Full name"),
            "password": openapi.Schema(type=openapi.TYPE_STRING, description="Password"),
        },
        required=["id", "username", "password"],
    ),
    responses={
        200: openapi.Response("Register success", examples={"application/json": {"message": "register berhasil"}}),
        400: openapi.Response("Validation error"),
    },
)
@api_view(['POST'])
@permission_classes([AllowAny])
def register(request):
    serializer = UserSerializer(data=request.data)
    if serializer.is_valid():
        serializer.save()
        return Response({
            "message": "register berhasil"
        }, status=status.HTTP_200_OK)
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


@api_view(['POST'])
@permission_classes([IsAdminUser])
def admin_reset_password(request, user_id):
    try:
        user = User.objects.get(id=user_id)
    except User.DoesNotExist:
        return Response({"detail": "User not found"}, status=404)

    serializer = AdminPasswordResetSerializer()
    new_pw = serializer.save(user=user)

    return Response({
        "message": "Password has been reset",
        "user_id": user.id,
        "new_password": new_pw
    }, status=200)


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def user_change_password(request):
    serializer = UserChangePasswordSerializer(data=request.data, context={"request": request})
    
    if serializer.is_valid():
        serializer.save()
        return Response({"message": "Password updated successfully"}, status=200)

    return Response(serializer.errors, status=400)

class UserSelfView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        """Return logged in user's own data"""
        serializer = UserSerializer(request.user)
        return Response(serializer.data)

    def patch(self, request):
        """Partial update (recommended)"""
        serializer = UserCreationSerializer(
            request.user,
            data=request.data,
            partial=True
        )
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def put(self, request):
        """Full update if needed"""
        serializer = UserCreationSerializer(
            request.user,
            data=request.data,
            partial=False
        )
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)