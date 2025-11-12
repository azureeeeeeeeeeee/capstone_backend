from rest_framework import serializers
from .models import Survey, ProgramStudy, Section, Question, ProgramSpecificQuestion, Faculty, Periode
import json

class PeriodeSerializer(serializers.ModelSerializer):
    class Meta:
        model = Periode
        fields = ['id', 'category', 'order']

class ProgramStudySerializer(serializers.ModelSerializer):
    faculty_name = serializers.CharField(source='faculty.name', read_only=True)

    class Meta:
        model = ProgramStudy
        fields = ['id', 'name', 'faculty_name']


class SurveySerializer(serializers.ModelSerializer):
    created_by = serializers.StringRelatedField(read_only=True)
    periode = PeriodeSerializer(read_only=True)
    periode_id = serializers.PrimaryKeyRelatedField(
        queryset=Periode.objects.all(), source='periode', write_only=True
    )

    class Meta:
        model = Survey
        fields = [
            'id',
            'title',
            'description',
            'is_active',
            'survey_type',
            'created_by',
            'periode',
            'periode_id',
            'start_at',
            'end_at',
            'created_at'
        ]
        read_only_fields = ['created_at', 'created_by']

class SectionSerializer(serializers.ModelSerializer):
    survey_title = serializers.CharField(source='survey.title', read_only=True)

    class Meta:
        model = Section
        fields = [
            'id',
            'survey',
            'survey_title',
            'title',
            'description',
            'order',
            'created_at',
        ]
        read_only_fields = ['created_at']


class QuestionSerializer(serializers.ModelSerializer):
    section_title = serializers.CharField(source='section.title', read_only=True)
    survey_title = serializers.CharField(source='section.survey.title', read_only=True)

    class Meta:
        model = Question
        fields = [
            'id',
            'section',
            'section_title',
            'survey_title',
            'text',
            'question_type',
            'options',
            'code',
            'source',
            'description',
            'order',
            'is_required',
            'created_at',
        ]
        read_only_fields = ['created_at']

    def to_internal_value(self, data):

        if isinstance(data.get('options'), list):
            data['options'] = json.dumps(data['options'])
        return super().to_internal_value(data)

    def to_representation(self, instance):

        rep = super().to_representation(instance)
        try:
            rep['options'] = json.loads(instance.options) if instance.options else []
        except Exception:
            rep['options'] = instance.options.splitlines() if instance.options else []
        return rep

class ProgramSpecificQuestionSerializer(serializers.ModelSerializer):
    program_study_name = serializers.CharField(source='program_study.name', read_only=True)
    survey_title = serializers.CharField(source='survey.title', read_only=True)

    class Meta:
        model = ProgramSpecificQuestion
        fields = [
            'id', 'program_study', 'program_study_name',
            'survey', 'survey_title',
            'text', 'question_type', 'options',
            'code', 'source', 'description',
            'order', 'is_required', 'created_at'
        ]


class FacultySerializer(serializers.ModelSerializer):
    class Meta:
        model = Faculty
        fields = ['id', 'name']


class ProgramStudySerializer(serializers.ModelSerializer):
    faculty_name = serializers.CharField(source='faculty.name', read_only=True)

    class Meta:
        model = ProgramStudy
        fields = ['id', 'name', 'faculty', 'faculty_name']