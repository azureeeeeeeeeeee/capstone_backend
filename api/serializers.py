from rest_framework import serializers
from .models import Survey, ProgramStudy, Section, Question


class ProgramStudySerializer(serializers.ModelSerializer):
    faculty_name = serializers.CharField(source='faculty.name', read_only=True)

    class Meta:
        model = ProgramStudy
        fields = ['id', 'name', 'faculty_name']


class SurveySerializer(serializers.ModelSerializer):
    created_by = serializers.StringRelatedField(read_only=True)

    class Meta:
        model = Survey
        fields = [
            'id',
            'title',
            'description',
            'is_active',
            'survey_type',
            'created_by',
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

import json
from rest_framework import serializers
from .models import Question

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

