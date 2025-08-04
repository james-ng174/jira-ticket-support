"""Admin interface for the API application."""

from django.contrib import admin
from django.utils.html import format_html
from django.utils.safestring import mark_safe
from api import models


@admin.register(models.ModelRequest)
class ModelRequestAdmin(admin.ModelAdmin):
    """
    Admin interface for ModelRequest model.
    
    Provides comprehensive management interface for viewing and managing
    Jira agent request/response records.
    """
    
    list_display = [
        'id', 
        'request_preview', 
        'response_preview', 
        'created_at', 
        'updated_at',
        'request_length',
        'response_length'
    ]
    
    list_filter = [
        'created_at',
        'updated_at',
    ]
    
    search_fields = [
        'request',
        'response',
    ]
    
    readonly_fields = [
        'id',
        'created_at',
        'updated_at',
        'request_length',
        'response_length',
        'request_display',
        'response_display',
    ]
    
    fieldsets = (
        ('Basic Information', {
            'fields': ('id', 'created_at', 'updated_at')
        }),
        ('Request Data', {
            'fields': ('request', 'request_display', 'request_length'),
            'classes': ('collapse',)
        }),
        ('Response Data', {
            'fields': ('response', 'response_display', 'response_length'),
            'classes': ('collapse',)
        }),
    )
    
    ordering = ['-created_at']
    
    list_per_page = 25
    
    def request_preview(self, obj: models.ModelRequest) -> str:
        """Display a preview of the request text."""
        preview = obj.request[:50] + "..." if len(obj.request) > 50 else obj.request
        return format_html('<span title="{}">{}</span>', obj.request, preview)
    request_preview.short_description = 'Request Preview'
    
    def response_preview(self, obj: models.ModelRequest) -> str:
        """Display a preview of the response text."""
        preview = obj.response[:50] + "..." if len(obj.response) > 50 else obj.response
        return format_html('<span title="{}">{}</span>', obj.response, preview)
    response_preview.short_description = 'Response Preview'
    
    def request_length(self, obj: models.ModelRequest) -> int:
        """Display the length of the request text."""
        return len(obj.request)
    request_length.short_description = 'Request Length'
    
    def response_length(self, obj: models.ModelRequest) -> int:
        """Display the length of the response text."""
        return len(obj.response)
    response_length.short_description = 'Response Length'
    
    def request_display(self, obj: models.ModelRequest) -> str:
        """Display the full request text with proper formatting."""
        return format_html('<pre style="max-height: 300px; overflow-y: auto;">{}</pre>', obj.request)
    request_display.short_description = 'Full Request'
    
    def response_display(self, obj: models.ModelRequest) -> str:
        """Display the full response text with proper formatting."""
        return format_html('<pre style="max-height: 300px; overflow-y: auto;">{}</pre>', obj.response)
    response_display.short_description = 'Full Response'
    
    def has_add_permission(self, request) -> bool:
        """Disable adding new records through admin interface."""
        return False
    
    def has_change_permission(self, request, obj=None) -> bool:
        """Disable editing records through admin interface."""
        return False
    
    def has_delete_permission(self, request, obj=None) -> bool:
        """Allow deletion of records."""
        return True
    
    class Media:
        """Custom CSS for better admin display."""
        css = {
            'all': ('admin/css/model_request.css',)
        }
