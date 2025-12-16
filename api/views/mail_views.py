from django.utils import timezone
from django.core.mail import send_mail
from django.conf import settings

from rest_framework.decorators import api_view, permission_classes
from rest_framework.response import Response

from drf_yasg.utils import swagger_auto_schema
from drf_yasg import openapi

from api.permissions.permissions import AllReminderPermission, ProdiReminderPermission, UserReminderPermission

from accounts.models import User
from api.models import Survey, Question, Answer

program_study_ids_param = openapi.Parameter(
    'program_study_ids',
    openapi.IN_BODY,
    description="Program Study IDs (Prodi can only send for their own Program Study)",
    type=openapi.TYPE_ARRAY,
    items=openapi.Items(type=openapi.TYPE_STRING),
)




@swagger_auto_schema(
    methods=['POST'],
    tags=['Survey Reminder'],
    operation_description="Send reminder emails to all alumni who have not completed active surveys.",
    responses={
        200: openapi.Schema(
            type=openapi.TYPE_OBJECT,
            properties={
                "message": openapi.Schema(type=openapi.TYPE_STRING),
                "total_reminded": openapi.Schema(type=openapi.TYPE_INTEGER),
            },
        )
    },
)
@api_view(['POST'])
@permission_classes([AllReminderPermission])
def remind_unfinished_survey_users(request):
    now = timezone.now()
    reminders_sent = []

    active_surveys = Survey.objects.filter(
        is_active=True,
        start_at__lte=now,
        end_at__gte=now
    )

    alumni_users = User.objects.filter(
        role__name='Alumni'
    ).select_related('program_study')

    for survey in active_surveys:
        required_questions = Question.objects.filter(
            section__survey=survey,
            is_required=True
        )

        total_required = required_questions.count()
        if total_required == 0:
            continue

        for user in alumni_users:
            answered_count = Answer.objects.filter(
                user=user,
                survey=survey,
                question__in=required_questions
            ).count()

            if answered_count < total_required:
                send_mail(
                    subject=f"Reminder Survey: {survey.title}",
                    message=(
                        f"Halo {user.username},\n\n"
                        f"Anda belum menyelesaikan survey:\n"
                        f"{survey.title}\n\n"
                        f"Batas waktu: {survey.end_at}\n\n"
                        f"Terima kasih."
                    ),
                    from_email=settings.DEFAULT_FROM_EMAIL,
                    recipient_list=[user.email],
                    fail_silently=True,
                )

                reminders_sent.append(user.id)

    return Response({
        "message": "Reminder process completed",
        "total_reminded": len(reminders_sent),
    })







@swagger_auto_schema(
    methods=['POST'],
    tags=['Survey Reminder'],
    operation_description="Send reminder emails to alumni in the Prodi of the logged-in Prodi user.",
    responses={
        200: openapi.Schema(
            type=openapi.TYPE_OBJECT,
            properties={
                "total_reminded": openapi.Schema(type=openapi.TYPE_INTEGER),
            },
        )
    },
)
@api_view(['POST'])
@permission_classes([ProdiReminderPermission])
def remind_unfinished_by_program_study(request):
    now = timezone.now()
    reminders_sent = []

    users = User.objects.filter(
        role__name='Alumni',
        program_study=request.user.program_study
    ).select_related('program_study')

    active_surveys = Survey.objects.filter(
        is_active=True,
        start_at__lte=now,
        end_at__gte=now
    )

    for survey in active_surveys:
        required_questions = Question.objects.filter(
            section__survey=survey,
            is_required=True
        )

        total_required = required_questions.count()
        if total_required == 0:
            continue

        for user in users:
            answered_count = Answer.objects.filter(
                user=user,
                survey=survey,
                question__in=required_questions
            ).count()

            if answered_count < total_required:
                send_mail(
                    subject=f"Reminder Survey: {survey.title}",
                    message=(
                        f"Halo {user.username},\n\n"
                        f"Anda belum menyelesaikan survey:\n"
                        f"{survey.title}\n\n"
                        f"Batas waktu: {survey.end_at}\n\n"
                        f"Terima kasih."
                    ),
                    from_email=settings.DEFAULT_FROM_EMAIL,
                    recipient_list=[user.email],
                    fail_silently=True,
                )

                reminders_sent.append(user.id)

    return Response({
        "total_reminded": len(reminders_sent),
    })







@swagger_auto_schema(
    methods=['POST'],
    tags=['Survey Reminder'],
    operation_description="Send reminder emails to specific alumni users.",
    request_body=openapi.Schema(
        type=openapi.TYPE_OBJECT,
        required=['user_ids'],
        properties={
            "user_ids": openapi.Schema(
                type=openapi.TYPE_ARRAY,
                items=openapi.Items(type=openapi.TYPE_STRING),
            )
        },
    ),
    responses={
        200: openapi.Schema(
            type=openapi.TYPE_OBJECT,
            properties={
                "total_reminded": openapi.Schema(type=openapi.TYPE_INTEGER),
            },
        )
    },
)
@api_view(['POST'])
@permission_classes([UserReminderPermission])
def remind_unfinished_by_users(request):
    user_ids = request.data.get("user_ids", [])

    now = timezone.now()
    reminders_sent = []

    users = User.objects.filter(
        id__in=user_ids,
        role__name='Alumni'
    )

    active_surveys = Survey.objects.filter(
        is_active=True,
        start_at__lte=now,
        end_at__gte=now
    )

    for survey in active_surveys:
        required_questions = Question.objects.filter(
            section__survey=survey,
            is_required=True
        )

        total_required = required_questions.count()
        if total_required == 0:
            continue

        for user in users:
            answered_count = Answer.objects.filter(
                user=user,
                survey=survey,
                question__in=required_questions
            ).count()

            if answered_count < total_required:
                send_mail(
                    subject=f"Reminder Survey: {survey.title}",
                    message=(
                        f"Halo {user.username},\n\n"
                        f"Anda belum menyelesaikan survey:\n"
                        f"{survey.title}\n\n"
                        f"Batas waktu: {survey.end_at}\n\n"
                        f"Terima kasih."
                    ),
                    from_email=settings.DEFAULT_FROM_EMAIL,
                    recipient_list=[user.email],
                    fail_silently=True,
                )

                reminders_sent.append(user.id)

    return Response({
        "total_reminded": len(reminders_sent),
    })
