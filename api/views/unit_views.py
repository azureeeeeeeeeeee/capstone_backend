from rest_framework.decorators import api_view, permission_classes
from rest_framework.response import Response
from rest_framework import status
from api.models import Faculty, ProgramStudy, Department
from api.serializers import FacultySerializer, ProgramStudySerializer, DepartmentSerializer
from api.permissions import permissions
from accounts.models import Role
from drf_yasg.utils import swagger_auto_schema
from drf_yasg import openapi




faculty_id_param = openapi.Parameter(
    'faculty_id',
    openapi.IN_QUERY,
    description="Optional: Filter Program Studies by Faculty ID",
    type=openapi.TYPE_INTEGER
)




@swagger_auto_schema(
    method='get',
    tags=['Work Unit - Faculty'],
    operation_description="Retrieve all faculties ordered by ID.",
    responses={
        200: openapi.Response("List of Faculties", FacultySerializer(many=True)),
    },
)
@swagger_auto_schema(
    method='post',
    tags=['Work Unit - Faculty'],
    operation_description="Create a new Faculty.",
    request_body=FacultySerializer,
    responses={
        201: openapi.Response("Faculty created successfully", FacultySerializer),
        400: "Validation error",
    },
)
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
    


@swagger_auto_schema(
    method='get',
    tags=['Work Unit - Faculty'],
    operation_description="Retrieve details of a Faculty by ID.",
    responses={
        200: openapi.Response("Faculty details", FacultySerializer),
        404: "Faculty not found",
    },
)
@swagger_auto_schema(
    method='put',
    tags=['Work Unit - Faculty'],
    operation_description="Update an existing Faculty (full update).",
    request_body=FacultySerializer,
    responses={
        200: openapi.Response("Faculty updated successfully", FacultySerializer),
        400: "Validation error",
        404: "Faculty not found",
    },
)
@swagger_auto_schema(
    method='patch',
    tags=['Work Unit - Faculty'],
    operation_description="Partially update an existing Faculty.",
    request_body=FacultySerializer,
    responses={
        200: openapi.Response("Faculty partially updated", FacultySerializer),
        400: "Validation error",
        404: "Faculty not found",
    },
)
@swagger_auto_schema(
    method='delete',
    tags=['Work Unit - Faculty'],
    operation_description="Delete a Faculty by ID.",
    responses={
        204: "Faculty deleted successfully",
        404: "Faculty not found",
    },
)
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






@swagger_auto_schema(
    method='get',
    tags=['Work Unit - Program Study'],
    operation_description="Retrieve all Program Studies ordered by ID. Optionally filter by faculty_id.",
    manual_parameters=[faculty_id_param],
    responses={
        200: openapi.Response("List of Program Studies", ProgramStudySerializer(many=True)),
    },
)
@swagger_auto_schema(
    method='post',
    tags=['Work Unit - Program Study'],
    operation_description="Create a new Program Study. Automatically creates a matching Role named 'Prodi <name>'.",
    request_body=ProgramStudySerializer,
    responses={
        201: openapi.Response("Program Study created successfully", ProgramStudySerializer),
        400: "Validation error",
    },
)
@api_view(['GET', 'POST'])
@permission_classes([permissions.UnitPermissions])
def program_study_list(request):
    if request.method == 'GET':
        queryset = ProgramStudy.objects.select_related('department', 'department__faculty').all().order_by('id')

        faculty_id = request.query_params.get('faculty_id')
        if faculty_id:
            queryset = queryset.filter(department__faculty_id=faculty_id)

        serializer = ProgramStudySerializer(queryset, many=True)
        return Response(serializer.data)

    elif request.method == 'POST':
        serializer = ProgramStudySerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()

            new_study_program_name = serializer.validated_data.get('name')
            Role.objects.get_or_create(name=f"Prodi {new_study_program_name}", program_study=serializer.instance)

            return Response(serializer.data, status=status.HTTP_201_CREATED)

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    






@swagger_auto_schema(
    method='get',
    tags=['Work Unit - Program Study'],
    operation_description="Retrieve details of a Program Study by ID.",
    responses={
        200: openapi.Response("Program Study details", ProgramStudySerializer),
        404: "Program Study not found",
    },
)
@swagger_auto_schema(
    method='put',
    tags=['Work Unit - Program Study'],
    operation_description="Update a Program Study (full update).",
    request_body=ProgramStudySerializer,
    responses={
        200: openapi.Response("Program Study updated successfully", ProgramStudySerializer),
        400: "Validation error",
        404: "Program Study not found",
    },
)
@swagger_auto_schema(
    method='patch',
    tags=['Work Unit - Program Study'],
    operation_description="Partially update a Program Study.",
    request_body=ProgramStudySerializer,
    responses={
        200: openapi.Response("Program Study partially updated", ProgramStudySerializer),
        400: "Validation error",
        404: "Program Study not found",
    },
)
@swagger_auto_schema(
    method='delete',
    tags=['Work Unit - Program Study'],
    operation_description="Delete a Program Study by ID.",
    responses={
        204: "Program Study deleted successfully",
        404: "Program Study not found",
    },
)
@api_view(['GET', 'PUT', 'PATCH', 'DELETE'])
@permission_classes([permissions.UnitPermissions])
def program_study_detail(request, pk):
    try:
        program = ProgramStudy.objects.select_related('department', 'department__faculty').get(pk=pk)
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
        Role.objects.filter(program_study=program).delete()
        program.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)
    









@swagger_auto_schema(
    method='get',
    tags=['Work Unit - Department'],
    operation_description="Retrieve all Departments ordered by ID. Optionally filter by faculty_id.",
    manual_parameters=[faculty_id_param],
    responses={200: DepartmentSerializer(many=True)},
)
@swagger_auto_schema(
    method='post',
    tags=['Work Unit - Department'],
    operation_description="Create a new Department.",
    request_body=DepartmentSerializer,
    responses={201: DepartmentSerializer},
)
@api_view(['GET', 'POST'])
@permission_classes([permissions.UnitPermissions])
def department_list(request):
    if request.method == 'GET':
        queryset = Department.objects.select_related('faculty').all().order_by('id')
        faculty_id = request.query_params.get('faculty_id')

        if faculty_id:
            queryset = queryset.filter(faculty_id=faculty_id)

        serializer = DepartmentSerializer(queryset, many=True)
        return Response(serializer.data)

    elif request.method == 'POST':
        serializer = DepartmentSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)



@swagger_auto_schema(
    method='get',
    tags=['Work Unit - Department'],
    operation_description="Retrieve Department details.",
    responses={200: DepartmentSerializer}
)
@swagger_auto_schema(
    method='put',
    tags=['Work Unit - Department'],
    operation_description="Full update Department.",
    request_body=DepartmentSerializer,
    responses={200: DepartmentSerializer}
)
@swagger_auto_schema(
    method='patch',
    tags=['Work Unit - Department'],
    operation_description="Partial update Department.",
    request_body=DepartmentSerializer,
    responses={200: DepartmentSerializer}
)
@swagger_auto_schema(
    method='delete',
    tags=['Work Unit - Department'],
    operation_description="Delete Department.",
    responses={204: "Deleted"}
)
@api_view(['GET', 'PUT', 'PATCH', 'DELETE'])
@permission_classes([permissions.UnitPermissions])
def department_detail(request, pk):
    try:
        department = Department.objects.get(pk=pk)
    except Department.DoesNotExist:
        return Response({'detail': 'Department not found.'}, status=status.HTTP_404_NOT_FOUND)

    if request.method == 'GET':
        serializer = DepartmentSerializer(department)
        return Response(serializer.data)

    elif request.method in ['PUT', 'PATCH']:
        serializer = DepartmentSerializer(
            department,
            data=request.data,
            partial=(request.method == 'PATCH')
        )
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    elif request.method == 'DELETE':
        department.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)