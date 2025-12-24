import os
from rest_framework.decorators import api_view, permission_classes
from rest_framework.response import Response
from rest_framework import status
from rest_framework.permissions import AllowAny
from api.models import (
    SupervisorAnswer, Survey, Question,
    ProgramSpecificQuestion, Answer,
    SystemConfig, SupervisorToken
)
from api.serializers import AnswerSerializer, SupervisorAnswerSerializer
from api.permissions import permissions
from drf_yasg.utils import swagger_auto_schema
from drf_yasg import openapi
from django.conf import settings
from django.core.mail import send_mail


# =====================================================
# HELPER: ROLE-BASED ANSWER QUERYSET
# =====================================================
def get_answer_queryset(user, survey):
    role = user.role.name if user.role else None

    if role in ['Admin', 'Tracer']:
        return Answer.objects.filter(survey=survey)

    if role == 'Tim Prodi':
        return Answer.objects.filter(
            survey=survey,
            user__program_study=user.program_study
        )

    # Alumni (default)
    return Answer.objects.filter(
        survey=survey,
        user=user
    )


# =====================================================
# ANSWER LIST + CREATE
# =====================================================
@swagger_auto_schema(
    method='get',
    tags=['Answer'],
    operation_description="Retrieve all answers for a specific survey.",
    responses={200: AnswerSerializer(many=True)},
)
@swagger_auto_schema(
    method='post',
    tags=['Answer'],
    operation_description="Submit an answer for a question in a survey.",
    request_body=AnswerSerializer,
    responses={201: AnswerSerializer},
)
@api_view(['GET', 'POST'])
@permission_classes([permissions.SurveyPermissions])
def answer_list_create(request, survey_id):
    try:
        survey = Survey.objects.get(pk=survey_id)
    except Survey.DoesNotExist:
        return Response({'detail': 'Survey not found.'}, status=404)

    if request.method == 'GET':
        answers = get_answer_queryset(request.user, survey)
        serializer = AnswerSerializer(answers, many=True)
        return Response(serializer.data)

    data = request.data.copy()
    data['survey'] = survey_id

    serializer = AnswerSerializer(data=data)
    if serializer.is_valid():
        serializer.save(user=request.user)
        return Response(serializer.data, status=201)
    return Response(serializer.errors, status=400)


# =====================================================
# ANSWER DETAIL
# =====================================================
@api_view(['GET', 'PUT', 'PATCH', 'DELETE'])
@permission_classes([permissions.SurveyPermissions])
def answer_detail(request, survey_id, pk):
    try:
        answer = Answer.objects.get(pk=pk, survey_id=survey_id)
    except Answer.DoesNotExist:
        return Response({'detail': 'Answer not found.'}, status=404)

    role = request.user.role.name if request.user.role else None

    # READ ACCESS
    if request.method == 'GET':
        allowed_answers = get_answer_queryset(request.user, answer.survey)
        if not allowed_answers.filter(pk=answer.pk).exists():
            return Response({'detail': 'Forbidden.'}, status=403)
        return Response(AnswerSerializer(answer).data)

    # WRITE ACCESS (OWNER ONLY + ADMIN/TRACER)
    if role not in ['Admin', 'Tracer'] and answer.user != request.user:
        return Response(
            {'detail': 'You do not have permission to modify this answer.'},
            status=403
        )

    if request.method in ['PUT', 'PATCH']:
        data = request.data.copy()
        data['survey'] = survey_id
        serializer = AnswerSerializer(
            answer,
            data=data,
            partial=(request.method == 'PATCH')
        )
        if serializer.is_valid():
            serializer.save(user=request.user)
            return Response(serializer.data)
        return Response(serializer.errors, status=400)

    answer.delete()
    return Response(status=204)


# =====================================================
# ANSWER BY QUESTION
# =====================================================
@api_view(['GET'])
@permission_classes([permissions.SurveyPermissions])
def answer_by_question(request, survey_id, section_id, question_id):
    try:
        question = Question.objects.get(pk=question_id, section_id=section_id)
    except Question.DoesNotExist:
        return Response({'detail': 'Question not found.'}, status=404)

    answers = get_answer_queryset(request.user, question.section.survey)
    answers = answers.filter(question=question)

    return Response(AnswerSerializer(answers, many=True).data)


# =====================================================
# ANSWER BY PROGRAM-SPECIFIC QUESTION
# =====================================================
@api_view(['GET'])
@permission_classes([permissions.SurveyPermissions])
def answer_by_program_question(request, survey_id, program_study_id, question_id):
    try:
        question = ProgramSpecificQuestion.objects.get(
            pk=question_id,
            survey_id=survey_id,
            program_study_id=program_study_id
        )
    except ProgramSpecificQuestion.DoesNotExist:
        return Response({'detail': 'Program-specific question not found.'}, status=404)

    answers = get_answer_queryset(request.user, question.survey)
    answers = answers.filter(program_specific_question=question)

    return Response(AnswerSerializer(answers, many=True).data)







@api_view(['POST'])
@permission_classes([permissions.AnswerPermissions])
def answer_bulk_create(request, survey_id):
    try:
        survey = Survey.objects.get(pk=survey_id)
    except Survey.DoesNotExist:
        return Response({'detail': 'Survey not found.'}, status=404)

    answers_data = request.data.get('answers', [])
    results, errors = [], []

    for idx, ans in enumerate(answers_data):
        ans = ans.copy()
        ans['survey'] = survey_id
        serializer = AnswerSerializer(data=ans)
        if serializer.is_valid():
            serializer.save(user=request.user)
            results.append(serializer.data)
        else:
            errors.append({'index': idx, 'errors': serializer.errors})

    if errors:
        return Response({'success': results, 'errors': errors}, status=207)

    # Update user's last_survey field based on survey type
    if survey.survey_type in ['exit', 'lv1', 'lv2']:
        user = request.user
        # Only update if it's a progression (not going backwards)
        survey_order = {'none': 0, 'exit': 1, 'lv1': 2, 'lv2': 3}
        current_level = survey_order.get(user.last_survey, 0)
        new_level = survey_order.get(survey.survey_type, 0)
        
        if new_level > current_level:
            user.last_survey = survey.survey_type
            user.save(update_fields=['last_survey'])

    # Supervisor email logic
    if survey.survey_type == "lv1":
        try:
            code = SystemConfig.objects.get(key="QUESTION_CODE_SPV_EMAIL").value
            question_spv = Question.objects.get(code=code)
            answer_spv = Answer.objects.get(
                user=request.user,
                survey=survey,
                question=question_spv
            )
            spv_email = answer_spv.answer_value

            # Use filter().first() to handle 0 or multiple SKP surveys
            # Prefer active survey (newest first), fallback to any SKP survey (newest first)
            skp_survey = Survey.objects.filter(survey_type='skp', is_active=True).order_by('-created_at').first()
            if not skp_survey:
                skp_survey = Survey.objects.filter(survey_type='skp').order_by('-created_at').first()
            
            if not skp_survey:
                print("Warning: No SKP survey found, cannot send supervisor email")
            else:
                token_obj = SupervisorToken.objects.create(alumni=request.user)
                token = str(token_obj.token)

                send_mail(
                    f"Pengisian survey kepuasan pengguna - {request.user.username}",
                    f"""
Nama : {request.user.username}
NIM : {request.user.id}
Program Studi : {request.user.program_study.name}

Link:
{os.getenv("FRONTEND_URL")}/survey/{skp_survey.id}/supervisor?token={token}
""",
                    settings.EMAIL_HOST_USER,
                    [spv_email],
                )
        except (SystemConfig.DoesNotExist, Question.DoesNotExist, Answer.DoesNotExist) as e:
            # Log the error but don't fail the request - answers are already saved
            print(f"Warning: Could not send supervisor email - {str(e)}")

    return Response(results, status=201)





@swagger_auto_schema(
    method='post',
    tags=['Supervisor Answer'],
    operation_description=(
        "Submit supervisor answers in bulk for a SKP survey using a unique token. "
        "Each token can only be used once."
    ),
    manual_parameters=[
        openapi.Parameter(
            'token',
            openapi.IN_QUERY,
            description="Supervisor unique token",
            type=openapi.TYPE_STRING,
            required=True
        )
    ],
    request_body=openapi.Schema(
        type=openapi.TYPE_OBJECT,
        required=['answers'],
        properties={
            'answers': openapi.Schema(
                type=openapi.TYPE_ARRAY,
                items=openapi.Schema(
                    type=openapi.TYPE_OBJECT,
                    required=['question_id', 'answer_value'],
                    properties={
                        'question_id': openapi.Schema(
                            type=openapi.TYPE_INTEGER,
                            description='Question ID'
                        ),
                        'answer_value': openapi.Schema(
                            type=openapi.TYPE_STRING,
                            description='Answer value'
                        ),
                    }
                )
            )
        }
    ),
    responses={
        201: openapi.Response(
            description="Answers submitted successfully",
            examples={
                "application/json": {
                    "detail": "Answers submitted successfully."
                }
            }
        ),
        400: openapi.Response(
            description="Bad request (missing/invalid token or token already used)"
        ),
        404: openapi.Response(
            description="Survey not found or invalid"
        ),
    },
)
@api_view(["POST"])
@permission_classes([AllowAny])
def supervisor_answer_bulk(request, survey_id):
    try:
        survey = Survey.objects.get(id=survey_id, survey_type='skp')
    except Survey.DoesNotExist:
        return Response({'detail': 'Survey not found or invalid.'}, status=404)

    token_value = request.query_params.get("token")
    if not token_value:
        return Response({'detail': 'Token required.'}, status=400)

    try:
        token = SupervisorToken.objects.get(token=token_value)
    except SupervisorToken.DoesNotExist:
        return Response({'detail': 'Invalid token.'}, status=400)

    if token.is_used:
        return Response({'detail': 'Token already used.'}, status=400)

    for ans in request.data.get("answers", []):
        SupervisorAnswer.objects.update_or_create(
            token=token,
            survey=survey,
            question_id=ans.get("question_id"),
            defaults={"answer_value": ans.get("answer_value")}
        )

    token.is_used = True
    token.save()
    return Response({'detail': 'Answers submitted successfully.'}, status=201)
