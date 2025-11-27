from rest_framework import serializers
from .models import Survey, ProgramStudy, Section, Question, ProgramSpecificQuestion, Faculty, Periode, Answer, Department, QuestionBranch
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
        queryset=Periode.objects.all(),
        source='periode', 
        write_only=True,
        required=False,
        allow_null=True
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

class QuestionBranchSerializer(serializers.ModelSerializer):
    class Meta:
        model = QuestionBranch
        fields = ['answer_value', 'next_section']

class QuestionSerializer(serializers.ModelSerializer):
    section_title = serializers.CharField(source='section.title', read_only=True)
    survey_title = serializers.CharField(source='section.survey.title', read_only=True)

    branches = QuestionBranchSerializer(many=True, read_only=True)

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
            'branches',
            'is_required',
            'created_at',
        ]
        read_only_fields = ['created_at']

    def to_internal_value(self, data):
        # Convert list -> JSON string for options
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

    # ==========================
    # MAIN VALIDATION
    # ==========================
    def validate(self, data):
        branches_data = self.initial_data.get('branches')

        # If no branches submitted → skip validation
        if not branches_data:
            return data

        # Check question_type
        q_type = data.get('question_type', getattr(self.instance, 'question_type', None))

        if q_type != 'radio':
            raise serializers.ValidationError("Branching is only allowed for 'radio' (single choice) question type.")

        # Ensure options exist
        raw_options = self.initial_data.get('options')
        if raw_options is None and self.instance:
            raw_options = self.instance.options

        # Parse options
        try:
            options = json.loads(raw_options) if isinstance(raw_options, str) else raw_options
        except:
            options = []

        if not isinstance(options, list):
            raise serializers.ValidationError("Invalid options format.")

        # Validate each branch.answer_value
        for b in branches_data:
            ans = b.get("answer_value")
            if ans not in options:
                raise serializers.ValidationError(
                    f"Branch answer_value '{ans}' does not exist in options."
                )

        return data

    # ==========================
    # CREATE
    # ==========================
    def create(self, validated_data):
        branches_data = self.initial_data.get('branches', [])

        question = Question.objects.create(**validated_data)

        # Create branches
        for b in branches_data:
            QuestionBranch.objects.create(
                question=question,
                answer_value=b['answer_value'],
                next_section_id=b['next_section']
            )

        return question

    # ==========================
    # UPDATE
    # ==========================
    def update(self, instance, validated_data):
        branches_data = self.initial_data.get('branches')

        # update main question fields
        for attr, value in validated_data.items():
            setattr(instance, attr, value)
        instance.save()

        # If branches submitted, replace all old ones
        if branches_data is not None:
            QuestionBranch.objects.filter(question=instance).delete()
            for b in branches_data:
                QuestionBranch.objects.create(
                    question=instance,
                    answer_value=b['answer_value'],
                    next_section_id=b['next_section']
                )

        return instance



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
        read_only_fields = ['created_at']

    def to_internal_value(self, data):
        """Convert list options to JSON string when saving"""
        if isinstance(data.get('options'), list):
            data['options'] = json.dumps(data['options'])
        return super().to_internal_value(data)

    def to_representation(self, instance):
        """Convert JSON string options to list when reading"""
        rep = super().to_representation(instance)
        try:
            rep['options'] = json.loads(instance.options) if instance.options else []
        except Exception:
            rep['options'] = instance.options.splitlines() if instance.options else []
        return rep


class FacultySerializer(serializers.ModelSerializer):
    class Meta:
        model = Faculty
        fields = ['id', 'name']

class DepartmentSerializer(serializers.ModelSerializer):
    faculty_name = serializers.CharField(source='faculty.name', read_only=True)

    class Meta:
        model = Department
        fields = ['id', 'name', 'faculty', 'faculty_name']


class ProgramStudySerializer(serializers.ModelSerializer):
    department_name = serializers.CharField(source='department.name', read_only=True)
    faculty_name = serializers.CharField(source='department.faculty.name', read_only=True)

    class Meta:
        model = ProgramStudy
        fields = [
            'id',
            'name',
            'department',
            'department_name',
            'faculty_name',
        ]


class AnswerSerializer(serializers.ModelSerializer):
    """
    Serializer untuk menyimpan dan mengambil jawaban survey.
    Mendukung berbagai tipe pertanyaan dengan validasi yang sesuai.
    """
    user_id = serializers.CharField(source='user.id', read_only=True)
    user_username = serializers.CharField(source='user.username', read_only=True)
    user_email = serializers.CharField(source='user.email', read_only=True)
    user_program_study = serializers.CharField(source='user.program_study.name', read_only=True)
    question_text = serializers.CharField(source='question.text', read_only=True)
    question_type = serializers.CharField(source='question.question_type', read_only=True)
    program_specific_question_text = serializers.CharField(
        source='program_specific_question.text', 
        read_only=True
    )
    program_specific_question_type = serializers.CharField(
        source='program_specific_question.question_type', 
        read_only=True
    )

    class Meta:
        model = Answer
        fields = [
            'id',
            'user_id',
            'user_username',
            'user_email',
            'user_program_study',
            'survey',
            'question',
            'question_text',
            'question_type',
            'program_specific_question',
            'program_specific_question_text',
            'program_specific_question_type',
            'answer_value',
            'created_at',
            'updated_at',
        ]
        read_only_fields = ['created_at', 'updated_at', 'user']

    def validate(self, data):
        """
        Validasi untuk memastikan:
        1. Harus ada question ATAU program_specific_question (tidak keduanya, tidak kosong)
        2. answer_value sesuai dengan tipe pertanyaan
        """
        question = data.get('question')
        program_specific_question = data.get('program_specific_question')
        answer_value = data.get('answer_value')
        survey = data.get('survey')

        # Validasi: harus ada salah satu question
        if not question and not program_specific_question:
            raise serializers.ValidationError(
                "Harus menyediakan 'question' atau 'program_specific_question'"
            )
        
        if question and program_specific_question:
            raise serializers.ValidationError(
                "Hanya boleh menyediakan 'question' ATAU 'program_specific_question', tidak keduanya"
            )

        # Tentukan question object dan tipe pertanyaan
        if question:
            question_obj = question
            question_type = question.question_type
        else:
            question_obj = program_specific_question
            question_type = program_specific_question.question_type

        # Validasi answer_value sesuai tipe pertanyaan
        if question_type == 'text':
            if not isinstance(answer_value, str):
                raise serializers.ValidationError(
                    "Jawaban untuk tipe 'text' harus berupa string"
                )
        
        elif question_type == 'number':
            try:
                float(answer_value)
            except (ValueError, TypeError):
                raise serializers.ValidationError(
                    "Jawaban untuk tipe 'number' harus berupa angka"
                )
        
        elif question_type in ['radio', 'dropdown']:
            # Single choice - harus string dan harus ada di options
            if not isinstance(answer_value, str):
                raise serializers.ValidationError(
                    f"Jawaban untuk tipe '{question_type}' harus berupa string"
                )
            if question_obj.options:
                try:
                    options = json.loads(question_obj.options) if isinstance(question_obj.options, str) else question_obj.options
                    if answer_value not in options:
                        raise serializers.ValidationError(
                            f"Jawaban '{answer_value}' tidak ada dalam pilihan yang tersedia"
                        )
                except (json.JSONDecodeError, TypeError):
                    # Jika options bukan JSON, anggap sebagai line-separated
                    options = question_obj.options.splitlines() if question_obj.options else []
                    if answer_value not in options:
                        raise serializers.ValidationError(
                            f"Jawaban '{answer_value}' tidak ada dalam pilihan yang tersedia"
                        )
        
        elif question_type == 'checkbox':
            # Multiple choice - harus array dan semua item harus ada di options
            if not isinstance(answer_value, (list, str)):
                raise serializers.ValidationError(
                    "Jawaban untuk tipe 'checkbox' harus berupa array/list"
                )
            
            # Jika string, coba parse sebagai JSON
            if isinstance(answer_value, str):
                try:
                    answer_value = json.loads(answer_value)
                except json.JSONDecodeError:
                    raise serializers.ValidationError(
                        "Jawaban untuk tipe 'checkbox' harus berupa JSON array yang valid"
                    )
            
            if not isinstance(answer_value, list):
                raise serializers.ValidationError(
                    "Jawaban untuk tipe 'checkbox' harus berupa array/list"
                )
            
            if question_obj.options:
                try:
                    options = json.loads(question_obj.options) if isinstance(question_obj.options, str) else question_obj.options
                    for ans in answer_value:
                        if ans not in options:
                            raise serializers.ValidationError(
                                f"Jawaban '{ans}' tidak ada dalam pilihan yang tersedia"
                            )
                except (json.JSONDecodeError, TypeError):
                    options = question_obj.options.splitlines() if question_obj.options else []
                    for ans in answer_value:
                        if ans not in options:
                            raise serializers.ValidationError(
                                f"Jawaban '{ans}' tidak ada dalam pilihan yang tersedia"
                            )
            
            # Simpan sebagai JSON string
            data['answer_value'] = json.dumps(answer_value)
        
        elif question_type == 'scale':
            # Scale 1-5 - harus angka antara 1-5
            try:
                scale_value = int(answer_value)
                if scale_value < 1 or scale_value > 5:
                    raise serializers.ValidationError(
                        "Jawaban untuk tipe 'scale' harus berupa angka antara 1-5"
                    )
            except (ValueError, TypeError):
                raise serializers.ValidationError(
                    "Jawaban untuk tipe 'scale' harus berupa angka antara 1-5"
                )

        return data

    def to_representation(self, instance):
        """
        Convert answer_value dari JSON string ke format yang sesuai saat membaca
        """
        rep = super().to_representation(instance)
        
        # Jika question_type adalah checkbox, parse JSON
        question_type = None
        if instance.question:
            question_type = instance.question.question_type
        elif instance.program_specific_question:
            question_type = instance.program_specific_question.question_type
        
        if question_type == 'checkbox':
            try:
                rep['answer_value'] = json.loads(instance.answer_value)
            except (json.JSONDecodeError, TypeError):
                rep['answer_value'] = instance.answer_value.splitlines() if instance.answer_value else []
        elif question_type == 'number' or question_type == 'scale':
            try:
                rep['answer_value'] = float(instance.answer_value) if '.' in str(instance.answer_value) else int(instance.answer_value)
            except (ValueError, TypeError):
                rep['answer_value'] = instance.answer_value
        
        return rep