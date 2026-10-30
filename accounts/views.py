"""
Views for User Authentication (Registration, Login, Logout) in TaskFlow.
"""

from django.shortcuts import render, redirect
from django.contrib.auth import login, logout
from django.contrib import messages
from .forms import UserRegisterForm, UserLoginForm


def register_view(request):
    """Handles new user account registration."""
    if request.user.is_authenticated:
        return redirect('tasks:dashboard')

    if request.method == 'POST':
        form = UserRegisterForm(request.POST)
        if form.is_valid():
            user = form.save()

            # Auto-assign newly registered users to default workspace project if present
            from tasks.models import Project, ProjectMembership
            default_project = Project.objects.order_by('created_at').first()
            if default_project:
                ProjectMembership.objects.get_or_create(project=default_project, user=user)

            login(request, user)
            messages.success(request, f'Welcome to TaskFlow, {user.first_name or user.username}! Your account has been created.')
            return redirect('tasks:dashboard')
        else:
            messages.error(request, 'Please correct the errors below.')
    else:
        form = UserRegisterForm()

    return render(request, 'accounts/register.html', {'form': form})


def login_view(request):
    """Handles user authentication and login."""
    if request.user.is_authenticated:
        return redirect('tasks:dashboard')

    if request.method == 'POST':
        form = UserLoginForm(request, data=request.POST)
        if form.is_valid():
            user = form.get_user()
            login(request, user)
            messages.success(request, f'Welcome back, {user.username}!')
            next_url = request.GET.get('next')
            if next_url:
                return redirect(next_url)
            return redirect('tasks:dashboard')
        else:
            messages.error(request, 'Invalid username or password.')
    else:
        form = UserLoginForm()

    return render(request, 'accounts/login.html', {'form': form})


def logout_view(request):
    """Logs out the active user and redirects to login."""
    logout(request)
    messages.info(request, 'You have been successfully logged out.')
    return redirect('accounts:login')
