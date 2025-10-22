from rest_framework.decorators import api_view, permission_classes
from rest_framework.response import Response
from rest_framework import status
from api.models import Survey, Section
from api.serializers import SurveySerializer, SectionSerializer
from api.permissions import permissions


@api_view(['GET', 'POST'])
@permission_classes([permissions.SurveyPermissions])
def survey_list_create(request):
    if request.method == 'GET':
        surveys = Survey.objects.all().order_by('-created_at')
        serializer = SurveySerializer(surveys, many=True)
        return Response(serializer.data)
    
    elif request.method == 'POST':
        serializer = SurveySerializer(data=request.data)
        if serializer.is_valid():
            serializer.save(created_by=request.user)
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


@api_view(['GET', 'PUT', 'PATCH', 'DELETE'])
@permission_classes([permissions.SurveyPermissions])
def survey_detail(request, pk):
    try:
        survey = Survey.objects.get(pk=pk)
    except Survey.DoesNotExist:
        return Response({'detail': 'Survey not found.'}, status=status.HTTP_404_NOT_FOUND)

    if request.method == 'GET':
        serializer = SurveySerializer(survey)
        return Response(serializer.data)
    
    elif request.method in ['PUT', 'PATCH']:
        serializer = SurveySerializer(survey, data=request.data, partial=(request.method == 'PATCH'))
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
    elif request.method == 'DELETE':
        survey.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)
    
@api_view(['GET', 'POST'])
@permission_classes([permissions.SurveyPermissions])
def section_list_create(request):
    if request.method == 'GET':
        sections = Section.objects.all().order_by('order', 'id')
        serializer = SectionSerializer(sections, many=True)
        return Response(serializer.data)
    
    elif request.method == 'POST':
        serializer = SectionSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


@api_view(['GET', 'PUT', 'PATCH', 'DELETE'])
@permission_classes([permissions.SurveyPermissions])
def section_detail(request, pk):
    try:
        section = Section.objects.get(pk=pk)
    except Section.DoesNotExist:
        return Response({'detail': 'Section not found.'}, status=status.HTTP_404_NOT_FOUND)

    if request.method == 'GET':
        serializer = SectionSerializer(section)
        return Response(serializer.data)
    
    elif request.method in ['PUT', 'PATCH']:
        serializer = SectionSerializer(section, data=request.data, partial=(request.method == 'PATCH'))
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
    elif request.method == 'DELETE':
        section.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)
