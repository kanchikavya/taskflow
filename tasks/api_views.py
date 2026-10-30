"""
DRF ViewSets for Projects, Tasks, and Comments.

ViewSets bundle standard REST operations (list, retrieve, create, update, partial_update, destroy)
into organized, highly reusable classes with built-in search, filtering, and pagination.
"""

from django.db.models import Q
import logging
from rest_framework import viewsets, permissions, filters, status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.exceptions import PermissionDenied

from .models import Project, Task, TaskComment
from .serializers import ProjectSerializer, TaskSerializer, TaskCommentSerializer
from .permissions import IsProjectMemberOrAdmin

logger = logging.getLogger('tasks')


class ProjectViewSet(viewsets.ModelViewSet):
    """
    CRUD ViewSet for Projects.
    - List: Accessible projects for the user.
    - Create: Restricted to Managers and Admins.
    - Search: ?search=<term> (matches name and description).
    """

    serializer_class = ProjectSerializer
    permission_classes = [permissions.IsAuthenticated, IsProjectMemberOrAdmin]
    filter_backends = [filters.SearchFilter, filters.OrderingFilter]
    search_fields = ['name', 'description']
    ordering_fields = ['name', 'created_at']
    ordering = ['-created_at']

    def get_queryset(self):
        user = self.request.user
        if not user.is_authenticated:
            return Project.objects.none()
        if user.is_admin_role():
            return Project.objects.all().select_related('created_by').prefetch_related('members')
        return Project.objects.filter(
            Q(created_by=user) | Q(members=user)
        ).distinct().select_related('created_by').prefetch_related('members')

    def perform_create(self, serializer):
        # Enforce role restriction: Only Managers and Admins can create projects
        if not self.request.user.is_manager_role():
            raise PermissionDenied("Only Managers and Admins can create projects.")
        serializer.save(created_by=self.request.user)


class TaskViewSet(viewsets.ModelViewSet):
    """
    CRUD ViewSet for Tasks.
    Features:
    - Query Filtering: ?status=todo&priority=high&project=1&assigned_to=me
    - Search: ?search=caching (searches title & description)
    - Ordering: ?ordering=due_date or ?ordering=-created_at
    - Custom Endpoint: PATCH /api/tasks/{id}/update-status/ for Kanban updates
    """

    serializer_class = TaskSerializer
    permission_classes = [permissions.IsAuthenticated, IsProjectMemberOrAdmin]
    filter_backends = [filters.SearchFilter, filters.OrderingFilter]
    search_fields = ['title', 'description']
    ordering_fields = ['due_date', 'priority', 'status', 'created_at']
    ordering = ['due_date', '-created_at']

    def get_queryset(self):
        user = self.request.user
        if not user.is_authenticated:
            return Task.objects.none()

        if user.is_admin_role():
            qs = Task.objects.all()
        else:
            qs = Task.objects.filter(
                Q(project__members=user) | Q(project__created_by=user)
            ).distinct()

        # Optimize queries to avoid N+1 problem
        qs = qs.select_related('project', 'assigned_to', 'created_by')

        # Query Parameter Filtering
        status_param = self.request.query_params.get('status')
        priority_param = self.request.query_params.get('priority')
        project_param = self.request.query_params.get('project')
        assigned_param = self.request.query_params.get('assigned_to')

        if status_param:
            qs = qs.filter(status=status_param)
        if priority_param:
            qs = qs.filter(priority=priority_param)
        if project_param:
            qs = qs.filter(project_id=project_param)
        if assigned_param:
            if assigned_param.lower() == 'me':
                qs = qs.filter(assigned_to=user)
            elif assigned_param.isdigit():
                qs = qs.filter(assigned_to_id=assigned_param)

        return qs

    def perform_create(self, serializer):
        # Automatically assign task creator
        project = serializer.validated_data.get('project')
        if not project.is_member(self.request.user):
            raise PermissionDenied("You must be a member of the project to add tasks.")
        serializer.save(created_by=self.request.user)

    @action(detail=True, methods=['patch'], url_path='update-status')
    def update_status(self, request, pk=None):
        """
        Lightweight endpoint specifically for Kanban board drag & drop.
        Payload: { "status": "in_progress" }
        """
        task = self.get_object()
        new_status = request.data.get('status')

        valid_statuses = [choice[0] for choice in Task.Status.choices]
        if new_status not in valid_statuses:
            return Response(
                {"error": f"Invalid status. Choose from: {valid_statuses}"},
                status=status.HTTP_400_BAD_REQUEST
            )

        old_status = task.status
        task.status = new_status
        task.save(update_fields=['status', 'updated_at'])

        logger.info(
            "Task #%s ('%s') status transitioned: %s -> %s by user '%s'",
            task.id, task.title, old_status, new_status, request.user.username
        )

        serializer = self.get_serializer(task)
        return Response(serializer.data, status=status.HTTP_200_OK)


class TaskCommentViewSet(viewsets.ModelViewSet):
    """
    CRUD ViewSet for Task Comments.
    Filtering: ?task=<task_id> returns comments for that specific task.
    """

    serializer_class = TaskCommentSerializer
    permission_classes = [permissions.IsAuthenticated, IsProjectMemberOrAdmin]
    filter_backends = [filters.OrderingFilter]
    ordering = ['-created_at']

    def get_queryset(self):
        user = self.request.user
        if not user.is_authenticated:
            return TaskComment.objects.none()

        if user.is_admin_role():
            qs = TaskComment.objects.all()
        else:
            qs = TaskComment.objects.filter(
                Q(task__project__members=user) | Q(task__project__created_by=user)
            ).distinct()

        qs = qs.select_related('author', 'task')

        task_param = self.request.query_params.get('task')
        if task_param:
            qs = qs.filter(task_id=task_param)

        return qs

    def perform_create(self, serializer):
        task = serializer.validated_data.get('task')
        if not task.project.is_member(self.request.user):
            raise PermissionDenied("You must be a member of the project to comment on this task.")
        serializer.save(author=self.request.user)
