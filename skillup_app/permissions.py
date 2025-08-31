from rest_framework.permissions import BasePermission, SAFE_METHODS


class IsAdmin(BasePermission):
    def has_permission(self, request, view):
        return bool(request.user and request.user.is_authenticated and request.user.is_staff)


class IsAssignee(BasePermission):
    def has_object_permission(self, request, view, obj):
        return bool(request.user and request.user.is_athenticated and obj.student_id == request.user.id)
