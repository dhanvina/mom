"""
Calendar Integration for MoM Generator.

This module provides integrations with calendar services like Google Calendar,
Outlook, and other calendar systems.
"""

import logging
import requests
from typing import Dict, Any, List, Optional
from datetime import datetime, timedelta
from dataclasses import dataclass
from .base import BaseIntegration, IntegrationConfig, IntegrationResult, IntegrationType, AuthMethod

logger = logging.getLogger(__name__)


@dataclass
class CalendarEvent:
    """Represents a calendar event."""
    title: str
    description: str
    start_time: datetime
    end_time: datetime
    location: Optional[str] = None
    attendees: List[str] = None
    reminders: List[int] = None  # Minutes before event
    all_day: bool = False
    
    def __post_init__(self):
        if self.attendees is None:
            self.attendees = []
        if self.reminders is None:
            self.reminders = [15]  # Default 15 minutes reminder


@dataclass
class Reminder:
    """Represents a reminder for a calendar event."""
    method: str  # 'email', 'popup', 'sms'
    minutes: int  # Minutes before event


class CalendarIntegration(BaseIntegration):
    """
    Base class for calendar integrations.
    
    Provides common functionality for integrating with calendar services
    like Google Calendar, Outlook, etc.
    """
    
    def __init__(self, config: IntegrationConfig):
        """
        Initialize the calendar integration.
        
        Args:
            config: Configuration for this integration
        """
        super().__init__(config)
        self.base_url = self.settings.get('base_url', '')
        self.default_calendar = self.settings.get('default_calendar', 'primary')
        self.session = requests.Session()
        self._setup_session()
    
    def _setup_session(self):
        """Set up the HTTP session with authentication headers."""
        if self.auth_method == AuthMethod.OAUTH2:
            access_token = self.credentials.get('access_token')
            if access_token:
                self.session.headers.update({
                    'Authorization': f'Bearer {access_token}',
                    'Content-Type': 'application/json'
                })
        elif self.auth_method == AuthMethod.API_KEY:
            api_key = self.credentials.get('api_key')
            if api_key:
                self.session.headers.update({
                    'Authorization': f'Bearer {api_key}',
                    'Content-Type': 'application/json'
                })
    
    def authenticate(self) -> IntegrationResult:
        """
        Authenticate with the calendar service.
        
        Returns:
            Result of the authentication operation
        """
        try:
            # Test authentication by fetching calendar list
            response = self.session.get(f"{self.base_url}/calendars")
            
            if response.status_code == 200:
                self._authenticated = True
                calendars = response.json()
                return IntegrationResult(
                    success=True,
                    message="Authentication successful",
                    data={"calendars": calendars}
                )
            else:
                return IntegrationResult(
                    success=False,
                    message="Authentication failed",
                    error=f"HTTP {response.status_code}: {response.text}"
                )
        
        except Exception as e:
            self.logger.error(f"Authentication error: {e}")
            return IntegrationResult(
                success=False,
                message="Authentication failed",
                error=str(e)
            )
    
    def test_connection(self) -> IntegrationResult:
        """
        Test the connection to the calendar service.
        
        Returns:
            Result of the connection test
        """
        auth_result = self._ensure_authenticated()
        if not auth_result.success:
            return auth_result
        
        try:
            # Test connection by fetching calendar information
            response = self.session.get(f"{self.base_url}/calendars/{self.default_calendar}")
            
            if response.status_code == 200:
                calendar_info = response.json()
                return IntegrationResult(
                    success=True,
                    message="Connection test successful",
                    data={"calendar": calendar_info}
                )
            else:
                return IntegrationResult(
                    success=False,
                    message="Connection test failed",
                    error=f"HTTP {response.status_code}: {response.text}"
                )
        
        except Exception as e:
            self.logger.error(f"Connection test error: {e}")
            return IntegrationResult(
                success=False,
                message="Connection test failed",
                error=str(e)
            )
    
    def create_event(self, event_data: Dict[str, Any]) -> IntegrationResult:
        """
        Create a calendar event.
        
        Args:
            event_data: Event data dictionary
            
        Returns:
            Result of the event creation
        """
        auth_result = self._ensure_authenticated()
        if not auth_result.success:
            return auth_result
        
        try:
            event = self._convert_event_data(event_data)
            result = self._create_calendar_event(event)
            return result
        
        except Exception as e:
            self.logger.error(f"Error creating calendar event: {e}")
            return IntegrationResult(
                success=False,
                message="Failed to create calendar event",
                error=str(e)
            )
    
    def _convert_event_data(self, event_data: Dict[str, Any]) -> CalendarEvent:
        """
        Convert event data dictionary to CalendarEvent object.
        
        Args:
            event_data: Event data dictionary
            
        Returns:
            CalendarEvent object
        """
        # Parse start and end times
        start_time = event_data.get('start_time')
        if isinstance(start_time, str):
            start_time = datetime.fromisoformat(start_time)
        elif not isinstance(start_time, datetime):
            # Default to next hour if not provided
            start_time = datetime.now().replace(minute=0, second=0, microsecond=0) + timedelta(hours=1)
        
        end_time = event_data.get('end_time')
        if isinstance(end_time, str):
            end_time = datetime.fromisoformat(end_time)
        elif not isinstance(end_time, datetime):
            # Default to 1 hour after start time
            end_time = start_time + timedelta(hours=1)
        
        # Parse attendees
        attendees = event_data.get('attendees', [])
        if isinstance(attendees, str):
            attendees = [email.strip() for email in attendees.split(',')]
        
        # Parse reminders
        reminders = event_data.get('reminders', [15])
        if isinstance(reminders, int):
            reminders = [reminders]
        
        return CalendarEvent(
            title=event_data.get('title', 'Meeting'),
            description=event_data.get('description', ''),
            start_time=start_time,
            end_time=end_time,
            location=event_data.get('location'),
            attendees=attendees,
            reminders=reminders,
            all_day=event_data.get('all_day', False)
        )
    
    def _create_calendar_event(self, event: CalendarEvent) -> IntegrationResult:
        """
        Create an event in the calendar service.
        
        Args:
            event: CalendarEvent to create
            
        Returns:
            Result of the event creation
        """
        try:
            event_data = {
                'summary': event.title,
                'description': event.description,
                'location': event.location,
                'start': {
                    'dateTime': event.start_time.isoformat(),
                    'timeZone': 'UTC'
                },
                'end': {
                    'dateTime': event.end_time.isoformat(),
                    'timeZone': 'UTC'
                },
                'attendees': [{'email': email} for email in event.attendees],
                'reminders': {
                    'useDefault': False,
                    'overrides': [
                        {'method': 'email', 'minutes': minutes}
                        for minutes in event.reminders
                    ]
                }
            }
            
            # Handle all-day events
            if event.all_day:
                event_data['start'] = {'date': event.start_time.strftime('%Y-%m-%d')}
                event_data['end'] = {'date': event.end_time.strftime('%Y-%m-%d')}
            
            # Remove None values
            event_data = {k: v for k, v in event_data.items() if v is not None}
            
            response = self.session.post(
                f"{self.base_url}/calendars/{self.default_calendar}/events",
                json=event_data
            )
            
            if response.status_code in [200, 201]:
                event_info = response.json()
                return IntegrationResult(
                    success=True,
                    message=f"Event '{event.title}' created successfully",
                    data=event_info
                )
            else:
                return IntegrationResult(
                    success=False,
                    message=f"Failed to create event '{event.title}'",
                    error=f"HTTP {response.status_code}: {response.text}"
                )
        
        except Exception as e:
            self.logger.error(f"Error creating calendar event '{event.title}': {e}")
            return IntegrationResult(
                success=False,
                message=f"Failed to create event '{event.title}'",
                error=str(e)
            )
    
    def update_event(self, event_id: str, event_data: Dict[str, Any]) -> IntegrationResult:
        """
        Update an existing calendar event.
        
        Args:
            event_id: ID of the event to update
            event_data: Updated event data
            
        Returns:
            Result of the event update
        """
        auth_result = self._ensure_authenticated()
        if not auth_result.success:
            return auth_result
        
        try:
            event = self._convert_event_data(event_data)
            
            update_data = {
                'summary': event.title,
                'description': event.description,
                'location': event.location,
                'start': {
                    'dateTime': event.start_time.isoformat(),
                    'timeZone': 'UTC'
                },
                'end': {
                    'dateTime': event.end_time.isoformat(),
                    'timeZone': 'UTC'
                }
            }
            
            # Remove None values
            update_data = {k: v for k, v in update_data.items() if v is not None}
            
            response = self.session.put(
                f"{self.base_url}/calendars/{self.default_calendar}/events/{event_id}",
                json=update_data
            )
            
            if response.status_code == 200:
                event_info = response.json()
                return IntegrationResult(
                    success=True,
                    message=f"Event updated successfully",
                    data=event_info
                )
            else:
                return IntegrationResult(
                    success=False,
                    message="Failed to update event",
                    error=f"HTTP {response.status_code}: {response.text}"
                )
        
        except Exception as e:
            self.logger.error(f"Error updating calendar event: {e}")
            return IntegrationResult(
                success=False,
                message="Failed to update event",
                error=str(e)
            )
    
    def delete_event(self, event_id: str) -> IntegrationResult:
        """
        Delete a calendar event.
        
        Args:
            event_id: ID of the event to delete
            
        Returns:
            Result of the event deletion
        """
        auth_result = self._ensure_authenticated()
        if not auth_result.success:
            return auth_result
        
        try:
            response = self.session.delete(
                f"{self.base_url}/calendars/{self.default_calendar}/events/{event_id}"
            )
            
            if response.status_code in [200, 204]:
                return IntegrationResult(
                    success=True,
                    message="Event deleted successfully"
                )
            else:
                return IntegrationResult(
                    success=False,
                    message="Failed to delete event",
                    error=f"HTTP {response.status_code}: {response.text}"
                )
        
        except Exception as e:
            self.logger.error(f"Error deleting calendar event: {e}")
            return IntegrationResult(
                success=False,
                message="Failed to delete event",
                error=str(e)
            )
    
    def get_events(self, start_date: datetime, end_date: datetime) -> IntegrationResult:
        """
        Get events within a date range.
        
        Args:
            start_date: Start date for event search
            end_date: End date for event search
            
        Returns:
            Result containing list of events
        """
        auth_result = self._ensure_authenticated()
        if not auth_result.success:
            return auth_result
        
        try:
            params = {
                'timeMin': start_date.isoformat(),
                'timeMax': end_date.isoformat(),
                'singleEvents': True,
                'orderBy': 'startTime'
            }
            
            response = self.session.get(
                f"{self.base_url}/calendars/{self.default_calendar}/events",
                params=params
            )
            
            if response.status_code == 200:
                events_data = response.json()
                return IntegrationResult(
                    success=True,
                    message="Events retrieved successfully",
                    data=events_data
                )
            else:
                return IntegrationResult(
                    success=False,
                    message="Failed to retrieve events",
                    error=f"HTTP {response.status_code}: {response.text}"
                )
        
        except Exception as e:
            self.logger.error(f"Error retrieving calendar events: {e}")
            return IntegrationResult(
                success=False,
                message="Failed to retrieve events",
                error=str(e)
            )


class GoogleCalendarIntegration(CalendarIntegration):
    """Specific integration for Google Calendar."""
    
    def __init__(self, config: IntegrationConfig):
        """Initialize Google Calendar integration."""
        if not config.settings.get('base_url'):
            config.settings['base_url'] = 'https://www.googleapis.com/calendar/v3'
        super().__init__(config)


class OutlookCalendarIntegration(CalendarIntegration):
    """Specific integration for Outlook Calendar."""
    
    def __init__(self, config: IntegrationConfig):
        """Initialize Outlook Calendar integration."""
        if not config.settings.get('base_url'):
            config.settings['base_url'] = 'https://graph.microsoft.com/v1.0/me'
        super().__init__(config)
    
    def _create_calendar_event(self, event: CalendarEvent) -> IntegrationResult:
        """Create an event in Outlook Calendar."""
        try:
            event_data = {
                'subject': event.title,
                'body': {
                    'contentType': 'HTML',
                    'content': event.description
                },
                'start': {
                    'dateTime': event.start_time.isoformat(),
                    'timeZone': 'UTC'
                },
                'end': {
                    'dateTime': event.end_time.isoformat(),
                    'timeZone': 'UTC'
                },
                'location': {
                    'displayName': event.location
                } if event.location else None,
                'attendees': [
                    {
                        'emailAddress': {
                            'address': email,
                            'name': email
                        }
                    }
                    for email in event.attendees
                ],
                'reminderMinutesBeforeStart': event.reminders[0] if event.reminders else 15
            }
            
            # Remove None values
            event_data = {k: v for k, v in event_data.items() if v is not None}
            
            response = self.session.post(f"{self.base_url}/events", json=event_data)
            
            if response.status_code in [200, 201]:
                event_info = response.json()
                return IntegrationResult(
                    success=True,
                    message=f"Event '{event.title}' created successfully",
                    data=event_info
                )
            else:
                return IntegrationResult(
                    success=False,
                    message=f"Failed to create event '{event.title}'",
                    error=f"HTTP {response.status_code}: {response.text}"
                )
        
        except Exception as e:
            self.logger.error(f"Error creating Outlook event '{event.title}': {e}")
            return IntegrationResult(
                success=False,
                message=f"Failed to create event '{event.title}'",
                error=str(e)
            )