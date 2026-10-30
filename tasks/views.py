"""
Views for Dashboard, Project management, Task management, and Comments.
Demonstrates select_related, prefetch_related, and role-based permissions.
"""

from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.core.exceptions import PermissionDenied
from django.db.models import Count, Q
from django.utils import timezone

from .models import Project, ProjectMembership, Task, TaskComment
from .forms import ProjectForm, TaskForm, TaskCommentForm


def get_user_projects_queryset(user):
    """
    Helper function returning projects accessible to the user.
    Admins see all projects; managers and members see projects they belong to or created.
    """
    if user.is_admin_role():
        return Project.objects.all()
    return Project.objects.filter(Q(created_by=user) | Q(members=user)).distinct()


@login_required
def dashboard_view(request):
    """
    User dashboard displaying key metrics:
    - Total accessible projects
    - Task counts grouped by status (To Do, In Progress, Done)
    - Overdue tasks
    - 'My Assigned Tasks' (tasks assigned to current user)
    """
    accessible_projects = get_user_projects_queryset(request.user)

    # All tasks within accessible projects
    tasks_qs = Task.objects.filter(project__in=accessible_projects)

    # Aggregate status counts efficiently
    status_counts = {
        'todo': tasks_qs.filter(status=Task.Status.TODO).count(),
        'in_progress': tasks_qs.filter(status=Task.Status.IN_PROGRESS).count(),
        'done': tasks_qs.filter(status=Task.Status.DONE).count(),
        'total': tasks_qs.count(),
    }

    # Overdue tasks (due date past and not done)
    today = timezone.localdate()
    overdue_tasks = tasks_qs.filter(
        due_date__lt=today
    ).exclude(
        status=Task.Status.DONE
    ).select_related('project', 'assigned_to').order_by('due_date')[:5]

    # Tasks assigned specifically to request.user (Avoid N+1 using select_related)
    my_tasks = Task.objects.filter(
        assigned_to=request.user
    ).select_related('project').order_by('due_date', '-created_at')[:8]

    # Recent projects with preloaded members
    recent_projects = accessible_projects.prefetch_related('members').annotate(
        task_count=Count('tasks')
    ).order_by('-created_at')[:4]

    context = {
        'status_counts': status_counts,
        'overdue_tasks': overdue_tasks,
        'my_tasks': my_tasks,
        'recent_projects': recent_projects,
        'total_projects_count': accessible_projects.count(),
    }
    return render(request, 'tasks/dashboard.html', context)


@login_required
def project_list_view(request):
    """List all projects accessible to the current user."""
    projects = get_user_projects_queryset(request.user).select_related(
        'created_by'
    ).prefetch_related(
        'members'
    ).annotate(
        task_count=Count('tasks')
    ).order_by('-created_at')

    return render(request, 'tasks/project_list.html', {'projects': projects})


@login_required
def project_detail_view(request, pk):
    """
    Detailed view of a project, its members, and its tasks.
    Supports query parameter filtering: ?status=&priority=
    """
    project = get_object_or_404(
        Project.objects.prefetch_related('members', 'memberships__user'),
        pk=pk
    )

    # Permission check: user must be member, creator, or admin
    if not project.is_member(request.user):
        messages.error(request, 'You do not have permission to view this project.')
        return redirect('tasks:dashboard')

    tasks = project.tasks.select_related('assigned_to', 'created_by')

    # Optional query filtering (?status=todo&priority=high)
    status_filter = request.GET.get('status', '').strip()
    priority_filter = request.GET.get('priority', '').strip()

    if status_filter:
        tasks = tasks.filter(status=status_filter)
    if priority_filter:
        tasks = tasks.filter(priority=priority_filter)

    context = {
        'project': project,
        'tasks': tasks,
        'status_choices': Task.Status.choices,
        'priority_choices': Task.Priority.choices,
        'selected_status': status_filter,
        'selected_priority': priority_filter,
    }
    return render(request, 'tasks/project_detail.html', context)


@login_required
def project_kanban_view(request, pk):
    """
    Interactive Kanban Board for a specific project.
    Loads tasks grouped by status (To Do, In Progress, Done) and connects
    to the DRF REST API without page reloads.
    """
    project = get_object_or_404(
        Project.objects.prefetch_related('members'),
        pk=pk
    )

    if not project.is_member(request.user):
        messages.error(request, 'You do not have permission to view this project.')
        return redirect('tasks:dashboard')

    # Efficient single-query retrieval with select_related avoiding N+1
    tasks = list(project.tasks.select_related('assigned_to', 'created_by').prefetch_related('comments'))

    todo_tasks = [t for t in tasks if t.status == Task.Status.TODO]
    in_progress_tasks = [t for t in tasks if t.status == Task.Status.IN_PROGRESS]
    done_tasks = [t for t in tasks if t.status == Task.Status.DONE]

    user_projects = get_user_projects_queryset(request.user).only('id', 'name')

    context = {
        'project': project,
        'todo_tasks': todo_tasks,
        'in_progress_tasks': in_progress_tasks,
        'done_tasks': done_tasks,
        'user_projects': user_projects,
    }
    return render(request, 'tasks/kanban.html', context)


@login_required
def project_create_view(request):
    """Create a new project. Allowed for Managers and Admins."""
    if not request.user.is_manager_role():
        messages.error(request, 'Only Managers or Admins can create new projects.')
        return redirect('tasks:project_list')

    if request.method == 'POST':
        form = ProjectForm(request.POST)
        if form.is_valid():
            project = form.save(commit=False)
            project.created_by = request.user
            project.save()
            form.save_m2m()

            # Ensure creator is automatically a member
            ProjectMembership.objects.get_or_create(project=project, user=request.user)

            messages.success(request, f'Project "{project.name}" has been created!')
            return redirect('tasks:project_detail', pk=project.pk)
    else:
        form = ProjectForm()

    return render(request, 'tasks/project_form.html', {'form': form, 'title': 'Create New Project'})


@login_required
def project_update_view(request, pk):
    """Update project details. Only creator, manager, or admin allowed."""
    project = get_object_or_404(Project, pk=pk)

    if not (request.user.is_admin_role() or project.created_by == request.user):
        messages.error(request, 'You do not have permission to edit this project.')
        return redirect('tasks:project_detail', pk=project.pk)

    if request.method == 'POST':
        form = ProjectForm(request.POST, instance=project)
        if form.is_valid():
            form.save()
            messages.success(request, f'Project "{project.name}" updated successfully.')
            return redirect('tasks:project_detail', pk=project.pk)
    else:
        form = ProjectForm(instance=project)

    return render(request, 'tasks/project_form.html', {'form': form, 'title': f'Edit Project: {project.name}'})


@login_required
def project_delete_view(request, pk):
    """Delete a project. Only creator or admin allowed."""
    project = get_object_or_404(Project, pk=pk)

    if not (request.user.is_admin_role() or project.created_by == request.user):
        messages.error(request, 'You do not have permission to delete this project.')
        return redirect('tasks:project_detail', pk=project.pk)

    if request.method == 'POST':
        project_name = project.name
        project.delete()
        messages.success(request, f'Project "{project_name}" was deleted.')
        return redirect('tasks:project_list')

    return render(request, 'tasks/confirm_delete.html', {
        'object_name': f'Project "{project.name}"',
        'cancel_url': project_detail_view,
        'item': project,
    })


@login_required
def task_create_view(request):
    """Create a new task within an accessible project."""
    project_id = request.GET.get('project')
    initial_project = None
    if project_id:
        initial_project = get_object_or_404(Project, pk=project_id)
        if not initial_project.is_member(request.user):
            messages.error(request, 'You must be a member of this project to add tasks.')
            return redirect('tasks:project_list')

    if request.method == 'POST':
        form = TaskForm(request.POST, user=request.user, project=initial_project)
        if form.is_valid():
            task = form.save(commit=False)
            task.created_by = request.user
            task.save()
            messages.success(request, f'Task "{task.title}" created successfully!')
            return redirect('tasks:task_detail', pk=task.pk)
    else:
        form = TaskForm(user=request.user, project=initial_project, initial={'project': initial_project})

    return render(request, 'tasks/task_form.html', {
        'form': form,
        'title': 'Create New Task',
        'project': initial_project,
        'has_projects': form.fields['project'].queryset.exists(),
    })


@login_required
def task_detail_view(request, pk):
    """
    Task detail view showing description, status, priority, due date, assignee,
    and a comment timeline with inline comment posting.
    """
    task = get_object_or_404(
        Task.objects.select_related('project', 'assigned_to', 'created_by'),
        pk=pk
    )

    if not task.project.is_member(request.user):
        messages.error(request, 'You do not have permission to view this task.')
        return redirect('tasks:dashboard')

    # Comment submission handling
    if request.method == 'POST':
        comment_form = TaskCommentForm(request.POST)
        if comment_form.is_valid():
            comment = comment_form.save(commit=False)
            comment.task = task
            comment.author = request.user
            comment.save()
            messages.success(request, 'Comment added.')
            return redirect('tasks:task_detail', pk=task.pk)
    else:
        comment_form = TaskCommentForm()

    comments = task.comments.select_related('author').order_by('-created_at')

    context = {
        'task': task,
        'comments': comments,
        'comment_form': comment_form,
    }
    return render(request, 'tasks/task_detail.html', context)


@login_required
def task_update_view(request, pk):
    """Update task status, priority, assignee, description, or due date."""
    task = get_object_or_404(Task.objects.select_related('project'), pk=pk)

    if not task.project.is_member(request.user):
        messages.error(request, 'You do not have permission to modify this task.')
        return redirect('tasks:dashboard')

    if request.method == 'POST':
        form = TaskForm(request.POST, instance=task, project=task.project)
        if form.is_valid():
            form.save()
            messages.success(request, f'Task "{task.title}" updated successfully.')
            return redirect('tasks:task_detail', pk=task.pk)
    else:
        form = TaskForm(instance=task, project=task.project)

    return render(request, 'tasks/task_form.html', {
        'form': form,
        'title': f'Edit Task: {task.title}',
        'task': task,
    })


@login_required
def task_delete_view(request, pk):
    """Delete a task."""
    task = get_object_or_404(Task.objects.select_related('project'), pk=pk)

    # Only task creator, project creator, or admin can delete
    can_delete = (
        request.user.is_admin_role() or
        task.created_by == request.user or
        task.project.created_by == request.user
    )
    if not can_delete:
        messages.error(request, 'You do not have permission to delete this task.')
        return redirect('tasks:task_detail', pk=task.pk)

    project_pk = task.project.pk
    if request.method == 'POST':
        task_title = task.title
        task.delete()
        messages.success(request, f'Task "{task_title}" was deleted.')
        return redirect('tasks:project_detail', pk=project_pk)

    return render(request, 'tasks/confirm_delete.html', {
        'object_name': f'Task "{task.title}"',
        'item': task,
    })


def custom_404_view(request, exception=None):
    """Custom 404 Not Found error handler."""
    return render(request, '404.html', status=404)


def custom_403_view(request, exception=None):
    """Custom 403 Forbidden error handler."""
    return render(request, '403.html', status=403)


def custom_500_view(request):
    """Custom 500 Server Error handler."""
    return render(request, '500.html', status=500)
