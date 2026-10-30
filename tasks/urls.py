"""
URL routing for Projects, Tasks, and Dashboard.
"""

from django.urls import path
from . import views

app_name = 'tasks'

urlpatterns = [
    # Dashboard
    path('', views.dashboard_view, name='dashboard'),

    # Projects
    path('projects/', views.project_list_view, name='project_list'),
    path('projects/create/', views.project_create_view, name='project_create'),
    path('projects/<int:pk>/', views.project_detail_view, name='project_detail'),
    path('projects/<int:pk>/kanban/', views.project_kanban_view, name='project_kanban'),
    path('projects/<int:pk>/edit/', views.project_update_view, name='project_update'),
    path('projects/<int:pk>/delete/', views.project_delete_view, name='project_delete'),

    # Tasks
    path('tasks/create/', views.task_create_view, name='task_create'),
    path('tasks/<int:pk>/', views.task_detail_view, name='task_detail'),
    path('tasks/<int:pk>/edit/', views.task_update_view, name='task_update'),
    path('tasks/<int:pk>/delete/', views.task_delete_view, name='task_delete'),
]
