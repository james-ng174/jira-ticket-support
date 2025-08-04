"""
UI components for the AI Jira Assistant application.

This module contains all the user interface components for the Mesop application,
including layout, styling, and event handling for the chat interface.
"""

import logging
from typing import Optional

import mesop as me

from .config import get_config, get_state
from .api_utils import get_api_client

logger = logging.getLogger(__name__)


class UIComponents:
    """
    UI components manager for the AI Jira Assistant.
    
    This class manages all UI components and their interactions,
    providing a clean interface for rendering the application.
    """
    
    def __init__(self):
        """Initialize the UI components manager."""
        self.config = get_config()
        self.state = get_state()
        self.api_client = get_api_client()
    
    def render_header(self) -> None:
        """Render the application header with title and icon."""
        try:
            # Icon section
            with me.box(
                style=me.Style(
                    padding=me.Padding(top=50, bottom=10),
                )
            ):
                me.icon(
                    "psychology",
                    style=me.Style(
                        display="block",
                        width="100%",
                        height="100%",
                        font_size=50,
                        text_align="center",
                        font_weight=100,
                        background="linear-gradient(90deg, #4285F4, #AA5CDB, #DB4437) text",
                        color="transparent",
                    ),
                )
            
            # Title section
            with me.box(
                style=me.Style(
                    padding=me.Padding(top=0, bottom=40),
                )
            ):
                me.text(
                    "AI JIRA ASSISTANT",
                    style=me.Style(
                        text_align="center",
                        font_size=30,
                        font_weight=700,
                        background="linear-gradient(90deg, #4285F4, #AA5CDB, #DB4437) text",
                        color="transparent",
                    ),
                )
                
        except Exception as e:
            logger.error(f"Error rendering header: {str(e)}")
    
    def render_example_prompts(self) -> None:
        """Render the example prompts section."""
        try:
            is_mobile = me.viewport_size().width < 640
            
            with me.box(
                style=me.Style(
                    display="flex",
                    flex_direction="column" if is_mobile else "row",
                    gap=10,
                    margin=me.Margin(bottom=40),
                )
            ):
                for example in self.config.example_prompts:
                    self._render_prompt_box(example, is_mobile)
                    
        except Exception as e:
            logger.error(f"Error rendering example prompts: {str(e)}")
    
    def _render_prompt_box(self, example: str, is_mobile: bool) -> None:
        """
        Render a single example prompt box.
        
        Args:
            example: The example prompt text
            is_mobile: Whether the device is mobile
        """
        try:
            with me.box(
                style=me.Style(
                    width="100%" if is_mobile else 200,
                    height=250,
                    text_align="center",
                    background="#F0F4F9",
                    padding=me.Padding.all(16),
                    font_weight=500,
                    line_height="1.5",
                    border_radius=16,
                    cursor="pointer",
                ),
                key=example,
                on_click=self._handle_prompt_click,
            ):
                me.text(example)
                
        except Exception as e:
            logger.error(f"Error rendering prompt box: {str(e)}")
    
    def _handle_prompt_click(self, event: me.ClickEvent) -> None:
        """
        Handle click events on example prompts.
        
        Args:
            event: The click event
        """
        try:
            self.state.set_input(event.key)
            logger.debug(f"Example prompt selected: {event.key[:50]}...")
            
        except Exception as e:
            logger.error(f"Error handling prompt click: {str(e)}")
    
    def render_chat_interface(self) -> None:
        """Render the chat input interface."""
        try:
            with me.box(
                style=me.Style(
                    padding=me.Padding.all(8),
                    background="white",
                    display="flex",
                    width="100%",
                    border=me.Border.all(me.BorderSide(width=0, style="solid", color="black")),
                    border_radius=12,
                    box_shadow="0 10px 20px #0000000a, 0 2px 6px #0000000a, 0 0 1px #0000000a",
                )
            ):
                # Text area
                with me.box(style=me.Style(flex_grow=1)):
                    me.native_textarea(
                        value=self.state.input,
                        autosize=True,
                        min_rows=4,
                        placeholder="Enter your prompt",
                        style=me.Style(
                            padding=me.Padding(top=16, left=16),
                            background="white",
                            outline="none",
                            width="100%",
                            overflow_y="auto",
                            border=me.Border.all(me.BorderSide(style="none")),
                        ),
                        on_blur=self._handle_textarea_blur,
                    )
                
                # Send button
                with me.content_button(type="icon", on_click=self._handle_send_click):
                    me.icon("send")
                    
        except Exception as e:
            logger.error(f"Error rendering chat interface: {str(e)}")
    
    def _handle_textarea_blur(self, event: me.InputBlurEvent) -> None:
        """
        Handle textarea blur events.
        
        Args:
            event: The blur event
        """
        try:
            self.state.set_input(event.value)
            
        except Exception as e:
            logger.error(f"Error handling textarea blur: {str(e)}")
    
    def _handle_send_click(self, event: me.ClickEvent) -> None:
        """
        Handle send button click events.
        
        Args:
            event: The click event
        """
        try:
            if not self.state.input or not self.state.input.strip():
                logger.debug("Empty input, ignoring send click")
                return
            
            # Start processing
            self.state.start_processing()
            input_text = self.state.input
            self.state.set_input("")
            
            # Process the request
            self._process_request(input_text)
            
        except Exception as e:
            logger.error(f"Error handling send click: {str(e)}")
            self.state.stop_processing()
            self.state.set_error("An error occurred while processing your request")
    
    def _process_request(self, input_text: str) -> None:
        """
        Process a user request through the API.
        
        Args:
            input_text: The user's input text
        """
        try:
            # Call the API
            result = self.api_client.call_jira_agent(input_text)
            
            if result:
                self.state.append_output(result)
                logger.info("Request processed successfully")
            else:
                logger.warning("API returned no result")
                me.navigate("/error")
            
        except Exception as e:
            logger.error(f"Error processing request: {str(e)}")
            me.navigate("/error")
        finally:
            self.state.stop_processing()
    
    def render_output(self) -> None:
        """Render the output section."""
        try:
            if self.state.output or self.state.in_progress:
                with me.box(
                    style=me.Style(
                        background="#F0F4F9",
                        padding=me.Padding.all(16),
                        border_radius=16,
                        margin=me.Margin(top=36),
                    )
                ):
                    # Display output content
                    if self.state.output:
                        me.markdown(self.state.output)
                    
                    # Display error message if any
                    if self.state.error_message:
                        me.text(
                            f"Error: {self.state.error_message}",
                            style=me.Style(color="red", font_weight=600)
                        )
                    
                    # Show loading spinner
                    if self.state.in_progress:
                        with me.box(style=me.Style(margin=me.Margin(top=16))):
                            me.progress_spinner()
                            
        except Exception as e:
            logger.error(f"Error rendering output: {str(e)}")
    
    def render_clear_button(self) -> None:
        """Render the clear output button."""
        try:
            with me.box(style=me.Style(margin=me.Margin.all(15))):
                with me.box(style=me.Style(display="flex", flex_direction="row", gap=12)):
                    me.button(
                        "Clear output", 
                        type="flat", 
                        on_click=self._handle_clear_click
                    )
                    
        except Exception as e:
            logger.error(f"Error rendering clear button: {str(e)}")
    
    def _handle_clear_click(self, event: me.ClickEvent) -> None:
        """
        Handle clear button click events.
        
        Args:
            event: The click event
        """
        try:
            self.state.clear_output()
            logger.debug("Output cleared")
            
        except Exception as e:
            logger.error(f"Error handling clear click: {str(e)}")
    
    def render_footer(self) -> None:
        """Render the application footer."""
        try:
            with me.box(
                style=me.Style(
                    position="sticky",
                    bottom=0,
                    padding=me.Padding.symmetric(vertical=16, horizontal=16),
                    width="100%",
                    background="#F0F4F9",
                    font_size=14,
                )
            ):
                me.html(
                    "Made with <a href='https://google.github.io/mesop/'>Mesop</a>",
                )
                
        except Exception as e:
            logger.error(f"Error rendering footer: {str(e)}")
    
    def render_error_content(self) -> None:
        """Render the error page content."""
        try:
            is_mobile = me.viewport_size().width < 640
            
            with me.box(
                style=me.Style(
                    position="sticky",
                    width="100%",
                    display="block",
                    height="100%",
                    font_size=50,
                    text_align="center",
                    flex_direction="column" if is_mobile else "row",
                    gap=10,
                    margin=me.Margin(bottom=30),
                )
            ):
                me.text(
                    "AN ERROR HAS OCCURRED",
                    style=me.Style(
                        text_align="center",
                        font_size=30,
                        font_weight=700,
                        padding=me.Padding.all(8),
                        background="white",
                        justify_content="center",
                        display="flex",
                        width="100%",
                    ),
                )
                
                me.button(
                    "Navigate to home page",
                    type="flat",
                    on_click=self._handle_navigate_home
                )
                
        except Exception as e:
            logger.error(f"Error rendering error content: {str(e)}")
    
    def _handle_navigate_home(self, event: me.ClickEvent) -> None:
        """
        Handle navigation to home page.
        
        Args:
            event: The click event
        """
        try:
            me.navigate("/")
            logger.debug("Navigating to home page")
            
        except Exception as e:
            logger.error(f"Error navigating to home: {str(e)}")


# Global UI components instance
_ui_components: Optional[UIComponents] = None


def get_ui_components() -> UIComponents:
    """
    Get the global UI components instance.
    
    Returns:
        UIComponents: The UI components instance
    """
    global _ui_components
    if _ui_components is None:
        _ui_components = UIComponents()
    return _ui_components


# Backward compatibility functions
def render_header() -> None:
    """Render the application header (backward compatibility)."""
    get_ui_components().render_header()


def render_example_prompts() -> None:
    """Render the example prompts (backward compatibility)."""
    get_ui_components().render_example_prompts()


def render_chat_interface() -> None:
    """Render the chat interface (backward compatibility)."""
    get_ui_components().render_chat_interface()


def render_output() -> None:
    """Render the output section (backward compatibility)."""
    get_ui_components().render_output()


def render_clear_button() -> None:
    """Render the clear button (backward compatibility)."""
    get_ui_components().render_clear_button()


def render_footer() -> None:
    """Render the footer (backward compatibility)."""
    get_ui_components().render_footer()


def render_error_content() -> None:
    """Render the error content (backward compatibility)."""
    get_ui_components().render_error_content()
