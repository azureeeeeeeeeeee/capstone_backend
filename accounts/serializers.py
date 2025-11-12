from rest_framework import serializers
from rest_framework_simplejwt.serializers import TokenObtainPairSerializer
from .models import User, Role

class CustomTokenObtainPairSerializer(TokenObtainPairSerializer):
    @classmethod
    def get_token(cls, user):
        token = super().get_token(user)
        token["role"] = str(user.role)
        return token

class RegisterSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True)

    class Meta:
        model = User
        fields = ("id", "username", "email", "password", "role")

    def create(self, validated_data):
        user = User.objects.create_user(
            username=validated_data["username"],
            email=validated_data["email"],
            password=validated_data["password"],
            role=validated_data.get("role", "user")
        )
        return user


class UserSerializer(serializers.ModelSerializer):
    role = serializers.StringRelatedField()
    class Meta:
        model = User
        fields = '__all__'

    def create(self, validated_data):
        user = User(
            id=validated_data['id'],
            username=validated_data['username'],
        )
        user.set_password(validated_data['password'])
        user.save()
        return user
    


class RoleSerializer(serializers.ModelSerializer):
    program_study_name = serializers.CharField(source='program_study.name', read_only=True)

    class Meta:
        model = Role
        fields = ['id', 'name', 'program_study', 'program_study_name']


class UserSerializer(serializers.ModelSerializer):
    role_name = serializers.CharField(source='role.name', read_only=True)
    program_study_name = serializers.CharField(source='program_study.name', read_only=True)

    class Meta:
        model = User
        fields = [
            'id', 'username', 'email', 'role', 'role_name',
            'program_study', 'program_study_name',
            'address', 'phone_number'
        ]