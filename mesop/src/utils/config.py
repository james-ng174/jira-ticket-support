"""
Configuration management for the Mesop application.

This module handles all configuration settings, environment variables,
and application state management for the AI Jira Assistant.
"""

import logging
import os
from typing import List, Optional

import mesop as me

logger = logging.getLogger(__name__)


class ConfigurationError(Exception):
    """Custom exception for configuration errors."""
    pass


class AppConfig:
    """
    Application configuration manager.
    
    This class manages all configuration settings including environment
    variables, application state, and dynamic configuration.
    """
    
    def __init__(self):
        """Initialize the configuration manager."""
        self._load_environment_variables()
        self._validate_configuration()
        self._setup_example_prompts()
    
    def _load_environment_variables(self) -> None:
        """Load and validate environment variables."""
        try:
            self.project_key = os.environ.get("PROJECT_KEY")
            self.docker_running = os.environ.get("DOCKER_RUNNING", "false").lower() == "true"
            self.environment = os.environ.get("ENVIRONMENT", "development")
            
            # Django URL configuration
            if self.docker_running:
                self.django_url = "http://django:8000/"
            else:
                self.django_url = "http://localhost:8000/"
            
            logger.info(f"Configuration loaded - Project: {self.project_key}, Docker: {self.docker_running}")
            
        except Exception as e:
            logger.error(f"Error loading environment variables: {str(e)}")
            raise ConfigurationError(f"Failed to load configuration: {str(e)}")
    
    def _validate_configuration(self) -> None:
        """Validate the configuration settings."""
        if not self.project_key:
            logger.warning("PROJECT_KEY environment variable is not set")
        
        if not self.django_url:
            raise ConfigurationError("Django URL is not properly configured")
    
    def _setup_example_prompts(self) -> None:
        """Setup example prompts for the user interface."""
        if not self.project_key:
            self.example_prompts = [
                "How many tasks are in status 'DONE'?",
                "Create a new task with description 'This is a test'.",
                "What are the tasks that are in status 'IN PROGRESS'?",
                "Triage the issue PROJECT-19",
                "Transition the tasks that are in status 'IN PROGRESS' to 'DONE'"
            ]
        else:
            self.example_prompts = [
                f"How many tasks are in status 'DONE' in project {self.project_key}?",
                f"Create a new task in project {self.project_key} with description 'This is a test'.",
                f"What are the tasks that are in status 'IN PROGRESS' in project {self.project_key}?",
                f"Triage the issue {self.project_key}-19",
                f"Transition the tasks that are in status 'IN PROGRESS' in project {self.project_key} to 'DONE'"
            ]
    
    def get_django_api_url(self, endpoint: str) -> str:
        """
        Get the full Django API URL for a given endpoint.
        
        Args:
            endpoint: The API endpoint path
            
        Returns:
            str: The complete API URL
        """
        return f"{self.django_url}api/{endpoint.lstrip('/')}"
    
    def is_production(self) -> bool:
        """
        Check if the application is running in production mode.
        
        Returns:
            bool: True if in production, False otherwise
        """
        return self.environment.lower() == "production"
    
    def get_health_status(self) -> dict:
        """
        Get the current health status of the configuration.
        
        Returns:
            dict: Health status information
        """
        return {
            "project_key": self.project_key,
            "docker_running": self.docker_running,
            "environment": self.environment,
            "django_url": self.django_url,
            "example_prompts_count": len(self.example_prompts),
        }


@me.stateclass
class AppState:
    """
    Application state management.
    
    This class manages the application's reactive state including
    user input, output, and processing status.
    """
    
    def __init__(self):
        """Initialize the application state."""
        self.input: str = ""
        self.output: str = ""
        self.in_progress: bool = False
        self.error_message: str = ""
        self.last_request_time: Optional[str] = None
    
    def clear_output(self) -> None:
        """Clear the output content."""
        self.output = ""
        self.error_message = ""
    
    def set_input(self, value: str) -> None:
        """
        Set the input value.
        
        Args:
            value: The input text
        """
        self.input = value
    
    def append_output(self, content: str) -> None:
        """
        Append content to the output.
        
        Args:
            content: The content to append
        """
        self.output += content
    
    def set_error(self, message: str) -> None:
        """
        Set an error message.
        
        Args:
            message: The error message
        """
        self.error_message = message
    
    def start_processing(self) -> None:
        """Mark the application as processing."""
        self.in_progress = True
        self.error_message = ""
    
    def stop_processing(self) -> None:
        """Mark the application as not processing."""
        self.in_progress = False
    
    def get_state_summary(self) -> dict:
        """
        Get a summary of the current state.
        
        Returns:
            dict: State summary information
        """
        return {
            "input_length": len(self.input),
            "output_length": len(self.output),
            "in_progress": self.in_progress,
            "has_error": bool(self.error_message),
            "error_message": self.error_message,
        }


# Global configuration and state instances
_config_instance: Optional[AppConfig] = None
_state_instance: Optional[AppState] = None


def get_config() -> AppConfig:
    """
    Get the global configuration instance.
    
    Returns:
        AppConfig: The configuration instance
    """
    global _config_instance
    if _config_instance is None:
        _config_instance = AppConfig()
    return _config_instance


def get_state() -> AppState:
    """
    Get the global application state instance.
    
    Returns:
        AppState: The state instance
    """
    global _state_instance
    if _state_instance is None:
        _state_instance = AppState()
    return _state_instance


# For backward compatibility
State = get_state()
