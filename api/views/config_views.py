from rest_framework.decorators import api_view, permission_classes
from rest_framework.response import Response
from rest_framework import status
from api.models import SystemConfig
from api.serializers import SystemConfigSerializer
from api.permissions import permissions
from drf_yasg.utils import swagger_auto_schema
from drf_yasg import openapi

config_id_param = openapi.Parameter(
    'pk',
    openapi.IN_PATH,
    description="ID of the SystemConfig",
    type=openapi.TYPE_INTEGER,
    required=True
)
















@swagger_auto_schema(
    method='get',
    tags=['System Config'],
    operation_description="Retrieve all system configurations.",
    responses={200: SystemConfigSerializer(many=True)},
)
@swagger_auto_schema(
    method='post',
    tags=['System Config'],
    operation_description="Create a new system configuration.",
    request_body=SystemConfigSerializer,
    responses={
        201: SystemConfigSerializer,
        400: "Bad Request - Validation Error"
    },
)
@api_view(["GET", "POST"])
@permission_classes([permissions.ConfigPermissions])
def system_config_list(request):
    if request.method == "GET":
        configs = SystemConfig.objects.all()
        serializer = SystemConfigSerializer(configs, many=True)
        return Response(serializer.data)

    elif request.method == "POST":
        serializer = SystemConfigSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    













@swagger_auto_schema(
    method='get',
    tags=['System Config'],
    operation_description="Retrieve a system configuration by ID.",
    manual_parameters=[config_id_param],
    responses={
        200: SystemConfigSerializer,
        404: "Not Found"
    },
)
@swagger_auto_schema(
    method='put',
    tags=['System Config'],
    operation_description="Update a system configuration by ID.",
    manual_parameters=[config_id_param],
    request_body=SystemConfigSerializer,
    responses={
        200: SystemConfigSerializer,
        400: "Bad Request",
        404: "Not Found"
    },
)
@swagger_auto_schema(
    method='delete',
    tags=['System Config'],
    operation_description="Delete a system configuration by ID.",
    manual_parameters=[config_id_param],
    responses={
        204: "No Content",
        404: "Not Found"
    },
)
@permission_classes([permissions.ConfigPermissions])
@api_view(["GET", "PUT", "DELETE"])
def system_config_detail(request, pk):
    try:
        config = SystemConfig.objects.get(pk=pk)
    except SystemConfig.DoesNotExist:
        return Response(
            {"detail": "SystemConfig not found"},
            status=status.HTTP_404_NOT_FOUND
        )

    if request.method == "GET":
        serializer = SystemConfigSerializer(config)
        return Response(serializer.data)

    elif request.method == "PUT":
        serializer = SystemConfigSerializer(config, data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    elif request.method == "DELETE":
        config.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)