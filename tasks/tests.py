"""
Comprehensive Unit Test Suite for TaskFlow.

Covers:
1. Model logic & constraints (roles, membership, overdue calculation)
2. Template views & access control (dashboard, project detail, kanban)
3. DRF REST API (token auth, serializers, validation rules, filtering, status updates)
"""

from datetime import timedelta
from django.test import TestCase, Client
from django.contrib.auth import get_user_model
from django.urls import reverse
from django.utils import timezone
from rest_framework import status
from rest_framework.test import APITestCase
from rest_framework.authtoken.models import Token

from .models import Project, ProjectMembership, Task, TaskComment

User = get_user_model()


class ModelTests(TestCase):
    """Unit tests for Accounts and Tasks database models."""

    def setUp(self):
        self.admin = User.objects.create_user(
            username='admin_test',
            email='admin@test.com',
            password='password123',
            role=User.Role.ADMIN
        )
        self.manager = User.objects.create_user(
            username='manager_test',
            email='manager@test.com',
            password='password123',
            role=User.Role.MANAGER
        )
        self.member = User.objects.create_user(
            username='member_test',
            email='member@test.com',
            password='password123',
            role=User.Role.MEMBER
        )

        self.project = Project.objects.create(
            name='Test Project',
            description='Test Description',
            created_by=self.manager
        )
        ProjectMembership.objects.create(project=self.project, user=self.manager)
        ProjectMembership.objects.create(project=self.project, user=self.member)

    def test_user_role_methods(self):
        """Test user role verification helper methods."""
        self.assertTrue(self.admin.is_admin_role())
        self.assertTrue(self.manager.is_manager_role())
        self.assertFalse(self.member.is_manager_role())
        self.assertTrue(self.member.is_member_role())

    def test_project_membership_check(self):
        """Test is_member() method on Project model."""
        outsider = User.objects.create_user(username='outsider', password='password123')

        self.assertTrue(self.project.is_member(self.manager))
        self.assertTrue(self.project.is_member(self.member))
        self.assertTrue(self.project.is_member(self.admin))  # Admins always have access
        self.assertFalse(self.project.is_member(outsider))

    def test_task_is_overdue_property(self):
        """Test computed property is_overdue on Task model."""
        today = timezone.localdate()

        # Task due yesterday and still In Progress -> OVERDUE
        overdue_task = Task.objects.create(
            title='Overdue Task',
            project=self.project,
            status=Task.Status.IN_PROGRESS,
            due_date=today - timedelta(days=2),
            created_by=self.manager
        )
        self.assertTrue(overdue_task.is_overdue)

        # Task due yesterday but marked DONE -> NOT OVERDUE
        done_task = Task.objects.create(
            title='Done Task',
            project=self.project,
            status=Task.Status.DONE,
            due_date=today - timedelta(days=2),
            created_by=self.manager
        )
        self.assertFalse(done_task.is_overdue)

        # Task due tomorrow -> NOT OVERDUE
        future_task = Task.objects.create(
            title='Future Task',
            project=self.project,
            status=Task.Status.TODO,
            due_date=today + timedelta(days=2),
            created_by=self.manager
        )
        self.assertFalse(future_task.is_overdue)

    def test_project_membership_unique_constraint(self):
        """Verify that duplicate user assignments to the same project raise IntegrityError."""
        from django.db import IntegrityError
        with self.assertRaises(IntegrityError):
            ProjectMembership.objects.create(project=self.project, user=self.member)


class ViewTests(TestCase):
    """Unit tests for template views and role-based access control."""

    def setUp(self):
        self.client = Client()
        self.admin = User.objects.create_user(username='admin', password='password123', role=User.Role.ADMIN)
        self.manager = User.objects.create_user(username='manager', password='password123', role=User.Role.MANAGER)
        self.member = User.objects.create_user(username='member', password='password123', role=User.Role.MEMBER)
        self.outsider = User.objects.create_user(username='outsider', password='password123', role=User.Role.MEMBER)

        self.project = Project.objects.create(name='Alpha Project', created_by=self.manager)
        ProjectMembership.objects.create(project=self.project, user=self.manager)
        ProjectMembership.objects.create(project=self.project, user=self.member)

        self.task = Task.objects.create(
            title='Build Auth',
            project=self.project,
            status=Task.Status.IN_PROGRESS,
            priority=Task.Priority.HIGH,
            created_by=self.manager,
            assigned_to=self.member
        )

    def test_anonymous_redirect(self):
        """Anonymous access to dashboard should redirect to login."""
        response = self.client.get(reverse('tasks:dashboard'))
        self.assertEqual(response.status_code, 302)
        self.assertIn('/accounts/login/', response.get('Location'))

    def test_dashboard_authenticated(self):
        """Authenticated member can access dashboard with correct context."""
        self.client.login(username='member', password='password123')
        response = self.client.get(reverse('tasks:dashboard'))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Alpha Project')
        self.assertContains(response, 'Build Auth')

    def test_project_detail_access_control(self):
        """Members can view project detail; outsiders are denied."""
        # Member should succeed
        self.client.login(username='member', password='password123')
        res_member = self.client.get(reverse('tasks:project_detail', args=[self.project.pk]))
        self.assertEqual(res_member.status_code, 200)

        # Outsider should be redirected with error message
        self.client.login(username='outsider', password='password123')
        res_outsider = self.client.get(reverse('tasks:project_detail', args=[self.project.pk]))
        self.assertEqual(res_outsider.status_code, 302)

    def test_kanban_view(self):
        """Kanban board loads columns and tasks."""
        self.client.login(username='member', password='password123')
        response = self.client.get(reverse('tasks:project_kanban', args=[self.project.pk]))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Build Auth')
        self.assertContains(response, 'kanban.js')


class APITests(APITestCase):
    """Unit tests for DRF REST API endpoints, validation, and permissions."""

    def setUp(self):
        self.manager = User.objects.create_user(username='api_manager', password='password123', role=User.Role.MANAGER)
        self.member = User.objects.create_user(username='api_member', password='password123', role=User.Role.MEMBER)
        self.outsider = User.objects.create_user(username='api_outsider', password='password123', role=User.Role.MEMBER)

        self.token = Token.objects.create(user=self.member)
        self.client.credentials(HTTP_AUTHORIZATION=f'Token {self.token.key}')

        self.project = Project.objects.create(name='API Project', created_by=self.manager)
        ProjectMembership.objects.create(project=self.project, user=self.manager)
        ProjectMembership.objects.create(project=self.project, user=self.member)

        self.task = Task.objects.create(
            title='API Task',
            project=self.project,
            status=Task.Status.TODO,
            priority=Task.Priority.MEDIUM,
            created_by=self.manager,
            assigned_to=self.member
        )

    def test_obtain_auth_token(self):
        """POST credentials to /api/auth/token/ returns valid auth token."""
        self.client.credentials()  # Clear credentials
        response = self.client.post(reverse('api_token_auth'), {
            'username': 'api_member',
            'password': 'password123'
        })
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn('token', response.data)

    def test_list_tasks_query_filtering(self):
        """Tasks API supports ?status= filtering."""
        response = self.client.get(reverse('api-task-list'), {'status': 'todo'})
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data['results']), 1)
        self.assertEqual(response.data['results'][0]['title'], 'API Task')

        # Filter with non-matching status
        response_empty = self.client.get(reverse('api-task-list'), {'status': 'done'})
        self.assertEqual(response_empty.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response_empty.data['results']), 0)

    def test_due_date_validation_rejects_past_date(self):
        """Serializer must reject due_date set in the past."""
        past_date = (timezone.localdate() - timedelta(days=5)).isoformat()
        response = self.client.post(reverse('api-task-list'), {
            'title': 'Invalid Past Task',
            'project': self.project.id,
            'due_date': past_date,
            'status': 'todo',
            'priority': 'medium'
        })
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn('due_date', response.data)

    def test_kanban_update_status_endpoint(self):
        """PATCH /api/tasks/{id}/update-status/ updates status without full reload."""
        url = reverse('api-task-update-status', args=[self.task.id])
        response = self.client.patch(url, {'status': 'in_progress'}, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['status'], 'in_progress')

        # Check DB updated
        self.task.refresh_from_db()
        self.assertEqual(self.task.status, Task.Status.IN_PROGRESS)

    def test_outsider_cannot_access_project_tasks(self):
        """Users outside the project cannot view or modify its tasks."""
        outsider_token = Token.objects.create(user=self.outsider)
        self.client.credentials(HTTP_AUTHORIZATION=f'Token {outsider_token.key}')

        # Attempt to retrieve task details
        url = reverse('api-task-detail', args=[self.task.id])
        response = self.client.get(url)
        # Should be 404 (hidden) or 403
        self.assertIn(response.status_code, [status.HTTP_404_NOT_FOUND, status.HTTP_403_FORBIDDEN])
