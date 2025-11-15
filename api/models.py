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

class Periode(models.Model):
    category = models.CharField(max_length=50, unique=True)
    order = models.PositiveIntegerField(unique=True)

    class Meta:
        ordering = ['order']

    def __str__(self):
        return f"{self.category} @ {self.order}"

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
    periode = models.ForeignKey(Periode, on_delete=models.CASCADE, related_name='surveys', null=True, blank=True)
    created_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True)
    start_at = models.DateTimeField(null=True, blank=True)
    end_at = models.DateTimeField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.title} @ {self.created_at}"

class Section(models.Model):
    survey = models.ForeignKey(Survey, on_delete=models.CASCADE, related_name='sections')
    title = models.CharField(max_length=255)
    description = models.TextField(blank=True)
    order = models.IntegerField(default=0)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.title} ({self.survey.title})"
    
class Question(models.Model):
    QUESTION_TYPE_CHOICES = [
        ('text', 'Text'),
        ('number', 'Number'),
        ('radio', 'Single Choice'),
        ('checkbox', 'Multiple Choice'),
        ('scale', 'Scale 1–5'),
        ('dropdown', 'Dropdown'),
    ]

    section = models.ForeignKey('Section', on_delete=models.CASCADE, related_name='questions')
    text = models.TextField()  # e.g. "Apa tingkat tempat kerja Anda?"
    question_type = models.CharField(max_length=20, choices=QUESTION_TYPE_CHOICES, default='text')
    options = models.TextField(blank=True, null=True) 
    code = models.CharField(max_length=50, blank=True, null=True) 
    source = models.CharField(max_length=100, blank=True, null=True)  
    description = models.TextField(blank=True, null=True) 
    order = models.IntegerField(default=0)
    is_required = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.text[:60]}..."
    
class ProgramSpecificQuestion(models.Model):
    QUESTION_TYPE_CHOICES = [
        ('text', 'Text'),
        ('number', 'Number'),
        ('radio', 'Single Choice'),
        ('checkbox', 'Multiple Choice'),
        ('scale', 'Scale 1–5'),
        ('dropdown', 'Dropdown'),
    ]

    program_study = models.ForeignKey(ProgramStudy, on_delete=models.CASCADE, related_name='questions')
    survey = models.ForeignKey(Survey, on_delete=models.CASCADE, related_name='program_questions', null=True, blank=True)
    text = models.TextField()
    question_type = models.CharField(max_length=20, choices=QUESTION_TYPE_CHOICES, default='text')
    options = models.TextField(blank=True, null=True) 
    code = models.CharField(max_length=50, blank=True, null=True) 
    source = models.CharField(max_length=100, blank=True, null=True)  
    description = models.TextField(blank=True, null=True) 
    order = models.IntegerField(default=0)
    is_required = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.text[:60]}..."
