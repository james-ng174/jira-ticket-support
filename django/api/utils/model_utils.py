"""Model utilities for Jira agent functionality."""

import json
import logging
import os
from pathlib import Path
from typing import Dict, List, Optional, Tuple
import concurrent.futures

from langchain.agents import AgentType, initialize_agent
from langchain_community.agent_toolkits.jira.toolkit import JiraToolkit
from langchain_community.utilities.jira import JiraAPIWrapper
from langchain_openai import OpenAI
from langchain.tools import tool
from langchain_core.prompts import ChatPromptTemplate, FewShotChatMessagePromptTemplate

from api.utils import jira_utils

logger = logging.getLogger(__name__)


class LLMTask:
    """
    Wrapper class for LLM tasks with few-shot prompting.
    
    This class handles the construction and execution of LLM prompts
    with system prompts and example-based learning.
    """
    
    def __init__(self, system_prompt: str, examples: List[Dict], llm: OpenAI):
        """
        Initialize the LLM task.
        
        Args:
            system_prompt: The system prompt for the LLM
            examples: List of example input/output pairs
            llm: The LLM instance to use
        """
        self.system_prompt = system_prompt
        self.examples = examples
        self.llm = llm
        self._chain = None
    
    def construct_prompt(self) -> ChatPromptTemplate:
        """
        Construct the prompt template with few-shot examples.
        
        Returns:
            ChatPromptTemplate: The constructed prompt template
        """
        example_prompt = ChatPromptTemplate.from_messages([
            ("human", "{input}"),
            ("ai", "{output}"),
        ])
        
        few_shot_prompt = FewShotChatMessagePromptTemplate(
            example_prompt=example_prompt,
            examples=self.examples,
        )
        
        return ChatPromptTemplate.from_messages([
            ("system", self.system_prompt),
            few_shot_prompt,
            ("human", "{input}"),
        ])
    
    def run_llm(self, input_text: str) -> Optional[str]:
        """
        Run the LLM with the given input.
        
        Args:
            input_text: The input text for the LLM
            
        Returns:
            Optional[str]: The LLM response or None if failed
        """
        try:
            if self._chain is None:
                self._chain = self.construct_prompt() | self.llm
            
            result = self._chain.invoke({"input": input_text})
            return result
            
        except Exception as e:
            logger.error(f"Error running LLM task: {str(e)}")
            return None


class JiraAgentManager:
    """
    Manager class for Jira agent operations.
    
    This class handles the initialization and management of the Jira agent
    and provides methods for common operations like triaging tickets.
    """
    
    def __init__(self):
        """Initialize the Jira agent manager."""
        self.llm = None
        self.product_model = None
        self.linking_model = None
        self.agent = None
        self._load_configuration()
    
    def _load_configuration(self) -> None:
        """Load configuration files and initialize components."""
        try:
            # Load prompt files
            utils_dir = Path(__file__).parent
            system_prompts_path = utils_dir / "system_prompts.json"
            example_prompts_path = utils_dir / "example_prompts.json"
            
            if not system_prompts_path.exists():
                raise FileNotFoundError(f"System prompts file not found: {system_prompts_path}")
            if not example_prompts_path.exists():
                raise FileNotFoundError(f"Example prompts file not found: {example_prompts_path}")
            
            with open(system_prompts_path) as f:
                system_prompts = json.load(f)
            with open(example_prompts_path) as f:
                example_prompts = json.load(f)
            
            # Initialize LLM
            self.llm = OpenAI(temperature=0)
            
            # Initialize models
            self.product_model = LLMTask(
                system_prompts.get("system_prompt_product"),
                example_prompts.get("examples_product", []),
                self.llm
            )
            self.linking_model = LLMTask(
                system_prompts.get("system_prompt_linking"),
                example_prompts.get("examples_linking", []),
                self.llm
            )
            
            # Initialize Jira agent
            jira = JiraAPIWrapper()
            toolkit = JiraToolkit.from_jira_api_wrapper(jira)
            self.agent = initialize_agent(
                toolkit.get_tools() + [self._triage_tool],
                self.llm,
                agent=AgentType.ZERO_SHOT_REACT_DESCRIPTION,
                verbose=True,
                max_iterations=5,
                return_intermediate_steps=True
            )
            
            logger.info("Jira agent manager initialized successfully")
            
        except Exception as e:
            logger.error(f"Error initializing Jira agent manager: {str(e)}")
            raise
    
    @tool
    def _triage_tool(self, ticket_number: str) -> str:
        """
        Triage a given ticket and link related tickets.
        
        Args:
            ticket_number: The ticket number to triage
            
        Returns:
            str: Status message indicating completion
        """
        try:
            ticket_number = str(ticket_number)
            logger.info(f"Starting triage for ticket: {ticket_number}")
            
            # Get all tickets and primary ticket data
            all_tickets = jira_utils.get_all_tickets()
            if not all_tickets:
                logger.warning("No tickets found for triage")
                return "No tickets found for triage"
            
            primary_ticket_data = jira_utils.get_ticket_data(ticket_number)
            if not primary_ticket_data:
                logger.error(f"Could not retrieve data for ticket: {ticket_number}")
                return f"Could not retrieve data for ticket: {ticket_number}"
            
            primary_issue_key, primary_issue_data = primary_ticket_data
            
            # Find and link related tickets
            self._find_related_tickets(primary_issue_key, primary_issue_data, all_tickets)
            
            # Generate user stories, acceptance criteria, and priority
            self._generate_ticket_metadata(primary_issue_key, primary_issue_data)
            
            logger.info(f"Triage completed for ticket: {ticket_number}")
            return "Task complete"
            
        except Exception as e:
            logger.error(f"Error during triage: {str(e)}")
            return f"Error during triage: {str(e)}"
    
    def _find_related_tickets(
        self, 
        primary_issue_key: str, 
        primary_issue_data: str, 
        issues: Dict[str, str]
    ) -> None:
        """
        Find and link related tickets using concurrent processing.
        
        Args:
            primary_issue_key: The primary ticket key
            primary_issue_data: The primary ticket description
            issues: Dictionary of all available tickets
        """
        try:
            args = [
                (key, data, primary_issue_key, primary_issue_data) 
                for key, data in issues.items()
            ]
            
            with concurrent.futures.ThreadPoolExecutor(max_workers=os.cpu_count()) as executor:
                executor.map(self._check_issue_and_link_helper, args)
                
        except Exception as e:
            logger.error(f"Error finding related tickets: {str(e)}")
    
    def _check_issue_and_link_helper(self, args: Tuple[str, str, str, str]) -> None:
        """
        Helper function to check if two tickets are related and link them.
        
        Args:
            args: Tuple containing (key, data, primary_issue_key, primary_issue_data)
        """
        key, data, primary_issue_key, primary_issue_data = args
        
        try:
            if key != primary_issue_key and self._llm_check_ticket_match(primary_issue_data, data):
                jira_utils.link_jira_issue(primary_issue_key, key)
                
        except Exception as e:
            logger.error(f"Error checking issue link for {key}: {str(e)}")
    
    def _llm_check_ticket_match(self, ticket1: str, ticket2: str) -> bool:
        """
        Use LLM to check if two tickets are related.
        
        Args:
            ticket1: First ticket description
            ticket2: Second ticket description
            
        Returns:
            bool: True if tickets are related
        """
        try:
            if not self.linking_model:
                logger.error("Linking model not initialized")
                return False
            
            prompt = f"<ticket1>{ticket1}<ticket1><ticket2>{ticket2}<ticket2>"
            llm_result = self.linking_model.run_llm(prompt)
            
            if not llm_result:
                return False
            
            result = jira_utils.extract_tag_helper(llm_result, "related")
            return result == 'True' if result else False
            
        except Exception as e:
            logger.error(f"Error checking ticket match: {str(e)}")
            return False
    
    def _generate_ticket_metadata(self, primary_issue_key: str, primary_issue_data: str) -> None:
        """
        Generate user stories, acceptance criteria, and priority for a ticket.
        
        Args:
            primary_issue_key: The ticket key
            primary_issue_data: The ticket description
        """
        try:
            if not self.product_model:
                logger.error("Product model not initialized")
                return
            
            prompt = f"<description>{primary_issue_data}<description>"
            llm_result = self.product_model.run_llm(prompt)
            
            if not llm_result:
                logger.warning("No LLM result for metadata generation")
                return
            
            # Extract metadata from LLM result
            user_stories = jira_utils.extract_tag_helper(llm_result, "user_stories") or ''
            acceptance_criteria = jira_utils.extract_tag_helper(llm_result, "acceptance_criteria") or ''
            priority = jira_utils.extract_tag_helper(llm_result, "priority") or ''
            thought = jira_utils.extract_tag_helper(llm_result, "thought") or ''
            
            # Create comment
            comment = (
                f"user_stories: {user_stories}\n"
                f"acceptance_criteria: {acceptance_criteria}\n"
                f"priority: {priority}\n"
                f"thought: {thought}"
            )
            
            # Add comment to Jira ticket
            jira_utils.add_jira_comment(primary_issue_key, comment)
            
        except Exception as e:
            logger.error(f"Error generating ticket metadata: {str(e)}")
    
    def invoke_agent(self, input_data: Dict[str, str]) -> Optional[Dict]:
        """
        Invoke the Jira agent with input data.
        
        Args:
            input_data: Dictionary containing the input for the agent
            
        Returns:
            Optional[Dict]: Agent response or None if failed
        """
        try:
            if not self.agent:
                logger.error("Agent not initialized")
                return None
            
            return self.agent.invoke(input_data)
            
        except Exception as e:
            logger.error(f"Error invoking agent: {str(e)}")
            return None


# Global instance of the agent manager
_agent_manager = None


def get_agent_manager() -> JiraAgentManager:
    """
    Get the global agent manager instance.
    
    Returns:
        JiraAgentManager: The agent manager instance
    """
    global _agent_manager
    if _agent_manager is None:
        _agent_manager = JiraAgentManager()
    return _agent_manager


def get_agent() -> Optional[object]:
    """
    Get the Jira agent instance.
    
    Returns:
        Optional[object]: The agent instance or None if not available
    """
    try:
        manager = get_agent_manager()
        return manager.agent
    except Exception as e:
        logger.error(f"Error getting agent: {str(e)}")
        return None


# For backward compatibility
agent = get_agent() 