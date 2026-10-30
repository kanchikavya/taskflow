"""
Authentication API Views for React Frontend integration.
Provides token login, registration, and user profile retrieval.
"""

from django.contrib.auth import authenticate, get_user_model
from rest_framework import status, permissions
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.authtoken.models import Token

from tasks.models import Project, ProjectMembership
from tasks.serializers import UserSummarySerializer

User = get_user_model()


class APILoginView(APIView):
    """
    POST /api/auth/login/
    Authenticates user credentials and returns an Auth Token along with user info.
    """
    permission_classes = [permissions.AllowAny]

    def post(self, request):
        username = request.data.get('username', '').strip()
        password = request.data.get('password', '').strip()

        if not username or not password:
            return Response(
                {'error': 'Both username and password are required.'},
                status=status.HTTP_400_BAD_REQUEST
            )

        user = authenticate(request, username=username, password=password)
        if not user:
            return Response(
                {'error': 'Invalid credentials. Please check your username and password.'},
                status=status.HTTP_401_UNAUTHORIZED
            )

        token, _ = Token.objects.get_or_create(user=user)
        user_data = UserSummarySerializer(user).data

        return Response({
            'token': token.key,
            'user': user_data
        }, status=status.HTTP_200_OK)


class APIRegisterView(APIView):
    """
    POST /api/auth/register/
    Registers a new user, enrolls them in the default project, and returns an Auth Token.
    """
    permission_classes = [permissions.AllowAny]

    def post(self, request):
        username = request.data.get('username', '').strip()
        email = request.data.get('email', '').strip()
        password = request.data.get('password', '').strip()
        first_name = request.data.get('first_name', '').strip()
        last_name = request.data.get('last_name', '').strip()
        role = request.data.get('role', User.Role.MEMBER).strip().lower()

        if not username or not password:
            return Response(
                {'error': 'Username and password are required.'},
                status=status.HTTP_400_BAD_REQUEST
            )

        if User.objects.filter(username=username).exists():
            return Response(
                {'error': f"Username '{username}' is already taken."},
                status=status.HTTP_400_BAD_REQUEST
            )

        if role not in [r[0] for r in User.Role.choices]:
            role = User.Role.MEMBER

        user = User.objects.create_user(
            username=username,
            email=email,
            password=password,
            first_name=first_name,
            last_name=last_name,
            role=role
        )

        # Automatically enroll newly registered user in default project
        default_project = Project.objects.order_by('created_at').first()
        if default_project:
            ProjectMembership.objects.get_or_create(project=default_project, user=user)

        token = Token.objects.create(user=user)
        user_data = UserSummarySerializer(user).data

        return Response({
            'token': token.key,
            'user': user_data
        }, status=status.HTTP_201_CREATED)


class APICurrentUserView(APIView):
    """
    GET /api/auth/me/
    Returns the authenticated user's profile and role.
    """
    permission_classes = [permissions.IsAuthenticated]

    def get(self, request):
        serializer = UserSummarySerializer(request.user)
        return Response(serializer.data, status=status.HTTP_200_OK)
