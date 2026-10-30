"""
Custom DRF Permissions for TaskFlow.

Enforces that only members of a project (or Admins) can view, create, or modify
its tasks and comments.
"""

from rest_framework import permissions


class IsProjectMemberOrAdmin(permissions.BasePermission):
    """
    Object-level permission allowing access only to project members or system Admins.
    """

    def has_permission(self, request, view):
        # Must be authenticated to access any TaskFlow API endpoint
        return bool(request.user and request.user.is_authenticated)

    def has_object_permission(self, request, view, obj):
        user = request.user

        # Admins and Superusers have global permissions
        if user.is_superuser or (hasattr(user, 'is_admin_role') and user.is_admin_role()):
            return True

        # Check permission based on the target object type
        # 1. Project instance
        if hasattr(obj, 'is_member'):
            return obj.is_member(user)

        # 2. Task instance (check parent project)
        if hasattr(obj, 'project'):
            return obj.project.is_member(user)

        # 3. TaskComment instance (check parent task's project)
        if hasattr(obj, 'task') and hasattr(obj.task, 'project'):
            return obj.task.project.is_member(user)

        return False
