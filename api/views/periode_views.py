from rest_framework.decorators import api_view, permission_classes
from rest_framework.response import Response
from rest_framework import status
from api.models import Periode
from api.serializers import PeriodeSerializer
from api.permissions import permissions
from drf_yasg.utils import swagger_auto_schema
from drf_yasg import openapi


@swagger_auto_schema(
    method='get',
    tags=['Periode'],
    operation_description="Retrieve a list of all Periodes ordered by their `order` field.",
    responses={
        200: openapi.Response("List of Periodes", PeriodeSerializer(many=True)),
    },
)
@swagger_auto_schema(
    method='post',
    tags=['Periode'],
    operation_description="Create a new Periode record.",
    request_body=PeriodeSerializer,
    responses={
        201: openapi.Response("Periode created successfully", PeriodeSerializer),
        400: "Validation error",
    },
)
@api_view(['GET', 'POST'])
@permission_classes([permissions.PeriodePermissions])
def periode_list(request):
    if request.method == 'GET':
        periodes = Periode.objects.all().order_by('order')
        serializer = PeriodeSerializer(periodes, many=True)
        return Response(serializer.data)

    elif request.method == 'POST':
        serializer = PeriodeSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)



@swagger_auto_schema(
    method='get',
    tags=['Periode'],
    operation_description="Retrieve a specific Periode by ID.",
    responses={
        200: openapi.Response("Periode details", PeriodeSerializer),
        404: "Periode not found",
    },
)
@swagger_auto_schema(
    method='put',
    tags=['Periode'],
    operation_description="Fully update an existing Periode by ID.",
    request_body=PeriodeSerializer,
    responses={
        200: openapi.Response("Periode updated successfully", PeriodeSerializer),
        400: "Validation error",
        404: "Periode not found",
    },
)
@swagger_auto_schema(
    method='patch',
    tags=['Periode'],
    operation_description="Partially update an existing Periode by ID.",
    request_body=PeriodeSerializer,
    responses={
        200: openapi.Response("Periode partially updated", PeriodeSerializer),
        400: "Validation error",
        404: "Periode not found",
    },
)
@swagger_auto_schema(
    method='delete',
    tags=['Periode'],
    operation_description="Delete a Periode by ID.",
    responses={
        204: "Periode deleted successfully",
        404: "Periode not found",
    },
)
@api_view(['GET', 'PUT', 'PATCH', 'DELETE'])
@permission_classes([permissions.PeriodePermissions])
def periode_detail(request, pk):
    try:
        periode = Periode.objects.get(pk=pk)
    except Periode.DoesNotExist:
        return Response({'error': 'Periode not found'}, status=status.HTTP_404_NOT_FOUND)

    if request.method == 'GET':
        serializer = PeriodeSerializer(periode)
        return Response(serializer.data)

    elif request.method in ['PUT', 'PATCH']:
        serializer = PeriodeSerializer(periode, data=request.data, partial=(request.method == 'PATCH'))
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    elif request.method == 'DELETE':
        periode.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)