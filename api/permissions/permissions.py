from rest_framework.permissions import BasePermission

class SurveyPermissions(BasePermission):
    def has_permission(self, request, view):
        if request.method in ['POST', 'PUT', 'PATCH', 'DELETE']:
            return request.user.is_authenticated and request.user.role.name in ['Tracer', 'Admin']
        return True
