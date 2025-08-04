"""Jira API utilities for interacting with Jira instance."""

import logging
import os
import re
import json
from typing import Union, Optional, Dict, Tuple
from urllib.parse import urljoin

import requests
from requests.auth import HTTPBasicAuth

logger = logging.getLogger(__name__)

# Jira configuration
JIRA_INSTANCE_URL = os.environ.get("JIRA_INSTANCE_URL")
PROJECT_KEY = os.environ.get("PROJECT_KEY")
JIRA_USERNAME = os.environ.get("JIRA_USERNAME")
JIRA_API_TOKEN = os.environ.get("JIRA_API_TOKEN")

# Validate required environment variables
if not all([JIRA_INSTANCE_URL, PROJECT_KEY, JIRA_USERNAME, JIRA_API_TOKEN]):
    logger.error("Missing required Jira environment variables")


class JiraAPIError(Exception):
    """Custom exception for Jira API errors."""
    pass


class JiraConfigError(Exception):
    """Custom exception for Jira configuration errors."""
    pass


def _get_auth() -> HTTPBasicAuth:
    """
    Get HTTP Basic Auth for Jira API.
    
    Returns:
        HTTPBasicAuth: Authentication object for Jira API
        
    Raises:
        JiraConfigError: If required credentials are missing
    """
    if not JIRA_USERNAME or not JIRA_API_TOKEN:
        raise JiraConfigError("Jira username or API token not configured")
    
    return HTTPBasicAuth(JIRA_USERNAME, JIRA_API_TOKEN)


def _make_request(
    method: str, 
    endpoint: str, 
    data: Optional[Dict] = None,
    timeout: int = 30
) -> requests.Response:
    """
    Make a request to the Jira API.
    
    Args:
        method: HTTP method (GET, POST, etc.)
        endpoint: API endpoint path
        data: Request data for POST requests
        timeout: Request timeout in seconds
        
    Returns:
        requests.Response: The API response
        
    Raises:
        JiraAPIError: If the request fails
    """
    if not JIRA_INSTANCE_URL:
        raise JiraConfigError("Jira instance URL not configured")
    
    url = urljoin(JIRA_INSTANCE_URL, endpoint)
    auth = _get_auth()
    
    headers = {
        "Accept": "application/json",
        "Content-Type": "application/json"
    }
    
    try:
        response = requests.request(
            method=method,
            url=url,
            auth=auth,
            headers=headers,
            json=data,
            timeout=timeout
        )
        response.raise_for_status()
        return response
        
    except requests.exceptions.RequestException as e:
        logger.error(f"Jira API request failed: {str(e)}")
        raise JiraAPIError(f"Jira API request failed: {str(e)}")


def link_jira_issue(
    inward_issue_key: str, 
    outward_issue_key: str, 
    link_type: str = 'Relates'
) -> bool:
    """
    Link two Jira tickets.
    
    Args:
        inward_issue_key: Jira key of the inward issue
        outward_issue_key: Jira key of the outward issue
        link_type: Jira link type (default: 'Relates')
        
    Returns:
        bool: True if linking was successful
        
    Raises:
        JiraAPIError: If the linking operation fails
    """
    try:
        data = {
            "inwardIssue": {"key": inward_issue_key},
            "outwardIssue": {"key": outward_issue_key},
            "type": {"name": link_type}
        }
        
        response = _make_request("POST", "/rest/api/2/issueLink", data=data)
        
        if response.status_code == 201:
            logger.info(f"Successfully linked {inward_issue_key} -> {outward_issue_key}")
            return True
        else:
            logger.error(f"Failed to link issues: {response.status_code}")
            return False
            
    except Exception as e:
        logger.error(f"Error linking Jira issues: {str(e)}")
        raise JiraAPIError(f"Failed to link issues: {str(e)}")


def extract_tag_helper(text: str, tag: str = 'related') -> Optional[str]:
    """
    Extract text between XML-like tags.
    
    Args:
        text: Text to search in
        tag: Tag name to extract
        
    Returns:
        Optional[str]: Extracted text or None if not found
    """
    try:
        pattern = f'<{tag}>(.*?)<{tag}>'
        match = re.search(pattern, text, flags=re.DOTALL)
        return match.group(1) if match else None
        
    except Exception as e:
        logger.error(f"Error extracting tag '{tag}': {str(e)}")
        return None


def parse_jira_issue_fields(data: Dict) -> Tuple[str, str]:
    """
    Extract key, summary and description from Jira issue data.
    
    Args:
        data: Jira response JSON object
        
    Returns:
        Tuple[str, str]: (key, summary_description)
        
    Raises:
        JiraAPIError: If required fields are missing
    """
    try:
        key = data.get('key')
        if not key:
            raise JiraAPIError("Missing 'key' field in Jira response")
        
        fields = data.get('fields', {})
        summary = fields.get('summary', '')
        description = fields.get('description', '')
        
        summary_description = f"{summary} {description}".strip()
        
        return key, summary_description
        
    except Exception as e:
        logger.error(f"Error parsing Jira issue fields: {str(e)}")
        raise JiraAPIError(f"Failed to parse Jira issue fields: {str(e)}")


def get_all_tickets() -> Optional[Dict[str, str]]:
    """
    Get all unresolved Jira tickets for the project.
    
    Returns:
        Optional[Dict[str, str]]: Dictionary mapping ticket keys to descriptions,
                                 or None if the request fails
    """
    try:
        jql = f"project={PROJECT_KEY} AND resolution=unresolved"
        endpoint = f"/rest/api/2/search?jql={jql}&maxResults=1000"
        
        response = _make_request("GET", endpoint)
        data = response.json()
        
        issues = data.get('issues', [])
        tickets = {}
        
        for issue in issues:
            try:
                key, description = parse_jira_issue_fields(issue)
                tickets[key] = description
            except JiraAPIError as e:
                logger.warning(f"Skipping issue due to parsing error: {str(e)}")
                continue
        
        logger.info(f"Retrieved {len(tickets)} tickets from Jira")
        return tickets
        
    except Exception as e:
        logger.error(f"Error getting all tickets: {str(e)}")
        return None


def get_ticket_data(key: str) -> Optional[Tuple[str, str]]:
    """
    Get Jira issue data by key.
    
    Args:
        key: Jira issue key
        
    Returns:
        Optional[Tuple[str, str]]: (key, description) tuple or None if not found
    """
    try:
        endpoint = f"/rest/agile/1.0/issue/{key}"
        response = _make_request("GET", endpoint)
        data = response.json()
        
        return parse_jira_issue_fields(data)
        
    except Exception as e:
        logger.error(f"Error getting ticket data for {key}: {str(e)}")
        return None


def add_jira_comment(key: str, comment: str) -> bool:
    """
    Add a comment to a Jira issue.
    
    Args:
        key: Jira issue key
        comment: Comment text to add
        
    Returns:
        bool: True if comment was added successfully
        
    Raises:
        JiraAPIError: If the comment operation fails
    """
    try:
        data = {"body": comment}
        endpoint = f"/rest/api/2/issue/{key}/comment"
        
        response = _make_request("POST", endpoint, data=data)
        
        if response.status_code == 201:
            logger.info(f"Successfully added comment to {key}")
            return True
        else:
            logger.error(f"Failed to add comment to {key}: {response.status_code}")
            return False
            
    except Exception as e:
        logger.error(f"Error adding comment to {key}: {str(e)}")
        raise JiraAPIError(f"Failed to add comment: {str(e)}")


def validate_jira_config() -> bool:
    """
    Validate Jira configuration and connectivity.
    
    Returns:
        bool: True if configuration is valid and connection works
    """
    try:
        # Check if all required environment variables are set
        if not all([JIRA_INSTANCE_URL, PROJECT_KEY, JIRA_USERNAME, JIRA_API_TOKEN]):
            logger.error("Missing required Jira environment variables")
            return False
        
        # Test connection by making a simple API call
        response = _make_request("GET", "/rest/api/2/myself")
        if response.status_code == 200:
            logger.info("Jira configuration is valid")
            return True
        else:
            logger.error(f"Jira connection test failed: {response.status_code}")
            return False
            
    except Exception as e:
        logger.error(f"Jira configuration validation failed: {str(e)}")
        return False 