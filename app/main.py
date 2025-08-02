import ollama
import logging
from typing import Dict, Any, Union, Optional, List
from app.prompt.prompt_template import PromptManager
from app.utils.ollama_utils import OllamaManager
from app.extractor.mom_extractor import MoMExtractor
from app.formatter.mom_formatter import MoMFormatter
from app.integrations import (
    ExternalIntegrations, 
    TaskManagementIntegration, 
    CalendarIntegration, 
    EmailIntegration
)
from integrations.base import IntegrationConfig, IntegrationType, AuthMethod

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class MoMGenerator:
    def __init__(self, model_name="llama3:latest", config: Optional[Dict[str, Any]] = None):
        self.model_name = model_name
        self.config = config or {}
        self.prompt_manager = PromptManager()
        self.ollama_manager = OllamaManager(model_name)
        self.mom_extractor = MoMExtractor(model_name)
        self.mom_formatter = MoMFormatter()
        
        # Initialize external integrations
        self.integrations = ExternalIntegrations(self.config.get('integrations', {}))
        self._setup_integrations()
    
    def _setup_integrations(self):
        """Set up external integrations based on configuration."""
        integrations_config = self.config.get('integrations', {})
        
        # Set up task management integrations
        task_configs = integrations_config.get('task_management', {})
        for name, config in task_configs.items():
            try:
                integration_config = IntegrationConfig(
                    name=name,
                    integration_type=IntegrationType.TASK_MANAGEMENT,
                    auth_method=AuthMethod(config.get('auth_method', 'api_key')),
                    credentials=config.get('credentials', {}),
                    settings=config.get('settings', {}),
                    enabled=config.get('enabled', True)
                )
                
                # Create specific integration based on type
                integration_type = config.get('type', 'generic')
                if integration_type == 'asana':
                    from integrations.task_management import AsanaIntegration
                    integration = AsanaIntegration(integration_config)
                elif integration_type == 'trello':
                    from integrations.task_management import TrelloIntegration
                    integration = TrelloIntegration(integration_config)
                elif integration_type == 'jira':
                    from integrations.task_management import JiraIntegration
                    integration = JiraIntegration(integration_config)
                else:
                    integration = TaskManagementIntegration(integration_config)
                
                self.integrations.register_integration(integration)
                logger.info(f"Registered task management integration: {name}")
                
            except Exception as e:
                logger.error(f"Failed to setup task management integration '{name}': {e}")
        
        # Set up calendar integrations
        calendar_configs = integrations_config.get('calendar', {})
        for name, config in calendar_configs.items():
            try:
                integration_config = IntegrationConfig(
                    name=name,
                    integration_type=IntegrationType.CALENDAR,
                    auth_method=AuthMethod(config.get('auth_method', 'oauth2')),
                    credentials=config.get('credentials', {}),
                    settings=config.get('settings', {}),
                    enabled=config.get('enabled', True)
                )
                
                # Create specific integration based on type
                integration_type = config.get('type', 'generic')
                if integration_type == 'google':
                    from integrations.calendar import GoogleCalendarIntegration
                    integration = GoogleCalendarIntegration(integration_config)
                elif integration_type == 'outlook':
                    from integrations.calendar import OutlookCalendarIntegration
                    integration = OutlookCalendarIntegration(integration_config)
                else:
                    integration = CalendarIntegration(integration_config)
                
                self.integrations.register_integration(integration)
                logger.info(f"Registered calendar integration: {name}")
                
            except Exception as e:
                logger.error(f"Failed to setup calendar integration '{name}': {e}")
        
        # Set up email integrations
        email_configs = integrations_config.get('email', {})
        for name, config in email_configs.items():
            try:
                integration_config = IntegrationConfig(
                    name=name,
                    integration_type=IntegrationType.EMAIL,
                    auth_method=AuthMethod(config.get('auth_method', 'basic_auth')),
                    credentials=config.get('credentials', {}),
                    settings=config.get('settings', {}),
                    enabled=config.get('enabled', True)
                )
                
                # Create specific integration based on type
                integration_type = config.get('type', 'smtp')
                if integration_type == 'gmail':
                    from integrations.email import GmailIntegration
                    integration = GmailIntegration(integration_config)
                elif integration_type == 'outlook':
                    from integrations.email import OutlookEmailIntegration
                    integration = OutlookEmailIntegration(integration_config)
                else:
                    from integrations.email import SMTPIntegration
                    integration = SMTPIntegration(integration_config)
                
                self.integrations.register_integration(integration)
                logger.info(f"Registered email integration: {name}")
                
            except Exception as e:
                logger.error(f"Failed to setup email integration '{name}': {e}")

    def setup(self) -> tuple[bool, str]:
        """checks if the model and server are ready
            returns (bool,str)
        """
        if not self.ollama_manager.is_server_running():
            return False,"Ollama server is not running"
        
        if not self.ollama_manager.is_model_available():
            success = self.ollama_manager.pull_model()
            if not success:
                return False,f"failed to pull {self.model_name} model"
        return True, "server and model are setup"
    
    def generate_mom(self, transcript) -> str:
        """ generates mom"""
        try:
            message = self.prompt_manager.chat_prompt.format_messages(transcript=transcript)
            payload = [
                {"role": "system", "content":message[0].content},
                {"role": "user", "content":message[1].content}
            ]
            logger.info(f"Sending transcript to model '{self.model_name}'")
            response = ollama.chat(model=self.model_name, messages=payload)
            return response["message"]["content"]
        except Exception as e:
            logger.error(f"error generating MoM:{e}")
            raise RuntimeError(f"failed to generate MoM: {e}")
    
    def generate_mom_with_options(self, transcript, options: Dict[str, Any]) -> Union[str, Dict[str, Any]]:
        """
        Generate MoM with additional options.
        
        Args:
            transcript (str): The meeting transcript text
            options (Dict[str, Any]): Generation options
            
        Returns:
            Union[str, Dict[str, Any]]: Generated MoM (string or structured data)
            
        Raises:
            RuntimeError: If generation fails
        """
        try:
            # Extract MoM data with options
            mom_data = self.mom_extractor.extract_with_options(transcript, options)
            
            # Format output if not structured
            if not options.get('structured_output', False):
                format_type = options.get('format_type', 'text')
                format_options = {
                    'include_tables': options.get('include_tables', False),
                    'include_toc': options.get('include_toc', False),
                    'include_frontmatter': options.get('include_frontmatter', False),
                    'include_subject': options.get('include_subject', False),
                    'template': options.get('template'),
                    'include_analytics': options.get('include_analytics', False)
                }
                
                # Format MoM data
                mom_output = self.mom_formatter.format_with_options(mom_data, format_type, format_options)
                return mom_output
            
            # Return structured data
            return mom_data
        
        except Exception as e:
            logger.error(f"Error generating MoM with options: {e}")
            raise RuntimeError(f"Failed to generate MoM: {e}")
    
    def generate_mom_with_integrations(self, transcript: str, options: Dict[str, Any]) -> Dict[str, Any]:
        """
        Generate MoM with integration support.
        
        Args:
            transcript: The meeting transcript text
            options: Generation and integration options
            
        Returns:
            Dictionary containing MoM data and integration results
            
        Raises:
            RuntimeError: If generation fails
        """
        try:
            # Generate MoM data
            mom_data = self.mom_extractor.extract_with_options(transcript, options)
            
            # Format output
            format_type = options.get('format_type', 'text')
            format_options = {
                'include_tables': options.get('include_tables', False),
                'include_toc': options.get('include_toc', False),
                'include_frontmatter': options.get('include_frontmatter', False),
                'include_subject': options.get('include_subject', False),
                'template': options.get('template'),
                'include_analytics': options.get('include_analytics', False)
            }
            
            mom_output = self.mom_formatter.format_with_options(mom_data, format_type, format_options)
            
            # Handle integrations
            integration_results = {}
            
            # Sync action items with task management
            if options.get('sync_tasks') and mom_data.get('action_items'):
                task_integration = options.get('task_integration')
                if task_integration:
                    result = self.sync_action_items(mom_data['action_items'], task_integration)
                    integration_results['task_sync'] = result
            
            # Create calendar events for follow-up meetings
            if options.get('create_calendar_events'):
                calendar_integration = options.get('calendar_integration')
                if calendar_integration and mom_data.get('next_steps'):
                    result = self.create_follow_up_events(mom_data, calendar_integration)
                    integration_results['calendar_events'] = result
            
            # Send email with MoM
            if options.get('send_email'):
                email_integration = options.get('email_integration')
                recipients = options.get('email_recipients', [])
                if email_integration and recipients:
                    result = self.send_mom_email(mom_data, recipients, email_integration)
                    integration_results['email_sent'] = result
            
            return {
                'mom_data': mom_data,
                'mom_output': mom_output,
                'integration_results': integration_results
            }
        
        except Exception as e:
            logger.error(f"Error generating MoM with integrations: {e}")
            raise RuntimeError(f"Failed to generate MoM with integrations: {e}")
    
    def sync_action_items(self, action_items: List[Dict[str, Any]], integration_name: str) -> Dict[str, Any]:
        """
        Sync action items with a task management system.
        
        Args:
            action_items: List of action items to sync
            integration_name: Name of the task management integration
            
        Returns:
            Result of the sync operation
        """
        try:
            result = self.integrations.sync_action_items(action_items, integration_name)
            return {
                'success': result.success,
                'message': result.message,
                'data': result.data,
                'error': result.error
            }
        except Exception as e:
            logger.error(f"Error syncing action items: {e}")
            return {
                'success': False,
                'message': 'Failed to sync action items',
                'error': str(e)
            }
    
    def create_follow_up_events(self, mom_data: Dict[str, Any], integration_name: str) -> Dict[str, Any]:
        """
        Create calendar events for follow-up meetings mentioned in MoM.
        
        Args:
            mom_data: Meeting minutes data
            integration_name: Name of the calendar integration
            
        Returns:
            Result of the event creation
        """
        try:
            events_created = []
            
            # Look for follow-up meetings in next steps
            next_steps = mom_data.get('next_steps', [])
            for step in next_steps:
                if any(keyword in step.lower() for keyword in ['meeting', 'follow-up', 'schedule', 'call']):
                    # Create a basic event
                    event_data = {
                        'title': f"Follow-up: {step}",
                        'description': f"Follow-up from meeting: {mom_data.get('meeting_title', 'Meeting')}",
                        'attendees': [att.get('name', '') for att in mom_data.get('attendees', [])],
                        'start_time': None,  # Would need to be parsed from the step text
                        'end_time': None
                    }
                    
                    result = self.integrations.create_calendar_event(event_data, integration_name)
                    events_created.append({
                        'step': step,
                        'result': {
                            'success': result.success,
                            'message': result.message,
                            'data': result.data,
                            'error': result.error
                        }
                    })
            
            return {
                'success': len(events_created) > 0,
                'message': f"Processed {len(events_created)} follow-up events",
                'events': events_created
            }
        
        except Exception as e:
            logger.error(f"Error creating follow-up events: {e}")
            return {
                'success': False,
                'message': 'Failed to create follow-up events',
                'error': str(e)
            }
    
    def send_mom_email(self, mom_data: Dict[str, Any], recipients: List[str], 
                       integration_name: str, template_name: str = 'default') -> Dict[str, Any]:
        """
        Send meeting minutes via email.
        
        Args:
            mom_data: Meeting minutes data
            recipients: List of email recipients
            integration_name: Name of the email integration
            template_name: Name of the email template to use
            
        Returns:
            Result of the email sending operation
        """
        try:
            integration = self.integrations.get_integration(integration_name)
            if not integration:
                return {
                    'success': False,
                    'message': f"Email integration '{integration_name}' not found",
                    'error': 'Integration not found'
                }
            
            result = integration.send_mom_email(mom_data, recipients, template_name)
            return {
                'success': result.success,
                'message': result.message,
                'data': result.data,
                'error': result.error
            }
        
        except Exception as e:
            logger.error(f"Error sending MoM email: {e}")
            return {
                'success': False,
                'message': 'Failed to send MoM email',
                'error': str(e)
            }
    
    def test_integrations(self) -> Dict[str, Any]:
        """
        Test all configured integrations.
        
        Returns:
            Dictionary with test results for each integration
        """
        results = {}
        
        for integration_name in self.integrations.list_integrations():
            try:
                result = self.integrations.test_integration(integration_name)
                results[integration_name] = {
                    'success': result.success,
                    'message': result.message,
                    'data': result.data,
                    'error': result.error
                }
            except Exception as e:
                results[integration_name] = {
                    'success': False,
                    'message': 'Test failed',
                    'error': str(e)
                }
        
        return results
    
    def get_integration_status(self) -> Dict[str, Any]:
        """
        Get status of all integrations.
        
        Returns:
            Dictionary with status information for each integration
        """
        status = {
            'total_integrations': len(self.integrations.list_integrations()),
            'integrations': {}
        }
        
        for integration_name in self.integrations.list_integrations():
            integration = self.integrations.get_integration(integration_name)
            if integration:
                status['integrations'][integration_name] = {
                    'type': integration.integration_type.value,
                    'enabled': integration.is_enabled(),
                    'authenticated': integration.is_authenticated()
                }
        
        return status
    
    def generate_mom_with_analytics(self, transcript: str, options: Dict[str, Any] = None) -> Dict[str, Any]:
        """
        Generate MoM with comprehensive analytics.
        
        Args:
            transcript (str): The meeting transcript text
            options (Dict[str, Any], optional): Generation options
            
        Returns:
            Dict[str, Any]: MoM data with analytics
            
        Raises:
            RuntimeError: If generation fails
        """
        try:
            # Set default options for analytics
            if options is None:
                options = {}
            
            # Ensure analytics are included
            options['include_analytics'] = True
            options['include_sentiment'] = options.get('include_sentiment', True)
            options['include_speakers'] = options.get('include_speakers', True)
            
            # Extract MoM data with analytics
            mom_data = self.mom_extractor.extract_with_options(transcript, options)
            
            # If analytics were generated, enhance the MoM data
            if 'analytics' in mom_data:
                # Use the analytics formatter to integrate analytics with MoM data
                from app.formatter.analytics_formatter import AnalyticsFormatter
                analytics_formatter = AnalyticsFormatter()
                mom_data = analytics_formatter.integrate_with_mom_data(mom_data, mom_data['analytics'])
            
            return mom_data
        
        except Exception as e:
            logger.error(f"Error generating MoM with analytics: {e}")
            raise RuntimeError(f"Failed to generate MoM with analytics: {e}")
    
    def get_meeting_analytics(self, transcript: str, speakers: Optional[List[str]] = None) -> Dict[str, Any]:
        """
        Get meeting analytics for a transcript.
        
        Args:
            transcript (str): The meeting transcript text
            speakers (List[str], optional): List of speaker names
            
        Returns:
            Dict[str, Any]: Meeting analytics
            
        Raises:
            RuntimeError: If analytics generation fails
        """
        try:
            from app.analyzer.meeting_analytics import MeetingAnalytics
            
            # Initialize analytics with configuration
            analytics_config = self.config.get('analytics', {})
            meeting_analytics = MeetingAnalytics(analytics_config)
            
            # Generate analytics
            analytics = meeting_analytics.analyze(transcript, speakers)
            
            return analytics
        
        except Exception as e:
            logger.error(f"Error generating meeting analytics: {e}")
            raise RuntimeError(f"Failed to generate meeting analytics: {e}")