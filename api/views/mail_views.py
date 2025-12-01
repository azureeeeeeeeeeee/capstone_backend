from rest_framework.decorators import api_view, permission_classes
from rest_framework.response import Response
from rest_framework.permissions import AllowAny
from rest_framework import status
from django.core.mail import send_mail
from django.conf import settings

@api_view(['GET'])
@permission_classes([AllowAny])
def submit_answer(request):

        subject = f"New Answer from rionando"
        message = f"""
            Hello Supervisor,

            An alumni has submitted an answer.

            Alumni : Rio
            Question: whas is das
            Answer  : your spv email

            Best regards,
            Tracer Study System
        """


        send_mail(
            subject,
            message,
            settings.EMAIL_HOST_USER,
            ["rionandosoeksin@gmail.com"],
            fail_silently=False,
        )

        return Response({"message": "email sent"}, status=status.HTTP_201_CREATED)
