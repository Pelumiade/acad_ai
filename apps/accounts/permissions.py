from rest_framework.permissions import BasePermission


class IsStudent(BasePermission):
    """Only students can access this endpoint."""

    def has_permission(self, request, view):
        return request.user and request.user.is_authenticated and request.user.role == "STUDENT"


class IsInstructor(BasePermission):
    """Only instructors can access this endpoint."""

    def has_permission(self, request, view):
        return request.user and request.user.is_authenticated and request.user.role == "INSTRUCTOR"


class IsOwner(BasePermission):
    """User can only access their own objects."""

    def has_object_permission(self, request, view, obj):
        if hasattr(obj, "student"):
            return obj.student == request.user
        if hasattr(obj, "user"):
            return obj.user == request.user
        return False
