from rest_framework.decorators import api_view, permission_classes
from rest_framework.response import Response
from rest_framework import status
from api.models import Survey, Question, ProgramSpecificQuestion, Answer
from api.serializers import AnswerSerializer
from api.permissions import permissions
from drf_yasg.utils import swagger_auto_schema
from drf_yasg import openapi
from django.db.models import Q


@swagger_auto_schema(
    method='get',
    tags=['Answer'],
    operation_description="Retrieve all answers for a specific survey.",
    responses={
        200: openapi.Response("List of answers", AnswerSerializer(many=True)),
    },
)
@swagger_auto_schema(
    method='post',
    tags=['Answer'],
    operation_description="Submit an answer for a question in a survey.",
    request_body=AnswerSerializer,
    responses={
        201: openapi.Response("Answer submitted successfully", AnswerSerializer),
        400: "Validation error",
    },
)
@api_view(['GET', 'POST'])
@permission_classes([permissions.SurveyPermissions])
def answer_list_create(request, survey_id):
    """
    GET: Mendapatkan semua jawaban untuk survey tertentu
    POST: Menyimpan jawaban baru untuk pertanyaan dalam survey
    """
    try:
        survey = Survey.objects.get(pk=survey_id)
    except Survey.DoesNotExist:
        return Response(
            {'detail': 'Survey not found.'}, 
            status=status.HTTP_404_NOT_FOUND
        )

    if request.method == 'GET':
        # Filter berdasarkan user jika bukan admin
        if request.user.is_staff or request.user.is_superuser:
            answers = Answer.objects.filter(survey=survey)
        else:
            answers = Answer.objects.filter(survey=survey, user=request.user)
        
        serializer = AnswerSerializer(answers, many=True)
        return Response(serializer.data)
    
    elif request.method == 'POST':
        data = request.data.copy()
        data['survey'] = survey_id
        # user akan di-set langsung saat save, tidak melalui data karena read_only
        
        serializer = AnswerSerializer(data=data)
        if serializer.is_valid():
            serializer.save(user=request.user)
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


@swagger_auto_schema(
    method='get',
    tags=['Answer'],
    operation_description="Retrieve a specific answer by ID.",
    responses={
        200: openapi.Response("Answer details", AnswerSerializer),
        404: "Answer not found",
    },
)
@swagger_auto_schema(
    method='put',
    tags=['Answer'],
    operation_description="Update an existing answer (full update).",
    request_body=AnswerSerializer,
    responses={
        200: openapi.Response("Answer updated successfully", AnswerSerializer),
        400: "Validation error",
        404: "Answer not found",
    },
)
@swagger_auto_schema(
    method='patch',
    tags=['Answer'],
    operation_description="Partially update an answer.",
    request_body=AnswerSerializer,
    responses={
        200: openapi.Response("Answer partially updated", AnswerSerializer),
        400: "Validation error",
        404: "Answer not found",
    },
)
@swagger_auto_schema(
    method='delete',
    tags=['Answer'],
    operation_description="Delete an answer by ID.",
    responses={
        204: "Answer deleted successfully",
        404: "Answer not found",
    },
)
@api_view(['GET', 'PUT', 'PATCH', 'DELETE'])
@permission_classes([permissions.SurveyPermissions])
def answer_detail(request, survey_id, pk):
    """
    GET, PUT, PATCH, DELETE untuk answer tertentu
    """
    try:
        answer = Answer.objects.get(pk=pk, survey_id=survey_id)
    except Answer.DoesNotExist:
        return Response(
            {'detail': 'Answer not found.'}, 
            status=status.HTTP_404_NOT_FOUND
        )

    # Cek apakah user memiliki akses (hanya bisa edit jawaban sendiri, kecuali admin)
    if not (request.user.is_staff or request.user.is_superuser) and answer.user != request.user:
        return Response(
            {'detail': 'You do not have permission to access this answer.'},
            status=status.HTTP_403_FORBIDDEN
        )

    if request.method == 'GET':
        serializer = AnswerSerializer(answer)
        return Response(serializer.data)
    
    elif request.method in ['PUT', 'PATCH']:
        data = request.data.copy()
        data['survey'] = survey_id
        # user akan di-set langsung saat save, tidak melalui data karena read_only
        
        serializer = AnswerSerializer(
            answer, 
            data=data, 
            partial=(request.method == 'PATCH')
        )
        if serializer.is_valid():
            serializer.save(user=request.user)
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
    elif request.method == 'DELETE':
        answer.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)


@swagger_auto_schema(
    method='get',
    tags=['Answer'],
    operation_description="Retrieve all answers for a specific question.",
    responses={
        200: openapi.Response("List of answers for question", AnswerSerializer(many=True)),
    },
)
@api_view(['GET'])
@permission_classes([permissions.SurveyPermissions])
def answer_by_question(request, survey_id, section_id, question_id):
    """
    Mendapatkan semua jawaban untuk pertanyaan tertentu
    """
    try:
        question = Question.objects.get(pk=question_id, section_id=section_id)
    except Question.DoesNotExist:
        return Response(
            {'detail': 'Question not found.'}, 
            status=status.HTTP_404_NOT_FOUND
        )

    # Filter berdasarkan user jika bukan admin
    if request.user.is_staff or request.user.is_superuser:
        answers = Answer.objects.filter(question=question, survey_id=survey_id)
    else:
        answers = Answer.objects.filter(
            question=question, 
            survey_id=survey_id, 
            user=request.user
        )
    
    serializer = AnswerSerializer(answers, many=True)
    return Response(serializer.data)


@swagger_auto_schema(
    method='get',
    tags=['Answer'],
    operation_description="Retrieve all answers for a specific program-specific question.",
    responses={
        200: openapi.Response("List of answers for program-specific question", AnswerSerializer(many=True)),
    },
)
@api_view(['GET'])
@permission_classes([permissions.SurveyPermissions])
def answer_by_program_question(request, survey_id, program_study_id, question_id):
    """
    Mendapatkan semua jawaban untuk program-specific question tertentu
    """
    try:
        question = ProgramSpecificQuestion.objects.get(
            pk=question_id, 
            survey_id=survey_id,
            program_study_id=program_study_id
        )
    except ProgramSpecificQuestion.DoesNotExist:
        return Response(
            {'detail': 'Program-specific question not found.'}, 
            status=status.HTTP_404_NOT_FOUND
        )

    # Filter berdasarkan user jika bukan admin
    if request.user.is_staff or request.user.is_superuser:
        answers = Answer.objects.filter(
            program_specific_question=question, 
            survey_id=survey_id
        )
    else:
        answers = Answer.objects.filter(
            program_specific_question=question, 
            survey_id=survey_id, 
            user=request.user
        )
    
    serializer = AnswerSerializer(answers, many=True)
    return Response(serializer.data)


@swagger_auto_schema(
    method='post',
    tags=['Answer'],
    operation_description="Submit multiple answers at once for a survey.",
    request_body=openapi.Schema(
        type=openapi.TYPE_OBJECT,
        properties={
            'answers': openapi.Schema(
                type=openapi.TYPE_ARRAY,
                items=openapi.Schema(type=openapi.TYPE_OBJECT)
            )
        },
        required=['answers']
    ),
    responses={
        201: openapi.Response("Answers submitted successfully", AnswerSerializer(many=True)),
        400: "Validation error",
    },
)
@api_view(['POST'])
@permission_classes([permissions.SurveyPermissions])
def answer_bulk_create(request, survey_id):
    """
    Menyimpan multiple jawaban sekaligus untuk survey
    """
    try:
        survey = Survey.objects.get(pk=survey_id)
    except Survey.DoesNotExist:
        return Response(
            {'detail': 'Survey not found.'}, 
            status=status.HTTP_404_NOT_FOUND
        )

    answers_data = request.data.get('answers', [])
    if not isinstance(answers_data, list):
        return Response(
            {'detail': "'answers' must be a list."},
            status=status.HTTP_400_BAD_REQUEST
        )

    results = []
    errors = []
    
    for idx, answer_data in enumerate(answers_data):
        answer_data = answer_data.copy()
        answer_data['survey'] = survey_id
        # user akan di-set langsung saat save, tidak melalui data karena read_only
        
        serializer = AnswerSerializer(data=answer_data)
        if serializer.is_valid():
            serializer.save(user=request.user)
            results.append(serializer.data)
        else:
            errors.append({
                'index': idx,
                'errors': serializer.errors
            })
    
    if errors:
        return Response(
            {
                'success': results,
                'errors': errors
            },
            status=status.HTTP_207_MULTI_STATUS  # Multi-Status
        )
    
    return Response(results, status=status.HTTP_201_CREATED)

