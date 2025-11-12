from rest_framework.decorators import api_view, permission_classes
from rest_framework.response import Response
from rest_framework import status
from api.models import Periode
from api.serializers import PeriodeSerializer
from api.permissions import permissions



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