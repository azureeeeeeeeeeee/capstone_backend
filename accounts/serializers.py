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
    class Meta:
        model = Role
        fields = ['id', 'name']


class UserCreationSerializer(serializers.ModelSerializer):
    # role_name = serializers.CharField(source='role.name', read_only=True)
    role = serializers.PrimaryKeyRelatedField(queryset=Role.objects.all())
    # program_study_name = serializers.CharField(source='program_study.name', read_only=True)

    class Meta:
        model = User
        fields = [
            'id', 'username', 'email',
            'role', 'program_study',
            'address', 'phone_number'
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

class AdminPasswordResetSerializer(serializers.Serializer):
    new_password = serializers.CharField(read_only=True)

    def save(self, user):
        phone = user.phone_number or "0000"
        new_pw = f"{user.id}-{phone}"
        user.set_password(new_pw)
        user.save()
        return new_pw

class UserChangePasswordSerializer(serializers.Serializer):
    old_password = serializers.CharField()
    new_password = serializers.CharField()

    def validate(self, data):
        user = self.context["request"].user

        if not user.check_password(data["old_password"]):
            raise serializers.ValidationError({"old_password": "Incorrect old password"})

        return data

    def save(self, **kwargs):
        user = self.context["request"].user
        user.set_password(self.validated_data["new_password"])
        user.save()
        return user
