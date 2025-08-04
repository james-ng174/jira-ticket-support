"""
API utilities for communicating with the Django backend.

This module handles all HTTP communication with the Django API,
including request/response handling, error management, and retry logic.
"""

import logging
import time
from typing import Dict, Optional, Any

import requests
from requests.exceptions import RequestException, Timeout

from .config import get_config

logger = logging.getLogger(__name__)


class APIError(Exception):
    """Custom exception for API-related errors."""
    pass


class APIClient:
    """
    HTTP client for communicating with the Django API.
    
    This class provides a robust interface for making API calls
    with proper error handling, timeout management, and retry logic.
    """
    
    def __init__(self, timeout: int = 30, max_retries: int = 3):
        """
        Initialize the API client.
        
        Args:
            timeout: Request timeout in seconds
            max_retries: Maximum number of retry attempts
        """
        self.timeout = timeout
        self.max_retries = max_retries
        self.config = get_config()
        self.session = requests.Session()
        
        # Set default headers
        self.session.headers.update({
            'Content-Type': 'application/json',
            'Accept': 'application/json',
        })
    
    def _make_request(
        self, 
        method: str, 
        endpoint: str, 
        data: Optional[Dict[str, Any]] = None,
        **kwargs
    ) -> requests.Response:
        """
        Make an HTTP request with retry logic.
        
        Args:
            method: HTTP method (GET, POST, etc.)
            endpoint: API endpoint path
            data: Request data
            **kwargs: Additional request parameters
            
        Returns:
            requests.Response: The API response
            
        Raises:
            APIError: If the request fails after all retries
        """
        url = self.config.get_django_api_url(endpoint)
        
        for attempt in range(self.max_retries):
            try:
                logger.debug(f"Making {method} request to {url} (attempt {attempt + 1})")
                
                response = self.session.request(
                    method=method,
                    url=url,
                    json=data,
                    timeout=self.timeout,
                    **kwargs
                )
                
                response.raise_for_status()
                return response
                
            except Timeout:
                logger.warning(f"Request timeout on attempt {attempt + 1}")
                if attempt == self.max_retries - 1:
                    raise APIError("Request timed out after all retry attempts")
                    
            except RequestException as e:
                logger.error(f"Request failed on attempt {attempt + 1}: {str(e)}")
                if attempt == self.max_retries - 1:
                    raise APIError(f"Request failed after all retry attempts: {str(e)}")
                
                # Wait before retry (exponential backoff)
                time.sleep(2 ** attempt)
    
    def call_jira_agent(self, request: str) -> Optional[str]:
        """
        Call the Jira agent API endpoint.
        
        Args:
            request: The user's request to the Jira agent
            
        Returns:
            Optional[str]: Formatted response or None if failed
        """
        try:
            if not request or not request.strip():
                logger.warning("Empty request provided to Jira agent")
                return None
            
            data = {"request": request.strip()}
            response = self._make_request("POST", "jira-agent/", data=data)
            
            if response.status_code == 200:
                response_data = response.json()
                output = response_data.get("output")
                
                if output:
                    formatted_response = self._format_response(request, output)
                    logger.info(f"Successfully processed Jira agent request")
                    return formatted_response
                else:
                    logger.warning("Jira agent returned empty output")
                    return None
            else:
                logger.error(f"Jira agent API returned status {response.status_code}")
                return None
                
        except APIError as e:
            logger.error(f"API error calling Jira agent: {str(e)}")
            return None
        except Exception as e:
            logger.error(f"Unexpected error calling Jira agent: {str(e)}")
            return None
    
    def check_health(self) -> Dict[str, Any]:
        """
        Check the health of the Django API.
        
        Returns:
            Dict[str, Any]: Health status information
        """
        try:
            response = self._make_request("GET", "health-check/")
            
            if response.status_code == 200:
                health_data = response.json()
                logger.info("Django API health check successful")
                return health_data
            else:
                logger.error(f"Health check failed with status {response.status_code}")
                return {"status": "unhealthy", "error": f"HTTP {response.status_code}"}
                
        except Exception as e:
            logger.error(f"Health check failed: {str(e)}")
            return {"status": "error", "error": str(e)}
    
    def get_records(self, page: int = 1, page_size: int = 20) -> Optional[Dict[str, Any]]:
        """
        Get paginated records from the Django API.
        
        Args:
            page: Page number (1-based)
            page_size: Number of records per page
            
        Returns:
            Optional[Dict[str, Any]]: Records data or None if failed
        """
        try:
            params = {"page": page, "page_size": page_size}
            response = self._make_request("GET", "records/", params=params)
            
            if response.status_code == 200:
                records_data = response.json()
                logger.info(f"Successfully retrieved records (page {page})")
                return records_data
            else:
                logger.error(f"Failed to get records: HTTP {response.status_code}")
                return None
                
        except Exception as e:
            logger.error(f"Error getting records: {str(e)}")
            return None
    
    def _format_response(self, request: str, output: str) -> str:
        """
        Format the API response for display.
        
        Args:
            request: The original request
            output: The agent's output
            
        Returns:
            str: Formatted response string
        """
        return f"Request: {request}<br>Output: {output}<br><br>"


# Global API client instance
_api_client: Optional[APIClient] = None


def get_api_client() -> APIClient:
    """
    Get the global API client instance.
    
    Returns:
        APIClient: The API client instance
    """
    global _api_client
    if _api_client is None:
        _api_client = APIClient()
    return _api_client


def call_jira_agent(request: str) -> Optional[str]:
    """
    Call the Jira agent API (backward compatibility function).
    
    Args:
        request: The user's request to the Jira agent
        
    Returns:
        Optional[str]: Formatted response or None if failed
    """
    client = get_api_client()
    return client.call_jira_agent(request)


def check_api_health() -> Dict[str, Any]:
    """
    Check the health of the Django API (backward compatibility function).
    
    Returns:
        Dict[str, Any]: Health status information
    """
    client = get_api_client()
    return client.check_health()
