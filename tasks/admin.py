"""
Django admin panel registrations for Tasks app models.
"""

from django.contrib import admin
from .models import Project, ProjectMembership, Task, TaskComment


class ProjectMembershipInline(admin.TabularInline):
    """Allows assigning team members directly inside Project edit page."""
    model = ProjectMembership
    extra = 1
    autocomplete_fields = ('user',)


class TaskCommentInline(admin.TabularInline):
    """Displays task discussion history directly inside Task admin."""
    model = TaskComment
    extra = 0
    readonly_fields = ('author', 'created_at')


@admin.register(Project)
class ProjectAdmin(admin.ModelAdmin):
    list_display = ('name', 'created_by', 'member_count', 'created_at')
    search_fields = ('name', 'description', 'created_by__username')
    list_filter = ('created_at',)
    inlines = [ProjectMembershipInline]

    @admin.display(description='Total Members')
    def member_count(self, obj):
        return obj.members.count()


@admin.register(ProjectMembership)
class ProjectMembershipAdmin(admin.ModelAdmin):
    list_display = ('project', 'user', 'joined_at')
    list_filter = ('project', 'joined_at')
    search_fields = ('project__name', 'user__username', 'user__email')


@admin.register(Task)
class TaskAdmin(admin.ModelAdmin):
    list_display = (
        'title',
        'project',
        'priority',
        'status',
        'assigned_to',
        'due_date',
        'created_at',
    )
    list_filter = ('status', 'priority', 'project', 'due_date')
    search_fields = (
        'title',
        'description',
        'assigned_to__username',
        'project__name',
    )
    inlines = [TaskCommentInline]
    date_hierarchy = 'due_date'
    list_editable = ('status', 'priority')


@admin.register(TaskComment)
class TaskCommentAdmin(admin.ModelAdmin):
    list_display = ('task', 'author', 'short_content', 'created_at')
    list_filter = ('created_at',)
    search_fields = ('content', 'author__username', 'task__title')

    @admin.display(description='Comment Content')
    def short_content(self, obj):
        return obj.content[:50] + ('...' if len(obj.content) > 50 else '')
