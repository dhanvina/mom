"""
Tests for external integrations functionality.
"""

import pytest
import json
from unittest.mock import Mock, patch, MagicMock
from app.integrations.base import (
    ExternalIntegrations, BaseIntegration, IntegrationConfig, 
    IntegrationResult, IntegrationType, AuthMethod
)
from app.integrations.task_management import TaskManagementIntegration, AsanaIntegration
from app.integrations.calendar import CalendarIntegration, GoogleCalendarIntegration
from app.integrations.email import EmailIntegration, SMTPIntegration


class TestExternalIntegrations:
    """Test the ExternalIntegrations manager."""
    
    def test_init(self):
        """Test initialization of ExternalIntegrations."""
        manager = ExternalIntegrations()
        assert manager.config == {}
        assert manager.integrations == {}
    
    def test_register_integration(self):
        """Test registering an integration."""
        manager = ExternalIntegrations()
        
        # Create a mock integration
        config = IntegrationConfig(
            name="test_integration",
            integration_type=IntegrationType.TASK_MANAGEMENT,
            auth_method=AuthMethod.API_KEY,
            credentials={"api_key": "test_key"},
            settings={}
        )
        integration = TaskManagementIntegration(config)
        
        manager.register_integration(integration)
        
        assert "test_integration" in manager.integrations
        assert manager.get_integration("test_integration") == integration
    
    def test_list_integrations(self):
        """Test listing integrations."""
        manager = ExternalIntegrations()
        
        # Initially empty
        assert manager.list_integrations() == []
        
        # Add an integration
        config = IntegrationConfig(
            name="test_integration",
            integration_type=IntegrationType.TASK_MANAGEMENT,
            auth_method=AuthMethod.API_KEY,
            credentials={"api_key": "test_key"},
            settings={}
        )
        integration = TaskManagementIntegration(config)
        manager.register_integration(integration)
        
        assert manager.list_integrations() == ["test_integration"]
    
    @patch('requests.Session.get')
    def test_test_integration(self, mock_get):
        """Test testing an integration."""
        manager = ExternalIntegrations()
        
        # Mock successful response
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.json.return_value = []
        mock_get.return_value = mock_response
        
        # Create and register integration
        config = IntegrationConfig(
            name="test_integration",
            integration_type=IntegrationType.TASK_MANAGEMENT,
            auth_method=AuthMethod.API_KEY,
            credentials={"api_key": "test_key"},
            settings={"base_url": "https://api.test.com"}
        )
        integration = TaskManagementIntegration(config)
        integration._authenticated = True  # Skip auth for test
        manager.register_integration(integration)
        
        result = manager.test_integration("test_integration")
        
        assert result.success is True
        assert "Connection test successful" in result.message


class TestTaskManagementIntegration:
    """Test TaskManagementIntegration."""
    
    def test_init(self):
        """Test initialization."""
        config = IntegrationConfig(
            name="test_task",
            integration_type=IntegrationType.TASK_MANAGEMENT,
            auth_method=AuthMethod.API_KEY,
            credentials={"api_key": "test_key"},
            settings={"base_url": "https://api.test.com"}
        )
        integration = TaskManagementIntegration(config)
        
        assert integration.name == "test_task"
        assert integration.base_url == "https://api.test.com"
        assert integration.session.headers["Authorization"] == "Bearer test_key"
    
    @patch('requests.Session.get')
    def test_authenticate(self, mock_get):
        """Test authentication."""
        config = IntegrationConfig(
            name="test_task",
            integration_type=IntegrationType.TASK_MANAGEMENT,
            auth_method=AuthMethod.API_KEY,
            credentials={"api_key": "test_key"},
            settings={"base_url": "https://api.test.com"}
        )
        integration = TaskManagementIntegration(config)
        
        # Mock successful response
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.json.return_value = {"id": "user123", "name": "Test User"}
        mock_get.return_value = mock_response
        
        result = integration.authenticate()
        
        assert result.success is True
        assert integration._authenticated is True
        assert "Authentication successful" in result.message
    
    @patch('requests.Session.post')
    def test_sync_action_items(self, mock_post):
        """Test syncing action items."""
        config = IntegrationConfig(
            name="test_task",
            integration_type=IntegrationType.TASK_MANAGEMENT,
            auth_method=AuthMethod.API_KEY,
            credentials={"api_key": "test_key"},
            settings={"base_url": "https://api.test.com"}
        )
        integration = TaskManagementIntegration(config)
        integration._authenticated = True  # Skip auth for test
        
        # Mock successful task creation
        mock_response = Mock()
        mock_response.status_code = 201
        mock_response.json.return_value = {"id": "task123", "name": "Test Task"}
        mock_post.return_value = mock_response
        
        action_items = [
            {
                "description": "Complete project documentation",
                "assignee": "john@example.com",
                "deadline": "2024-01-15T10:00:00"
            }
        ]
        
        result = integration.sync_action_items(action_items)
        
        assert result.success is True
        assert len(result.data["created_tasks"]) == 1
        assert len(result.data["failed_tasks"]) == 0


class TestCalendarIntegration:
    """Test CalendarIntegration."""
    
    def test_init(self):
        """Test initialization."""
        config = IntegrationConfig(
            name="test_calendar",
            integration_type=IntegrationType.CALENDAR,
            auth_method=AuthMethod.OAUTH2,
            credentials={"access_token": "test_token"},
            settings={"base_url": "https://api.calendar.com"}
        )
        integration = CalendarIntegration(config)
        
        assert integration.name == "test_calendar"
        assert integration.base_url == "https://api.calendar.com"
        assert integration.session.headers["Authorization"] == "Bearer test_token"
    
    @patch('requests.Session.post')
    def test_create_event(self, mock_post):
        """Test creating a calendar event."""
        config = IntegrationConfig(
            name="test_calendar",
            integration_type=IntegrationType.CALENDAR,
            auth_method=AuthMethod.OAUTH2,
            credentials={"access_token": "test_token"},
            settings={"base_url": "https://api.calendar.com"}
        )
        integration = CalendarIntegration(config)
        integration._authenticated = True  # Skip auth for test
        
        # Mock successful event creation
        mock_response = Mock()
        mock_response.status_code = 201
        mock_response.json.return_value = {"id": "event123", "summary": "Test Event"}
        mock_post.return_value = mock_response
        
        event_data = {
            "title": "Test Meeting",
            "description": "Test meeting description",
            "start_time": "2024-01-15T10:00:00",
            "end_time": "2024-01-15T11:00:00",
            "attendees": ["john@example.com", "jane@example.com"]
        }
        
        result = integration.create_event(event_data)
        
        assert result.success is True
        assert "Event 'Test Meeting' created successfully" in result.message


class TestEmailIntegration:
    """Test EmailIntegration."""
    
    def test_init(self):
        """Test initialization."""
        config = IntegrationConfig(
            name="test_email",
            integration_type=IntegrationType.EMAIL,
            auth_method=AuthMethod.BASIC_AUTH,
            credentials={"username": "test@example.com", "password": "password"},
            settings={
                "smtp_server": "smtp.test.com",
                "smtp_port": 587,
                "sender_email": "test@example.com"
            }
        )
        integration = EmailIntegration(config)
        
        assert integration.name == "test_email"
        assert integration.smtp_server == "smtp.test.com"
        assert integration.smtp_port == 587
        assert integration.sender_email == "test@example.com"
    
    def test_convert_email_data(self):
        """Test converting email data."""
        config = IntegrationConfig(
            name="test_email",
            integration_type=IntegrationType.EMAIL,
            auth_method=AuthMethod.BASIC_AUTH,
            credentials={"username": "test@example.com", "password": "password"},
            settings={"sender_email": "test@example.com"}
        )
        integration = EmailIntegration(config)
        
        email_data = {
            "to": "recipient@example.com",
            "subject": "Test Subject",
            "body": "Test body content",
            "cc": "cc@example.com",
            "attachments": "/path/to/file.pdf"
        }
        
        email_message = integration._convert_email_data(email_data)
        
        assert email_message.to == ["recipient@example.com"]
        assert email_message.subject == "Test Subject"
        assert email_message.body == "Test body content"
        assert email_message.cc == ["cc@example.com"]
        assert email_message.attachments == ["/path/to/file.pdf"]
    
    def test_format_mom_for_email(self):
        """Test formatting MoM data for email."""
        config = IntegrationConfig(
            name="test_email",
            integration_type=IntegrationType.EMAIL,
            auth_method=AuthMethod.BASIC_AUTH,
            credentials={"username": "test@example.com", "password": "password"},
            settings={"sender_email": "test@example.com"}
        )
        integration = EmailIntegration(config)
        
        mom_data = {
            "meeting_title": "Weekly Team Meeting",
            "date_time": "2024-01-15 10:00:00",
            "attendees": [
                {"name": "John Doe", "role": "Developer"},
                {"name": "Jane Smith", "role": "Manager"}
            ],
            "action_items": [
                {
                    "description": "Complete project documentation",
                    "assignee": "John Doe",
                    "deadline": "2024-01-20"
                }
            ]
        }
        
        formatted_text = integration._format_mom_for_email(mom_data)
        
        assert "Weekly Team Meeting" in formatted_text
        assert "John Doe (Developer)" in formatted_text
        assert "Complete project documentation" in formatted_text
        assert "Assigned to: John Doe" in formatted_text


if __name__ == "__main__":
    pytest.main([__file__])