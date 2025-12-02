import os
from rest_framework.decorators import api_view, permission_classes
from rest_framework.response import Response
from rest_framework import status
from rest_framework.permissions import AllowAny
from api.models import SupervisorAnswer, Survey, Question, ProgramSpecificQuestion, Answer, SystemConfig, SupervisorToken
from api.serializers import AnswerSerializer, SupervisorAnswerSerializer
from api.permissions import permissions
from drf_yasg.utils import swagger_auto_schema
from drf_yasg import openapi
from django.db.models import Q
from django.conf import settings
from django.core.mail import send_mail


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
@permission_classes([permissions.AnswerPermissions])
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
    

    

    if survey.survey_type == "lv1":
        code = SystemConfig.objects.get(key="QUESTION_CODE_SPV_EMAIL").value
        question_spv = Question.objects.get(code=code)
        answer_spv = Answer.objects.get(
            user=request.user,
            survey=survey,
            question=question_spv
        )
        spv_email = answer_spv.answer_value
        token_obj = SupervisorToken.objects.create(alumni=request.user)
        skp_survey = Survey.objects.get(survey_type='skp')
        token = str(token_obj.token)

        subject = f"Pengisian survey kepuasan pengguna - {request.user.username}"
        message = f"""
            Hello supervisor,

            Mahasiswa dengan identitas dibawah ini telah mengisi Tracer Study Survey level 1 ITK,
            Nama : {request.user.username}
            NIM : {request.user.id}
            Program Studi : {request.user.program_study.name}

            Mohon untuk mengisi survey kepuasan pengguna untuk saudara/i {request.user.username} dengan mengisi link berikut (Mohon untuk tidak menyebarkan linknya)

            {os.getenv("FRONTEND_URL")}/surveys/{skp_survey.id}/skp?token={token}

            Terima kasih,
            Tim Tracer Study ITK
        """

        send_mail(
            subject,
            message,
            settings.EMAIL_HOST_USER,
            [spv_email],
            fail_silently=False
        )

    return Response(results, status=status.HTTP_201_CREATED)





@swagger_auto_schema(
    method="post",
    tags=["Supervisor - SKP Answer"],
    operation_description="Submit SKP supervisor answers in bulk using a one-time token.",
    manual_parameters=[
        openapi.Parameter(
            name="token",
            in_=openapi.IN_QUERY,
            description="Supervisor token (one-time use)",
            required=True,
            type=openapi.TYPE_STRING
        ),
        openapi.Parameter(
            name="survey_id",
            in_=openapi.IN_PATH,
            description="ID of the SKP survey",
            required=True,
            type=openapi.TYPE_INTEGER
        )
    ],
    request_body=openapi.Schema(
        type=openapi.TYPE_OBJECT,
        properties={
            "answers": openapi.Schema(
                type=openapi.TYPE_ARRAY,
                description="List of answers",
                items=openapi.Schema(
                    type=openapi.TYPE_OBJECT,
                    properties={
                        "question_id": openapi.Schema(
                            type=openapi.TYPE_INTEGER,
                            description="ID of the question"
                        ),
                        "answer_value": openapi.Schema(
                            type=openapi.TYPE_STRING,
                            description="Answer text (optional)"
                        )
                    },
                    required=["question_id"]
                )
            )
        },
        required=["answers"]
    ),
    responses={
        201: openapi.Response(
            description="Answers submitted successfully.",
            examples={
                "application/json": {
                    "detail": "Answers submitted successfully."
                }
            }
        ),
        400: openapi.Response(
            description="Bad request / invalid token / survey invalid.",
            examples={
                "application/json": {
                    "detail": "Token has already been used."
                }
            }
        ),
        404: openapi.Response(
            description="Survey not found.",
            examples={
                "application/json": {
                    "detail": "Survey not found."
                }
            }
        )
    }
)
@api_view(["POST"])
@permission_classes([AllowAny])
def supervisor_answer_bulk(request, survey_id):
    try:
        skp_survey = Survey.objects.get(id=survey_id)
    except Survey.DoesNotExist:
        return Response(
            {"detail": "Survey not found."},
            status=status.HTTP_404_NOT_FOUND
        )

    if skp_survey.survey_type != "skp":
        return Response(
            {"detail": "Survey must be of type 'skp'."},
            status=status.HTTP_400_BAD_REQUEST
        )

    token_value = request.query_params.get("token")
    if not token_value:
        return Response(
            {"detail": "Token query parameter is required."},
            status=status.HTTP_400_BAD_REQUEST
        )
    
    

    try:
        token = SupervisorToken.objects.get(token=token_value)
    except SupervisorToken.DoesNotExist:
        return Response(
            {"detail": "Invalid token."},
            status=status.HTTP_400_BAD_REQUEST
        )
    
    if token.is_used:
        return Response(
            {"detail": "Token has already been used."},
            status=status.HTTP_400_BAD_REQUEST
        )

    answers = request.data.get("answers", [])
    if not isinstance(answers, list):
        return Response(
            {"detail": "Answers must be an array."},
            status=status.HTTP_400_BAD_REQUEST
        )

    for ans in answers:
        SupervisorAnswer.objects.update_or_create(
            token=token,
            survey=skp_survey,
            question_id=ans.get("question_id"),
            defaults={"answer_value": ans.get("answer_value")}
        )

    token.is_used = True
    token.save()

    return Response(
        {"detail": "Answers submitted successfully."},
        status=status.HTTP_201_CREATED
    )