"""
REST API URL routing for TaskFlow using DRF's DefaultRouter.
"""

from django.urls import path, include
from rest_framework.routers import DefaultRouter
from rest_framework.authtoken.views import obtain_auth_token

from .api_views import ProjectViewSet, TaskViewSet, TaskCommentViewSet
from accounts.api_views import APILoginView, APIRegisterView, APICurrentUserView

router = DefaultRouter()
router.register(r'projects', ProjectViewSet, basename='api-project')
router.register(r'tasks', TaskViewSet, basename='api-task')
router.register(r'comments', TaskCommentViewSet, basename='api-comment')

urlpatterns = [
    # Token Authentication endpoints
    path('auth/token/', obtain_auth_token, name='api_token_auth'),
    path('auth/login/', APILoginView.as_view(), name='api_login'),
    path('auth/register/', APIRegisterView.as_view(), name='api_register'),
    path('auth/me/', APICurrentUserView.as_view(), name='api_current_user'),

    # ViewSet CRUD endpoints
    path('', include(router.urls)),
]
