from rest_framework.permissions import BasePermission

class SurveyPermissions(BasePermission):
    def has_permission(self, request, view):
        if request.method in ['POST', 'PUT', 'PATCH', 'DELETE']:
            return request.user.is_authenticated and request.user.role.name in ['Tracer', 'Admin']
        return True

class ProgramSpecificQuestionPermissions(BasePermission):
    def has_permission(self, request, view):
        if request.method in ['GET']:
            return request.user.is_authenticated
        
        if not request.user.is_authenticated or not request.user.role:
            return False

        role_name = request.user.role.name

        if role_name in ['Admin', 'Tracer']:
            return True

        if role_name.startswith("Prodi "):
            program_study_id = view.kwargs.get('program_study_id')
            from api.models import ProgramStudy
            try:
                program = ProgramStudy.objects.get(id=program_study_id)
            except ProgramStudy.DoesNotExist:
                return False
            expected_role = f"Prodi {program.name}"
            return role_name == expected_role

        return False