"""
Main Mesop application for the AI Jira Assistant.

This module contains the main application pages and routing logic
for the AI Jira Assistant web interface.
"""

import logging
from typing import Optional

import mesop as me

# Local imports
try:
    from .utils import ui_components
    from .utils.config import get_config
except ImportError:
    from utils import ui_components
    from utils.config import get_config

logger = logging.getLogger(__name__)


@me.page(path="/")
def main_page(security_policy: me.SecurityPolicy = me.SecurityPolicy(dangerously_disable_trusted_types=True)) -> None:
    """
    Main application page.
    
    This is the primary interface for the AI Jira Assistant where users
    can interact with the Jira agent through a chat-like interface.
    
    Args:
        security_policy: Mesop security policy configuration
    """
    try:
        with me.box(
            style=me.Style(
                background="#fff",
                min_height="calc(100% - 48px)",
                padding=me.Padding(bottom=16),
            )
        ):
            with me.box(
                style=me.Style(
                    width="min(800px, 100%)",
                    margin=me.Margin.symmetric(horizontal="auto"),
                    padding=me.Padding.symmetric(horizontal=16),
                )
            ):
                ui_components.render_header()
                ui_components.render_example_prompts()
                ui_components.render_chat_interface()
                ui_components.render_output()
                ui_components.render_clear_button()
        
        ui_components.render_footer()
        
    except Exception as e:
        logger.error(f"Error rendering main page: {str(e)}")
        me.navigate("/error")


@me.page(path="/error")
def error_page(security_policy: me.SecurityPolicy = me.SecurityPolicy(dangerously_disable_trusted_types=True)) -> None:
    """
    Error page for handling application errors.
    
    This page is displayed when an error occurs in the application,
    providing users with a way to navigate back to the main interface.
    
    Args:
        security_policy: Mesop security policy configuration
    """
    try:
        with me.box(
            style=me.Style(
                background="#fff",
                min_height="calc(100% - 48px)",
                padding=me.Padding(bottom=16),
            )
        ):
            with me.box(
                style=me.Style(
                    width="min(720px, 100%)",
                    margin=me.Margin.symmetric(horizontal="auto"),
                    padding=me.Padding.symmetric(horizontal=16),
                )
            ):
                ui_components.render_header()
                ui_components.render_error_content()
        
        ui_components.render_footer()
        
    except Exception as e:
        logger.error(f"Error rendering error page: {str(e)}")
        # Fallback to basic error display
        me.text("An unexpected error occurred. Please refresh the page.")


@me.page(path="/health")
def health_page(security_policy: me.SecurityPolicy = me.SecurityPolicy(dangerously_disable_trusted_types=True)) -> None:
    """
    Health check page for monitoring and debugging.
    
    This page provides system health information and can be used
    for monitoring the application status.
    
    Args:
        security_policy: Mesop security policy configuration
    """
    try:
        config = get_config()
        
        with me.box(
            style=me.Style(
                background="#fff",
                min_height="calc(100% - 48px)",
                padding=me.Padding.all(16),
            )
        ):
            with me.box(
                style=me.Style(
                    width="min(600px, 100%)",
                    margin=me.Margin.symmetric(horizontal="auto"),
                )
            ):
                me.text(
                    "AI Jira Assistant - Health Check",
                    style=me.Style(
                        text_align="center",
                        font_size=24,
                        font_weight=700,
                        margin=me.Margin(bottom=20),
                    ),
                )
                
                # Display configuration status
                with me.box(style=me.Style(margin=me.Margin(bottom=16))):
                    me.text("Configuration Status:", style=me.Style(font_weight=600))
                    me.text(f"Project Key: {config.project_key or 'Not configured'}")
                    me.text(f"Docker Running: {config.docker_running}")
                    me.text(f"Django URL: {config.django_url}")
                
                # Display state information
                with me.box(style=me.Style(margin=me.Margin(bottom=16))):
                    me.text("Application State:", style=me.Style(font_weight=600))
                    me.text(f"Input Length: {len(config.state.input)}")
                    me.text(f"Output Length: {len(config.state.output)}")
                    me.text(f"In Progress: {config.state.in_progress}")
                
                # Navigation button
                me.button(
                    "Back to Main Page",
                    type="flat",
                    on_click=lambda _: me.navigate("/")
                )
                
    except Exception as e:
        logger.error(f"Error rendering health page: {str(e)}")
        me.text("Health check failed. Please check the logs.")
