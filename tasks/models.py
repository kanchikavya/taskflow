"""
Data models for Projects, Memberships, Tasks, and Comments in TaskFlow.
"""

from django.conf import settings
from django.db import models
from django.utils import timezone


class Project(models.Model):
    """
    Represents a workspace/project containing multiple tasks and team members.
    """

    name = models.CharField(
        max_length=150,
        help_text='Unique or descriptive name of the project'
    )
    description = models.TextField(
        blank=True,
        help_text='Detailed overview or goals of the project'
    )
    created_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='created_projects',
        help_text='User who created this project'
    )
    members = models.ManyToManyField(
        settings.AUTH_USER_MODEL,
        through='ProjectMembership',
        related_name='projects',
        blank=True,
        help_text='Team members assigned to this project'
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['created_at']),
        ]

    def is_member(self, user) -> bool:
        """Check if a given user is an assigned member, project creator, or admin."""
        if not user or not user.is_authenticated:
            return False
        if user.is_superuser or (hasattr(user, 'is_admin_role') and user.is_admin_role()) or user == self.created_by:
            return True
        return self.members.filter(id=user.id).exists()

    def __str__(self) -> str:
        return self.name


class ProjectMembership(models.Model):
    """
    Explicit intermediary table connecting Users to Projects.
    Enables storing membership metadata like joined date and enforcing unique pairing.
    """

    project = models.ForeignKey(
        Project,
        on_delete=models.CASCADE,
        related_name='memberships'
    )
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='project_memberships'
    )
    joined_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = 'Project Membership'
        verbose_name_plural = 'Project Memberships'
        constraints = [
            models.UniqueConstraint(
                fields=['project', 'user'],
                name='unique_project_membership'
            )
        ]

    def __str__(self) -> str:
        return f"{self.user.username} -> {self.project.name}"


class Task(models.Model):
    """
    An actionable work item within a project.
    Supports status tracking, priority, due dates, and assignee.
    """

    class Status(models.TextChoices):
        TODO = 'todo', 'To Do'
        IN_PROGRESS = 'in_progress', 'In Progress'
        DONE = 'done', 'Done'

    class Priority(models.TextChoices):
        LOW = 'low', 'Low'
        MEDIUM = 'medium', 'Medium'
        HIGH = 'high', 'High'
        URGENT = 'urgent', 'Urgent'

    title = models.CharField(
        max_length=200,
        help_text='Concise summary of the task'
    )
    description = models.TextField(
        blank=True,
        help_text='Detailed instructions, acceptance criteria, or context'
    )
    project = models.ForeignKey(
        Project,
        on_delete=models.CASCADE,
        related_name='tasks',
        help_text='Parent project'
    )
    status = models.CharField(
        max_length=20,
        choices=Status.choices,
        default=Status.TODO,
        help_text='Current progress status'
    )
    priority = models.CharField(
        max_length=20,
        choices=Priority.choices,
        default=Priority.MEDIUM,
        help_text='Urgency and importance rating'
    )
    due_date = models.DateField(
        null=True,
        blank=True,
        help_text='Expected completion deadline'
    )
    assigned_to = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='assigned_tasks',
        help_text='Team member responsible for this task'
    )
    created_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='created_tasks',
        help_text='Creator of the task'
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['due_date', '-created_at']
        indexes = [
            models.Index(fields=['project', 'status']),
            models.Index(fields=['assigned_to', 'status']),
            models.Index(fields=['due_date']),
        ]

    @property
    def is_overdue(self) -> bool:
        """Return True if due_date is in the past and task is not Done."""
        if self.due_date and self.status != self.Status.DONE:
            return self.due_date < timezone.localdate()
        return False

    def __str__(self) -> str:
        return f"[{self.get_status_display()}] {self.title}"


class TaskComment(models.Model):
    """
    User comments and collaboration history on a Task.
    """

    task = models.ForeignKey(
        Task,
        on_delete=models.CASCADE,
        related_name='comments',
        help_text='Task being discussed'
    )
    author = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='task_comments',
        help_text='Comment author'
    )
    content = models.TextField(
        help_text='Message text'
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['task', 'created_at']),
        ]

    def __str__(self) -> str:
        return f"Comment by {self.author.username} on #{self.task_id}"
