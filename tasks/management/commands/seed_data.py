"""
Custom Django management command to seed initial users, projects, and tasks for testing.

Usage:
    python manage.py seed_data
"""

from datetime import timedelta
from django.core.management.base import BaseCommand
from django.contrib.auth import get_user_model
from django.utils import timezone
from tasks.models import Project, ProjectMembership, Task, TaskComment

User = get_user_model()


class Command(BaseCommand):
    help = 'Seeds sample users with roles (Admin, Manager, Member), projects, and tasks.'

    def handle(self, *args, **options):
        self.stdout.write(self.style.NOTICE('Seeding TaskFlow initial data...'))

        # 1. Create or update sample users
        admin_user, _ = User.objects.get_or_create(
            username='admin',
            defaults={
                'email': 'admin@taskflow.dev',
                'first_name': 'Aarav',
                'last_name': 'Admin',
                'role': User.Role.ADMIN,
                'is_staff': True,
                'is_superuser': True,
            }
        )
        admin_user.set_password('admin123')
        admin_user.role = User.Role.ADMIN
        admin_user.is_staff = True
        admin_user.is_superuser = True
        admin_user.save()

        manager_user, _ = User.objects.get_or_create(
            username='manager1',
            defaults={
                'email': 'manager1@taskflow.dev',
                'first_name': 'Meera',
                'last_name': 'Manager',
                'role': User.Role.MANAGER,
                'is_staff': True,
            }
        )
        manager_user.set_password('manager123')
        manager_user.role = User.Role.MANAGER
        manager_user.is_staff = True
        manager_user.save()

        member_user, _ = User.objects.get_or_create(
            username='member1',
            defaults={
                'email': 'member1@taskflow.dev',
                'first_name': 'Rohan',
                'last_name': 'Member',
                'role': User.Role.MEMBER,
            }
        )
        member_user.set_password('member123')
        member_user.role = User.Role.MEMBER
        member_user.save()

        self.stdout.write(self.style.SUCCESS('Users created: admin, manager1, member1'))

        # 2. Create sample project
        project, _ = Project.objects.get_or_create(
            name='TaskFlow Core Engine',
            defaults={
                'description': 'Main backend services, authentication, and REST API development.',
                'created_by': admin_user,
            }
        )

        # 3. Add members through ProjectMembership
        ProjectMembership.objects.get_or_create(project=project, user=admin_user)
        ProjectMembership.objects.get_or_create(project=project, user=manager_user)
        ProjectMembership.objects.get_or_create(project=project, user=member_user)

        self.stdout.write(self.style.SUCCESS(f'Project "{project.name}" seeded with 3 members.'))

        # 4. Create sample tasks
        today = timezone.localdate()

        task1, _ = Task.objects.get_or_create(
            title='Configure Custom User Model and Migrations',
            project=project,
            defaults={
                'description': 'Define User extending AbstractUser with roles and setup indexes.',
                'status': Task.Status.DONE,
                'priority': Task.Priority.HIGH,
                'due_date': today - timedelta(days=1),
                'assigned_to': manager_user,
                'created_by': admin_user,
            }
        )

        task2, _ = Task.objects.get_or_create(
            title='Build Authentication and Project CRUD Views',
            project=project,
            defaults={
                'description': 'Create login/logout templates and project management views with Bootstrap 5.',
                'status': Task.Status.IN_PROGRESS,
                'priority': Task.Priority.HIGH,
                'due_date': today + timedelta(days=2),
                'assigned_to': member_user,
                'created_by': manager_user,
            }
        )

        task3, _ = Task.objects.get_or_create(
            title='Implement DRF Serializers and ViewSets',
            project=project,
            defaults={
                'description': 'Expose CRUD endpoints for tasks and comments with TokenAuthentication.',
                'status': Task.Status.TODO,
                'priority': Task.Priority.URGENT,
                'due_date': today + timedelta(days=5),
                'assigned_to': member_user,
                'created_by': manager_user,
            }
        )

        self.stdout.write(self.style.SUCCESS('3 Sample tasks created across statuses.'))

        # 5. Add sample comment
        TaskComment.objects.get_or_create(
            task=task2,
            author=manager_user,
            defaults={'content': 'Started working on registration and login template styling.'}
        )

        self.stdout.write(self.style.SUCCESS('Initial database seeding completed successfully!'))
