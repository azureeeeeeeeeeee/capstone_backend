from rest_framework.permissions import BasePermission

class SurveyPermissions(BasePermission):
    def has_permission(self, request, view):
        if request.method in ['POST', 'PUT', 'PATCH', 'DELETE']:
            return request.user.is_authenticated and request.user.role.name in ['Tracer', 'Admin']
        return True

class ProgramSpecificQuestionPermissions(BasePermission):
    def has_permission(self, request, view):
        if not request.user.is_authenticated or not request.user.role:
            return False

        role_name = request.user.role.name
        if request.method == 'GET':
            return True

        if role_name in ['Admin', 'Tracer']:
            return True

        if role_name == 'Tim Prodi':
            program_study_id = view.kwargs.get('program_study_id')
            if not program_study_id:
                return False
            return (
                request.user.program_study
                and str(request.user.program_study.id) == str(program_study_id)
            )

        return False

    

class UnitPermissions(BasePermission):
    def has_permission(self, request, view):
        if request.method in ['POST', 'PUT', 'PATCH', 'DELETE']:
            return request.user.is_authenticated and request.user.role.name in ['Admin']
        return True
    
class PeriodePermissions(BasePermission):
    def has_permission(self, request, view):
        return request.user.is_authenticated and request.user.role.name in ['Admin', 'Tracer']
    
class RolePermissions(BasePermission):
    def has_permission(self, request, view):
        return request.user.is_authenticated and request.user.role.name in ['Admin']
    
class UserPermissions(BasePermission):
    def has_permission(self, request, view):
        return request.user.is_authenticated and request.user.role.name in ['Admin']
class AnswerPermissions(BasePermission):
    def has_permission(self, request, view):
        if request.method in ['POST', 'GET']:
            return request.user.is_authenticated and request.user.role.name in ['Alumni']
        return True

class ConfigPermissions(BasePermission):
    def has_permission(self, request, view):
        return request.user.is_authenticated and request.user.role.name in ['Admin']