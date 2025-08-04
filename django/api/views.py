"""Views for the API application."""

import logging
from typing import Any, Dict

from django.conf import settings
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework.pagination import PageNumberPagination

from api import serializers, models
from api.utils import model_utils

logger = logging.getLogger(__name__)


class CustomPagination(PageNumberPagination):
    """Custom pagination class for API responses."""
    
    page_size = 20
    page_size_query_param = 'page_size'
    max_page_size = 100


class JiraAgentApiView(APIView):
    """
    API view for interacting with the Jira agent.
    
    This view handles requests to the Jira agent, processes them,
    stores the interaction, and returns the agent's response.
    """
    
    def post(self, request) -> Response:
        """
        Process a request to the Jira agent.
        
        Args:
            request: The HTTP request object
            
        Returns:
            Response: JSON response containing the agent's output or error details
        """
        # Validate incoming request data
        request_serializer = serializers.ModelRequestSerializer(data=request.data)
        if not request_serializer.is_valid():
            logger.warning(f"Invalid request data: {request_serializer.errors}")
            return Response(
                {
                    'error': 'Invalid request data',
                    'details': request_serializer.errors
                },
                status=status.HTTP_400_BAD_REQUEST
            )
        
        user_request = request_serializer.validated_data.get('request')
        logger.info(f"Processing Jira agent request: {user_request[:100]}...")
        
        try:
            # Invoke the Jira agent
            agent_response = model_utils.agent.invoke({"input": user_request})
            
            if not agent_response or 'output' not in agent_response:
                logger.error("Agent returned empty or invalid response")
                return Response(
                    {'error': 'Agent returned empty response'},
                    status=status.HTTP_500_INTERNAL_SERVER_ERROR
                )
            
            output = agent_response.get('output')
            
            # Validate and save the response
            response_serializer = serializers.ModelResponseSerializer(
                data={"response": output}
            )
            if not response_serializer.is_valid():
                logger.error(f"Invalid response data: {response_serializer.errors}")
                return Response(
                    {'error': 'Invalid response data'},
                    status=status.HTTP_500_INTERNAL_SERVER_ERROR
                )
            
            # Create and save the model request
            model_request = models.ModelRequest(
                request=user_request,
                response=output
            )
            model_request.save()
            
            logger.info(f"Successfully processed request {model_request.id}")
            
            return Response({
                'output': output,
                'request_id': model_request.id,
                'status': 'success'
            })
            
        except Exception as e:
            logger.error(f"Error processing Jira agent request: {str(e)}", exc_info=True)
            return Response(
                {
                    'error': 'Internal server error',
                    'message': 'An error occurred while processing your request'
                },
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )


class HealthCheck(APIView):
    """
    Health check endpoint for monitoring and load balancers.
    
    This endpoint provides basic health status information
    about the application and its dependencies.
    """
    
    def get(self, request) -> Response:
        """
        Return health status information.
        
        Args:
            request: The HTTP request object
            
        Returns:
            Response: JSON response with health status
        """
        try:
            # Basic health checks
            health_status = {
                'status': 'healthy',
                'service': 'django-api',
                'version': '1.0.0',
                'timestamp': models.timezone.now().isoformat(),
            }
            
            # Check database connectivity
            try:
                models.ModelRequest.objects.count()
                health_status['database'] = 'connected'
            except Exception as e:
                logger.error(f"Database health check failed: {str(e)}")
                health_status['database'] = 'disconnected'
                health_status['status'] = 'unhealthy'
            
            # Check agent availability
            try:
                # Simple test to ensure agent is available
                if hasattr(model_utils, 'agent') and model_utils.agent:
                    health_status['agent'] = 'available'
                else:
                    health_status['agent'] = 'unavailable'
                    health_status['status'] = 'unhealthy'
            except Exception as e:
                logger.error(f"Agent health check failed: {str(e)}")
                health_status['agent'] = 'unavailable'
                health_status['status'] = 'unhealthy'
            
            status_code = (
                status.HTTP_200_OK 
                if health_status['status'] == 'healthy' 
                else status.HTTP_503_SERVICE_UNAVAILABLE
            )
            
            return Response(health_status, status=status_code)
            
        except Exception as e:
            logger.error(f"Health check failed: {str(e)}", exc_info=True)
            return Response(
                {
                    'status': 'error',
                    'error': 'Health check failed',
                    'message': str(e)
                },
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )


class GetRecords(APIView):
    """
    API view for retrieving model request records.
    
    This view provides paginated access to stored request/response
    records for auditing and debugging purposes.
    """
    
    pagination_class = CustomPagination
    
    def get(self, request) -> Response:
        """
        Retrieve paginated model request records.
        
        Args:
            request: The HTTP request object
            
        Returns:
            Response: Paginated JSON response with request records
        """
        try:
            # Get queryset with ordering
            queryset = models.ModelRequest.objects.all()
            
            # Apply pagination
            paginator = self.pagination_class()
            page = paginator.paginate_queryset(queryset, request)
            
            if page is not None:
                # Serialize the page
                serializer = serializers.ModelRequestSummarySerializer(page, many=True)
                return paginator.get_paginated_response(serializer.data)
            
            # Fallback for non-paginated response
            serializer = serializers.ModelRequestSummarySerializer(queryset, many=True)
            return Response({
                'count': queryset.count(),
                'results': serializer.data
            })
            
        except Exception as e:
            logger.error(f"Error retrieving records: {str(e)}", exc_info=True)
            return Response(
                {
                    'error': 'Failed to retrieve records',
                    'message': str(e)
                },
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )


class GetRecordDetail(APIView):
    """
    API view for retrieving detailed information about a specific record.
    
    This view provides complete information about a single
    request/response record including full text and metadata.
    """
    
    def get(self, request, record_id: int) -> Response:
        """
        Retrieve detailed information about a specific record.
        
        Args:
            request: The HTTP request object
            record_id: The ID of the record to retrieve
            
        Returns:
            Response: JSON response with detailed record information
        """
        try:
            record = models.ModelRequest.objects.get(id=record_id)
            serializer = serializers.ModelRequestDetailSerializer(record)
            return Response(serializer.data)
            
        except models.ModelRequest.DoesNotExist:
            logger.warning(f"Record {record_id} not found")
            return Response(
                {'error': 'Record not found'},
                status=status.HTTP_404_NOT_FOUND
            )
        except Exception as e:
            logger.error(f"Error retrieving record {record_id}: {str(e)}", exc_info=True)
            return Response(
                {
                    'error': 'Failed to retrieve record',
                    'message': str(e)
                },
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )