"""URL configuration for the API application."""

from django.urls import path, include
from rest_framework.routers import DefaultRouter
from api import views

router = DefaultRouter()

urlpatterns = [
    # Health check endpoint
    path('health-check/', views.HealthCheck.as_view(), name='health-check'),
    
    # Record management endpoints
    path('records/', views.GetRecords.as_view(), name='get-records'),
    path('records/<int:record_id>/', views.GetRecordDetail.as_view(), name='get-record-detail'),
    
    # Jira agent endpoint
    path('jira-agent/', views.JiraAgentApiView.as_view(), name='jira-agent'),
    
    # Include router URLs
    path('', include(router.urls))
]