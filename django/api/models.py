"""Models for the API application."""

from django.db import models
from django.utils import timezone


class ModelRequest(models.Model):
    """
    Model to store Jira agent requests and responses.
    
    This model tracks all interactions with the Jira agent for auditing
    and debugging purposes.
    """
    
    request = models.TextField(
        help_text="The user's request to the Jira agent"
    )
    response = models.TextField(
        help_text="The agent's response to the request"
    )
    created_at = models.DateTimeField(
        default=timezone.now,
        help_text="Timestamp when the request was created"
    )
    updated_at = models.DateTimeField(
        auto_now=True,
        help_text="Timestamp when the record was last updated"
    )
    
    class Meta:
        """Meta options for ModelRequest."""
        db_table = 'api_model_request'
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['created_at']),
            models.Index(fields=['request']),
        ]
        verbose_name = 'Model Request'
        verbose_name_plural = 'Model Requests'
    
    def __str__(self) -> str:
        """Return string representation of the model."""
        return f"Request {self.id}: {self.request[:50]}..."
    
    def get_summary(self) -> dict:
        """
        Get a summary of the request and response.
        
        Returns:
            dict: Summary containing request length, response length, and timestamps
        """
        return {
            'id': self.id,
            'request_length': len(self.request),
            'response_length': len(self.response),
            'created_at': self.created_at,
            'updated_at': self.updated_at,
        }
    