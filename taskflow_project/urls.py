"""
URL configuration for TaskFlow project.
"""

from django.contrib import admin
from django.urls import path, include

urlpatterns = [
    path('admin/', admin.site.urls),
    path('accounts/', include('accounts.urls')),
    path('api/', include('tasks.api_urls')),
    path('', include('tasks.urls')),
]

# Custom HTTP Error Handlers
handler404 = 'tasks.views.custom_404_view'
handler403 = 'tasks.views.custom_403_view'
handler500 = 'tasks.views.custom_500_view'
