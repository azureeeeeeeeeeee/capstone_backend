from rest_framework import serializers
from .models import Survey, ProgramStudy


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
