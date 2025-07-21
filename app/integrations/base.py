"""
Base class for external integrations.

This module provides the foundation for integrating with external services
like task management tools, calendar services, and email systems.
"""

import logging
from abc import ABC, abstractmethod
from typing import Dict, Any, Optional, List
from dataclasses import dataclass
from enum import Enum

logger = logging.getLogger(__name__)


class IntegrationType(Enum):
    """Types of external integrations."""
    TASK_MANAGEMENT = "task_management"
    CALENDAR = "calendar"
    EMAIL = "email"


class AuthMethod(Enum):
    """Authentication methods for integrations."""
    API_KEY = "api_key"
    OAUTH2 = "oauth2"
    BASIC_AUTH = "basic_auth"
    TOKEN = "token"


@dataclass
class IntegrationConfig:
    """Configuration for an external integration."""
    name: str
    integration_type: IntegrationType
    auth_method: AuthMethod
    credentials: Dict[str, Any]
    settings: Dict[str, Any]
    enabled: bool = True


@dataclass
class IntegrationResult:
    """Result of an integration operation."""
    success: bool
    message: str
    data: Optional[Dict[str, Any]] = None
    error: Optional[str] = None


class ExternalIntegrations:
    """
    Base class for managing external integrations.
    
    This class provides the foundation for integrating with external services
    and manages authentication, configuration, and error handling.
    """
    
    def __init__(self, config: Optional[Dict[str, Any]] = None):
        """
        Initialize the external integrations manager.
        
        Args:
            config: Configuration dictionary for integrations
        """
        self.config = config or {}
        self.integrations: Dict[str, 'BaseIntegration'] = {}
        self._setup_logging()
    
    def _setup_logging(self):
        """Set up logging for integrations."""
        self.logger = logging.getLogger(f"{__name__}.{self.__class__.__name__}")
    
    def register_integration(self, integration: 'BaseIntegration'):
        """
        Register an integration with the manager.
        
        Args:
            integration: The integration instance to register
        """
        self.integrations[integration.name] = integration
        self.logger.info(f"Registered integration: {integration.name}")
    
    def get_integration(self, name: str) -> Optional['BaseIntegration']:
        """
        Get a registered integration by name.
        
        Args:
            name: Name of the integration
            
        Returns:
            The integration instance or None if not found
        """
        return self.integrations.get(name)
    
    def list_integrations(self) -> List[str]:
        """
        List all registered integration names.
        
        Returns:
            List of integration names
        """
        return list(self.integrations.keys())
    
    def test_integration(self, name: str) -> IntegrationResult:
        """
        Test an integration connection.
        
        Args:
            name: Name of the integration to test
            
        Returns:
            Result of the test operation
        """
        integration = self.get_integration(name)
        if not integration:
            return IntegrationResult(
                success=False,
                message=f"Integration '{name}' not found",
                error="Integration not registered"
            )
        
        try:
            return integration.test_connection()
        except Exception as e:
            self.logger.error(f"Error testing integration '{name}': {e}")
            return IntegrationResult(
                success=False,
                message=f"Failed to test integration '{name}'",
                error=str(e)
            )
    
    def sync_action_items(self, action_items: List[Dict[str, Any]], 
                         integration_name: str) -> IntegrationResult:
        """
        Sync action items with a task management integration.
        
        Args:
            action_items: List of action items to sync
            integration_name: Name of the task management integration
            
        Returns:
            Result of the sync operation
        """
        integration = self.get_integration(integration_name)
        if not integration:
            return IntegrationResult(
                success=False,
                message=f"Integration '{integration_name}' not found",
                error="Integration not registered"
            )
        
        if integration.integration_type != IntegrationType.TASK_MANAGEMENT:
            return IntegrationResult(
                success=False,
                message=f"Integration '{integration_name}' is not a task management integration",
                error="Invalid integration type"
            )
        
        try:
            return integration.sync_action_items(action_items)
        except Exception as e:
            self.logger.error(f"Error syncing action items with '{integration_name}': {e}")
            return IntegrationResult(
                success=False,
                message=f"Failed to sync action items",
                error=str(e)
            )
    
    def create_calendar_event(self, event_data: Dict[str, Any], 
                            integration_name: str) -> IntegrationResult:
        """
        Create a calendar event using a calendar integration.
        
        Args:
            event_data: Event data to create
            integration_name: Name of the calendar integration
            
        Returns:
            Result of the creation operation
        """
        integration = self.get_integration(integration_name)
        if not integration:
            return IntegrationResult(
                success=False,
                message=f"Integration '{integration_name}' not found",
                error="Integration not registered"
            )
        
        if integration.integration_type != IntegrationType.CALENDAR:
            return IntegrationResult(
                success=False,
                message=f"Integration '{integration_name}' is not a calendar integration",
                error="Invalid integration type"
            )
        
        try:
            return integration.create_event(event_data)
        except Exception as e:
            self.logger.error(f"Error creating calendar event with '{integration_name}': {e}")
            return IntegrationResult(
                success=False,
                message=f"Failed to create calendar event",
                error=str(e)
            )
    
    def send_email(self, email_data: Dict[str, Any], 
                   integration_name: str) -> IntegrationResult:
        """
        Send an email using an email integration.
        
        Args:
            email_data: Email data to send
            integration_name: Name of the email integration
            
        Returns:
            Result of the send operation
        """
        integration = self.get_integration(integration_name)
        if not integration:
            return IntegrationResult(
                success=False,
                message=f"Integration '{integration_name}' not found",
                error="Integration not registered"
            )
        
        if integration.integration_type != IntegrationType.EMAIL:
            return IntegrationResult(
                success=False,
                message=f"Integration '{integration_name}' is not an email integration",
                error="Invalid integration type"
            )
        
        try:
            return integration.send_email(email_data)
        except Exception as e:
            self.logger.error(f"Error sending email with '{integration_name}': {e}")
            return IntegrationResult(
                success=False,
                message=f"Failed to send email",
                error=str(e)
            )


class BaseIntegration(ABC):
    """
    Abstract base class for individual integrations.
    
    All specific integrations should inherit from this class and implement
    the required abstract methods.
    """
    
    def __init__(self, config: IntegrationConfig):
        """
        Initialize the integration.
        
        Args:
            config: Configuration for this integration
        """
        self.config = config
        self.name = config.name
        self.integration_type = config.integration_type
        self.auth_method = config.auth_method
        self.credentials = config.credentials
        self.settings = config.settings
        self.enabled = config.enabled
        self._setup_logging()
        self._authenticated = False
    
    def _setup_logging(self):
        """Set up logging for this integration."""
        self.logger = logging.getLogger(f"{__name__}.{self.__class__.__name__}")
    
    @abstractmethod
    def authenticate(self) -> IntegrationResult:
        """
        Authenticate with the external service.
        
        Returns:
            Result of the authentication operation
        """
        pass
    
    @abstractmethod
    def test_connection(self) -> IntegrationResult:
        """
        Test the connection to the external service.
        
        Returns:
            Result of the connection test
        """
        pass
    
    def is_authenticated(self) -> bool:
        """
        Check if the integration is authenticated.
        
        Returns:
            True if authenticated, False otherwise
        """
        return self._authenticated
    
    def is_enabled(self) -> bool:
        """
        Check if the integration is enabled.
        
        Returns:
            True if enabled, False otherwise
        """
        return self.enabled
    
    def enable(self):
        """Enable the integration."""
        self.enabled = True
        self.logger.info(f"Integration '{self.name}' enabled")
    
    def disable(self):
        """Disable the integration."""
        self.enabled = False
        self.logger.info(f"Integration '{self.name}' disabled")
    
    def _ensure_authenticated(self) -> IntegrationResult:
        """
        Ensure the integration is authenticated before performing operations.
        
        Returns:
            Result of authentication check/attempt
        """
        if not self.enabled:
            return IntegrationResult(
                success=False,
                message=f"Integration '{self.name}' is disabled",
                error="Integration disabled"
            )
        
        if not self._authenticated:
            auth_result = self.authenticate()
            if not auth_result.success:
                return auth_result
        
        return IntegrationResult(success=True, message="Authentication verified")