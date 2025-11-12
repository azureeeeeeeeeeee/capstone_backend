from rest_framework.decorators import api_view, permission_classes
from rest_framework.response import Response
from rest_framework import status
from api.models import Faculty, ProgramStudy
from api.serializers import FacultySerializer, ProgramStudySerializer
from api.permissions import permissions
from accounts.models import Role

@api_view(['GET', 'POST'])
@permission_classes([permissions.UnitPermissions])
def faculty_list(request):
    if request.method == 'GET':
        faculties = Faculty.objects.all().order_by('id')
        serializer = FacultySerializer(faculties, many=True)
        return Response(serializer.data)

    elif request.method == 'POST':
        serializer = FacultySerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    

@api_view(['GET', 'PUT', 'PATCH', 'DELETE'])
@permission_classes([permissions.UnitPermissions])
def faculty_detail(request, pk):
    try:
        faculty = Faculty.objects.get(pk=pk)
    except Faculty.DoesNotExist:
        return Response({'detail': 'Faculty not found.'}, status=status.HTTP_404_NOT_FOUND)

    if request.method == 'GET':
        serializer = FacultySerializer(faculty)
        return Response(serializer.data)

    elif request.method in ['PUT', 'PATCH']:
        serializer = FacultySerializer(faculty, data=request.data, partial=(request.method == 'PATCH'))
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    elif request.method == 'DELETE':
        faculty.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)


@api_view(['GET', 'POST'])
@permission_classes([permissions.UnitPermissions])
def program_study_list(request):
    if request.method == 'GET':
        queryset = ProgramStudy.objects.select_related('faculty').all().order_by('id')
        faculty_id = request.query_params.get('faculty_id')
        if faculty_id:
            queryset = queryset.filter(faculty_id=faculty_id)

        serializer = ProgramStudySerializer(queryset, many=True)
        return Response(serializer.data)

    elif request.method == 'POST':
        serializer = ProgramStudySerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            new_study_program_name = serializer.validated_data.get('name')
            Role.objects.get_or_create(name=f"Prodi {new_study_program_name}")
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    

@api_view(['GET', 'PUT', 'PATCH', 'DELETE'])
@permission_classes([permissions.UnitPermissions])
def program_study_detail(request, pk):
    try:
        program = ProgramStudy.objects.get(pk=pk)
    except ProgramStudy.DoesNotExist:
        return Response({'detail': 'Program Study not found.'}, status=status.HTTP_404_NOT_FOUND)

    if request.method == 'GET':
        serializer = ProgramStudySerializer(program)
        return Response(serializer.data)

    elif request.method in ['PUT', 'PATCH']:
        serializer = ProgramStudySerializer(program, data=request.data, partial=(request.method == 'PATCH'))
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    elif request.method == 'DELETE':
        program.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)