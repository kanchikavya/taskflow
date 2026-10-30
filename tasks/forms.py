"""
Forms for Project and Task management in TaskFlow.
"""

from django import forms
from django.contrib.auth import get_user_model
from .models import Project, Task, TaskComment

User = get_user_model()


class ProjectForm(forms.ModelForm):
    """Form to create and update Projects."""

    members = forms.ModelMultipleChoiceField(
        queryset=User.objects.filter(is_active=True).order_by('username'),
        widget=forms.SelectMultiple(attrs={'class': 'form-select', 'size': '5'}),
        required=False,
        help_text='Hold Ctrl (or Cmd on Mac) to select multiple members.'
    )

    class Meta:
        model = Project
        fields = ('name', 'description', 'members')
        widgets = {
            'name': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'e.g., E-Commerce API Redesign'}),
            'description': forms.Textarea(attrs={'class': 'form-control', 'rows': 4, 'placeholder': 'Project objectives, scope, and deliverables...'}),
        }


class TaskForm(forms.ModelForm):
    """Form to create and update Tasks with project-scoped member assignment."""

    class Meta:
        model = Task
        fields = ('title', 'description', 'project', 'priority', 'status', 'due_date', 'assigned_to')
        widgets = {
            'title': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'e.g., Set up Redis caching layer'}),
            'description': forms.Textarea(attrs={'class': 'form-control', 'rows': 4, 'placeholder': 'Detailed specifications or acceptance criteria...'}),
            'project': forms.Select(attrs={'class': 'form-select'}),
            'priority': forms.Select(attrs={'class': 'form-select'}),
            'status': forms.Select(attrs={'class': 'form-select'}),
            'due_date': forms.DateInput(attrs={'class': 'form-control', 'type': 'date'}),
            'assigned_to': forms.Select(attrs={'class': 'form-select'}),
        }

    def __init__(self, *args, user=None, project=None, **kwargs):
        super().__init__(*args, **kwargs)
        from django.db.models import Q

        # Restrict projects to those accessible by the user (unless Admin/Superuser)
        if user and not user.is_superuser and user.role != User.Role.ADMIN:
            accessible_projects = Project.objects.filter(
                Q(created_by=user) | Q(members=user)
            ).distinct()
        else:
            accessible_projects = Project.objects.all()

        self.fields['project'].queryset = accessible_projects

        # Auto-select the project if user only has access to one, or if passed via query param
        if project:
            self.initial['project'] = project
        elif accessible_projects.count() == 1 and not self.initial.get('project'):
            self.initial['project'] = accessible_projects.first()

        # Target project for assignee filtering
        target_project = project or (self.instance.project if self.instance and self.instance.pk else None)
        if not target_project and self.initial.get('project'):
            target_project = self.initial.get('project')

        if target_project:
            self.fields['assigned_to'].queryset = target_project.members.filter(is_active=True)
        else:
            self.fields['assigned_to'].queryset = User.objects.filter(is_active=True)


class TaskCommentForm(forms.ModelForm):
    """Quick inline form for posting comments on tasks."""

    class Meta:
        model = TaskComment
        fields = ('content',)
        widgets = {
            'content': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 3,
                'placeholder': 'Add a note or update progress on this task...'
            })
        }
