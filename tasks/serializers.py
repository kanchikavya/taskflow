"""
Serializers for Projects, Tasks, and Comments.

Serializers in DRF handle two-way translation:
1. Serialization: Django Model instances -> Python dicts -> JSON output
2. Deserialization & Validation: Incoming JSON payload -> Python data -> Validated Model instances
"""

from django.contrib.auth import get_user_model
from django.utils import timezone
from rest_framework import serializers

from .models import Project, Task, TaskComment

User = get_user_model()


class UserSummarySerializer(serializers.ModelSerializer):
    """Compact user representation for nested API responses."""

    class Meta:
        model = User
        fields = ('id', 'username', 'email', 'first_name', 'last_name', 'role')
        read_only_fields = fields


class TaskCommentSerializer(serializers.ModelSerializer):
    """Serializer for Task comments."""

    author = UserSummarySerializer(read_only=True)

    class Meta:
        model = TaskComment
        fields = ('id', 'task', 'author', 'content', 'created_at', 'updated_at')
        read_only_fields = ('id', 'author', 'created_at', 'updated_at')

    def create(self, validated_data):
        # Automatically set current authenticated user as comment author
        validated_data['author'] = self.context['request'].user
        return super().create(validated_data)


class TaskSerializer(serializers.ModelSerializer):
    """
    Serializer for Tasks with custom validation and nested summaries.
    """

    project_name = serializers.CharField(source='project.name', read_only=True)
    assigned_to_username = serializers.CharField(source='assigned_to.username', read_only=True, default=None)
    created_by = UserSummarySerializer(read_only=True)
    is_overdue = serializers.BooleanField(read_only=True)

    class Meta:
        model = Task
        fields = (
            'id',
            'title',
            'description',
            'project',
            'project_name',
            'status',
            'priority',
            'due_date',
            'assigned_to',
            'assigned_to_username',
            'created_by',
            'is_overdue',
            'created_at',
            'updated_at',
        )
        read_only_fields = ('id', 'created_by', 'is_overdue', 'created_at', 'updated_at')

    def validate_due_date(self, value):
        """
        Field-level validation: Due date cannot be set in the past.
        """
        if value and value < timezone.localdate():
            # If editing and the due date is untouched, let it pass
            if self.instance and self.instance.due_date == value:
                return value
            raise serializers.ValidationError("Due date cannot be in the past.")
        return value

    def validate(self, attrs):
        """
        Object-level validation:
        1. Verifies that the assignee (if provided) is actually a member of the project.
        """
        project = attrs.get('project') or (self.instance.project if self.instance else None)
        assigned_to = attrs.get('assigned_to', getattr(self.instance, 'assigned_to', None))

        if project and assigned_to:
            if not project.is_member(assigned_to):
                raise serializers.ValidationError({
                    'assigned_to': f"User '{assigned_to.username}' is not a member of project '{project.name}'."
                })

        return attrs

    def create(self, validated_data):
        # Automatically assign task creator to current user
        validated_data['created_by'] = self.context['request'].user
        return super().create(validated_data)


class ProjectSerializer(serializers.ModelSerializer):
    """Serializer for Projects with task count and member summaries."""

    created_by = UserSummarySerializer(read_only=True)
    member_count = serializers.IntegerField(source='members.count', read_only=True)
    task_count = serializers.IntegerField(source='tasks.count', read_only=True)

    class Meta:
        model = Project
        fields = (
            'id',
            'name',
            'description',
            'created_by',
            'members',
            'member_count',
            'task_count',
            'created_at',
            'updated_at',
        )
        read_only_fields = ('id', 'created_by', 'member_count', 'task_count', 'created_at', 'updated_at')

    def create(self, validated_data):
        members = validated_data.pop('members', [])
        user = self.context['request'].user
        project = Project.objects.create(created_by=user, **validated_data)

        # Set members and ensure creator is included
        project.members.set(members)
        project.members.add(user)
        return project
