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
        print(f"Password : {validated_data['id']}-{validated_data['phone_number']}")
        user.set_password(f"{validated_data['id']}-{validated_data['phone_number']}")
        user.save()
        return user
    


class RoleSerializer(serializers.ModelSerializer):
    program_study_name = serializers.CharField(source='program_study.name', read_only=True)

    class Meta:
        model = Role
        fields = ['id', 'name', 'program_study', 'program_study_name']


class UserCreationSerializer(serializers.ModelSerializer):
    # role_name = serializers.CharField(source='role.name', read_only=True)
    role = serializers.PrimaryKeyRelatedField(queryset=Role.objects.all())
    # program_study_name = serializers.CharField(source='program_study.name', read_only=True)

    class Meta:
        model = User
        fields = [
            'id', 'username', 'email',
            'role', 'program_study',
            'address', 'phone_number', 'nim'
        ]
        # fields = '__all__'

    def create(self, validated_data):
        user = User(
            **validated_data
        )
        # user.role = validated_data['role']

        user.set_password(f"{validated_data['id']}-{validated_data['phone_number']}")
        user.save()
        return user