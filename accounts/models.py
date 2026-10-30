"""
Custom User model for TaskFlow.

Inherits from Django's AbstractUser to enable custom roles (Admin, Manager, Member)
while keeping built-in authentication, password hashing, and permissions intact.
"""

from django.contrib.auth.models import AbstractUser
from django.db import models


class User(AbstractUser):
    """
    Custom user model with explicit organization roles.

    Roles:
    - Admin: Full system access across all projects and tasks.
    - Manager: Can create projects, add/remove members, and manage tasks.
    - Member: Can view assigned projects, update task statuses, and comment.
    """

    class Role(models.TextChoices):
        ADMIN = 'admin', 'Admin'
        MANAGER = 'manager', 'Manager'
        MEMBER = 'member', 'Member'

    role = models.CharField(
        max_length=20,
        choices=Role.choices,
        default=Role.MEMBER,
        help_text='Defines authorization level within TaskFlow.'
    )

    def is_admin_role(self) -> bool:
        """Return True if user has Admin role or is Django superuser."""
        return self.role == self.Role.ADMIN or self.is_superuser

    def is_manager_role(self) -> bool:
        """Return True if user has Manager or Admin role, or is superuser."""
        return self.role in {self.Role.ADMIN, self.Role.MANAGER} or self.is_superuser

    def is_member_role(self) -> bool:
        """Return True if user is a standard Member."""
        return self.role == self.Role.MEMBER

    def __str__(self) -> str:
        return f"{self.username} ({self.get_role_display()})"
