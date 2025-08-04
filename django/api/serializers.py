"""Serializers for the API application."""

from rest_framework import serializers
from api import models


class ModelRequestSerializer(serializers.ModelSerializer):
    """
    Serializer for creating model requests.
    
    This serializer handles the validation and serialization of incoming
    requests to the Jira agent.
    """
    
    class Meta:
        """Meta configuration for ModelRequestSerializer."""
        model = models.ModelRequest
        fields = ['request']
    
    def validate_request(self, value: str) -> str:
        """
        Validate the request field.
        
        Args:
            value: The request text to validate
            
        Returns:
            str: The validated request text
            
        Raises:
            serializers.ValidationError: If the request is empty or too long
        """
        if not value or not value.strip():
            raise serializers.ValidationError("Request cannot be empty")
        
        if len(value) > 10000:  # 10KB limit
            raise serializers.ValidationError("Request is too long (max 10KB)")
        
        return value.strip()


class ModelResponseSerializer(serializers.ModelSerializer):
    """
    Serializer for model responses.
    
    This serializer handles the serialization of agent responses
    for storage and retrieval.
    """
    
    class Meta:
        """Meta configuration for ModelResponseSerializer."""
        model = models.ModelRequest
        fields = ['response']


class ModelRequestDetailSerializer(serializers.ModelSerializer):
    """
    Detailed serializer for model requests including all fields.
    
    This serializer is used for retrieving complete request/response data
    including timestamps and metadata.
    """
    
    class Meta:
        """Meta configuration for ModelRequestDetailSerializer."""
        model = models.ModelRequest
        fields = ['id', 'request', 'response', 'created_at', 'updated_at']
        read_only_fields = ['id', 'created_at', 'updated_at']


class ModelRequestSummarySerializer(serializers.ModelSerializer):
    """
    Summary serializer for model requests.
    
    This serializer provides a lightweight view of request data
    for listing and overview purposes.
    """
    
    request_preview = serializers.SerializerMethodField()
    response_preview = serializers.SerializerMethodField()
    
    class Meta:
        """Meta configuration for ModelRequestSummarySerializer."""
        model = models.ModelRequest
        fields = ['id', 'request_preview', 'response_preview', 'created_at']
        read_only_fields = ['id', 'created_at']
    
    def get_request_preview(self, obj: models.ModelRequest) -> str:
        """Get a preview of the request text."""
        return obj.request[:100] + "..." if len(obj.request) > 100 else obj.request
    
    def get_response_preview(self, obj: models.ModelRequest) -> str:
        """Get a preview of the response text."""
        return obj.response[:100] + "..." if len(obj.response) > 100 else obj.response