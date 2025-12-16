from rest_framework.permissions import BasePermission

class SurveyPermissions(BasePermission):
    def has_permission(self, request, view):
        if request.method in ['POST', 'PUT', 'PATCH', 'DELETE']:
            return request.user.is_authenticated and request.user.role.name in ['Tracer', 'Admin']
        return True

class ProgramSpecificQuestionPermissions(BasePermission):
    def has_permission(self, request, view):
        user = request.user
        if not user.is_authenticated or not user.role:
            return False

        role = user.role.name

        # Semua boleh lihat
        if request.method == 'GET':
            return True

        # Admin & Tracer full akses
        if role in ['Admin', 'Tracer']:
            return True

        # Tim Prodi hanya prodi sendiri
        if role == 'Tim Prodi':
            program_study_id = view.kwargs.get('program_study_id')
            return (
                user.program_study
                and str(user.program_study.id) == str(program_study_id)
            )

        return False


    

class UnitPermissions(BasePermission):
    def has_permission(self, request, view):
        if request.method in ['POST', 'PUT', 'PATCH', 'DELETE']:
            return request.user.is_authenticated and request.user.role.name in ['Admin']
        return True
    
# class PeriodePermissions(BasePermission):
#     def has_permission(self, request, view):
#         return request.user.is_authenticated and request.user.role.name in ['Admin', 'Tracer']
class PeriodePermissions(BasePermission):
    def has_permission(self, request, view):
        if request.method == 'GET':
            return request.user.is_authenticated
        return (
            request.user.is_authenticated
            and request.user.role.name in ['Admin', 'Tracer']
        )

    
class RolePermissions(BasePermission):
    def has_permission(self, request, view):
        return request.user.is_authenticated and request.user.role.name in ['Admin']
    
class UserPermissions(BasePermission):
    def has_permission(self, request, view):
        if request.method == 'GET':
            return request.user.is_authenticated and request.user.role.name in ['Admin', 'Tracer', 'Tim Prodi', 'Pimpinan Unit']
        return request.user.is_authenticated and request.user.role.name in ['Admin']

class AnswerPermissions(BasePermission):
    def has_permission(self, request, view):
        if request.method in ['POST', 'GET']:
            return request.user.is_authenticated and request.user.role.name in ['Alumni']
        return True

class ConfigPermissions(BasePermission):
    def has_permission(self, request, view):
        return request.user.is_authenticated and request.user.role.name in ['Admin']