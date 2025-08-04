"""Management command to test Jira configuration and connectivity."""

import logging
from django.core.management.base import BaseCommand, CommandError
from api.utils import jira_utils

logger = logging.getLogger(__name__)


class Command(BaseCommand):
    """
    Test Jira configuration and connectivity.
    
    This command validates the Jira configuration and tests connectivity
    to ensure the application can properly interact with Jira.
    """
    
    help = 'Test Jira configuration and connectivity'
    
    def add_arguments(self, parser):
        """Add command arguments."""
        parser.add_argument(
            '--verbose',
            action='store_true',
            help='Enable verbose output',
        )
    
    def handle(self, *args, **options):
        """
        Execute the command.
        
        Args:
            *args: Command arguments
            **options: Command options
        """
        verbose = options.get('verbose', False)
        
        if verbose:
            self.stdout.write(self.style.SUCCESS('Testing Jira configuration...'))
        
        try:
            # Test configuration validation
            if verbose:
                self.stdout.write('Validating Jira configuration...')
            
            if not jira_utils.validate_jira_config():
                raise CommandError('Jira configuration validation failed')
            
            self.stdout.write(
                self.style.SUCCESS('✓ Jira configuration is valid')
            )
            
            # Test getting tickets
            if verbose:
                self.stdout.write('Testing ticket retrieval...')
            
            tickets = jira_utils.get_all_tickets()
            if tickets is None:
                raise CommandError('Failed to retrieve tickets from Jira')
            
            self.stdout.write(
                self.style.SUCCESS(f'✓ Successfully retrieved {len(tickets)} tickets')
            )
            
            # Test getting a specific ticket if available
            if tickets:
                sample_key = list(tickets.keys())[0]
                if verbose:
                    self.stdout.write(f'Testing retrieval of specific ticket: {sample_key}')
                
                ticket_data = jira_utils.get_ticket_data(sample_key)
                if ticket_data:
                    self.stdout.write(
                        self.style.SUCCESS(f'✓ Successfully retrieved ticket: {sample_key}')
                    )
                else:
                    self.stdout.write(
                        self.style.WARNING(f'⚠ Could not retrieve specific ticket: {sample_key}')
                    )
            
            self.stdout.write(
                self.style.SUCCESS('All Jira configuration tests passed!')
            )
            
        except Exception as e:
            self.stdout.write(
                self.style.ERROR(f'Jira configuration test failed: {str(e)}')
            )
            raise CommandError(f'Configuration test failed: {str(e)}') 