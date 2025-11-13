from rest_framework.decorators import api_view, permission_classes
from rest_framework.response import Response
from rest_framework import status, permissions
from accounts.models import User, Role
from accounts.serializers import UserCreationSerializer, RoleSerializer
from api.permissions import permissions
from drf_yasg.utils import swagger_auto_schema
from drf_yasg import openapi




@swagger_auto_schema(
    method='get',
    tags=['Admin - CRUD Role'],
    operation_description="Retrieve a list of all roles.",
    responses={200: RoleSerializer(many=True)}
)
@swagger_auto_schema(
    method='post',
    tags=['Admin - CRUD Role'],
    operation_description="Create a new role.",
    request_body=RoleSerializer,
    responses={
        201: RoleSerializer,
        400: 'Validation Error'
    }
)
@api_view(['GET', 'POST'])
@permission_classes([permissions.RolePermissions])
def role_list_create(request):
    if request.method == 'GET':
        roles = Role.objects.select_related('program_study').all()
        serializer = RoleSerializer(roles, many=True)
        return Response(serializer.data)

    if request.method == 'POST':
        serializer = RoleSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)





@swagger_auto_schema(
    method='get',
    tags=['Admin - CRUD Role'],
    operation_description="Retrieve details of a specific role by ID.",
    responses={200: RoleSerializer, 404: 'Not Found'}
)
@swagger_auto_schema(
    method='put',
    tags=['Admin - CRUD Role'],
    operation_description="Update an existing role.",
    request_body=RoleSerializer,
    responses={200: RoleSerializer, 400: 'Validation Error', 404: 'Not Found'}
)
@swagger_auto_schema(
    method='delete',
    tags=['Admin - CRUD Role'],
    operation_description="Delete a role by ID.",
    responses={204: 'No Content', 404: 'Not Found'}
)
@api_view(['GET', 'PUT', 'DELETE'])
@permission_classes([permissions.RolePermissions])
def role_detail(request, pk):
    try:
        role = Role.objects.get(pk=pk)
    except Role.DoesNotExist:
        return Response({'detail': 'Role not found.'}, status=status.HTTP_404_NOT_FOUND)

    if request.method == 'GET':
        serializer = RoleSerializer(role)
        return Response(serializer.data)

    if request.method == 'PUT':
        serializer = RoleSerializer(role, data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    if request.method == 'DELETE':
        role.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)




@swagger_auto_schema(
    method='get',
    tags=['Admin - CRUD User'],
    operation_description="Retrieve a list of all users.",
    responses={200: UserCreationSerializer(many=True)}
)
@swagger_auto_schema(
    method='post',
    tags=['Admin - CRUD User'],
    operation_description="Create a new user.",
    request_body=UserCreationSerializer,
    responses={201: UserCreationSerializer, 400: 'Validation Error'}
)
@api_view(['GET', 'POST'])
@permission_classes([permissions.UserPermissions])
def user_list_create(request):
    if request.method == 'GET':
        users = User.objects.select_related('role', 'program_study').all()
        serializer = UserCreationSerializer(users, many=True)
        return Response(serializer.data)

    if request.method == 'POST':
        serializer = UserCreationSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)




@swagger_auto_schema(
    method='get',
    tags=['Admin - CRUD User'],
    operation_description="Retrieve details of a specific user by ID.",
    responses={200: UserCreationSerializer, 404: 'Not Found'}
)
@swagger_auto_schema(
    method='put',
    tags=['Admin - CRUD User'],
    operation_description="Update user details by ID.",
    request_body=UserCreationSerializer,
    responses={200: UserCreationSerializer, 400: 'Validation Error', 404: 'Not Found'}
)
@swagger_auto_schema(
    method='delete',
    tags=['Admin - CRUD User'],
    operation_description="Delete a user by ID.",
    responses={204: 'No Content', 404: 'Not Found'}
)
@api_view(['GET', 'PUT', 'DELETE'])
@permission_classes([permissions.UserPermissions])
def user_detail(request, pk):
    try:
        user = User.objects.get(pk=pk)
    except User.DoesNotExist:
        return Response({'detail': 'User not found.'}, status=status.HTTP_404_NOT_FOUND)

    if request.method == 'GET':
        serializer = UserCreationSerializer(user)
        return Response(serializer.data)

    if request.method == 'PUT':
        serializer = UserCreationSerializer(user, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    if request.method == 'DELETE':
        user.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)