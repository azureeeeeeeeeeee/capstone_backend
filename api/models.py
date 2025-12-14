import uuid
from django.db import models
from accounts.models import User


class Faculty(models.Model):
    name = models.CharField(max_length=255)

    def __str__(self):
        return self.name
    

class Department(models.Model):
    faculty = models.ForeignKey(Faculty, on_delete=models.CASCADE, related_name="departments")
    name = models.CharField(max_length=255)

    def __str__(self):
        return f"{self.name} ({self.faculty.name})"


class ProgramStudy(models.Model):
    department = models.ForeignKey(Department, on_delete=models.CASCADE, related_name="programs", null=True)
    name = models.CharField(max_length=255)

    def __str__(self):
        return f"{self.name} ({self.department.name})"

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


class Answer(models.Model):
    """
    Model untuk menyimpan jawaban dari user untuk pertanyaan survey.
    Mendukung berbagai tipe pertanyaan: text, number, radio, checkbox, scale, dropdown.
    """
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='answers')
    survey = models.ForeignKey(Survey, on_delete=models.CASCADE, related_name='answers')
    question = models.ForeignKey(
        Question, 
        on_delete=models.CASCADE, 
        related_name='answers',
        null=True, 
        blank=True
    )
    program_specific_question = models.ForeignKey(
        ProgramSpecificQuestion,
        on_delete=models.CASCADE,
        related_name='answers',
        null=True,
        blank=True
    )
    # answer_value menyimpan jawaban dalam format JSON string untuk fleksibilitas
    # Untuk text/number: string/number biasa
    # Untuk radio/dropdown: string (single value)
    # Untuk checkbox: JSON array ["option1", "option2"]
    # Untuk scale: number (1-5)
    answer_value = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        # Memastikan satu user hanya bisa menjawab satu kali per pertanyaan
        unique_together = [
            ['user', 'question'],
            ['user', 'program_specific_question']
        ]
        ordering = ['-created_at']

    def __str__(self):
        question_text = self.question.text[:50] if self.question else self.program_specific_question.text[:50] if self.program_specific_question else "Unknown"
        return f"{self.user.username} - {question_text} - {self.answer_value[:30]}"

class QuestionBranch(models.Model):
    question = models.ForeignKey(Question, on_delete=models.CASCADE, related_name="branches")
    answer_value = models.CharField(max_length=255)  # e.g. "Sudah bekerja"
    next_section = models.ForeignKey(Section, on_delete=models.CASCADE)

    def __str__(self):
        return f"{self.question.text[:30]} -> {self.next_section.title}"

class SupervisorToken(models.Model):
    alumni = models.ForeignKey(User, on_delete=models.CASCADE)
    token = models.UUIDField(default=uuid.uuid4, unique=True)
    is_used = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)

class SystemConfig(models.Model):
    key = models.CharField(max_length=100, unique=True)
    value = models.CharField(max_length=255)

    def __str__(self):
        return f"{self.key} = {self.value}"
    

class SupervisorAnswer(models.Model):
    token = models.ForeignKey(
        SupervisorToken,
        on_delete=models.CASCADE,
        related_name='answers'
    )
    survey = models.ForeignKey(
        Survey,
        on_delete=models.CASCADE,
        related_name='supervisor_answers'
    )
    question = models.ForeignKey(
        Question,
        on_delete=models.CASCADE,
        related_name='supervisor_answers'
    )
    
    # boleh null untuk pertanyaan opsional
    answer_value = models.TextField(null=True, blank=True)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        unique_together = [
            ['token', 'question']
        ]
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['token']),
            models.Index(fields=['survey']),
        ]

    def __str__(self):
        return f"Supervisor {self.token.alumni.username} - {self.question.text[:40]}"