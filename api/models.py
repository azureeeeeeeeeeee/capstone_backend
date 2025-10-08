from django.db import models
from accounts.models import User

class Faculty(models.Model):
    name = models.CharField(max_length=255)

    def __str__(self):
        return self.name


class ProgramStudy(models.Model):
    faculty = models.ForeignKey(Faculty, on_delete=models.CASCADE, related_name="programs")
    name = models.CharField(max_length=255)

    def __str__(self):
        return self.name


class Survey(models.Model):
    SURVEY_CHOICES = (
        ('exit', 'Exit'),
        ('lv1', 'Level 1'),
        ('lv2', 'Level 2'),
        ('skp', 'SKP'),
    )

    title = models.CharField(max_length=255)
    description = models.TextField(blank=True)
    is_active = models.BooleanField(default=False)
    survey_type = models.CharField(max_length=10, choices=SURVEY_CHOICES, default='exit')
    created_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True)
    start_at = models.DateTimeField(null=True, blank=True)
    end_at = models.DateTimeField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)