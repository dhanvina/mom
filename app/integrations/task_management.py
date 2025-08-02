"""
Task Management Integration for MoM Generator.

This module provides integrations with popular task management tools
like Trello, Asana, Jira, and others.
"""

import logging
import requests
from typing import Dict, Any, List, Optional
from datetime import datetime, timedelta
from dataclasses import dataclass
from .base import BaseIntegration, IntegrationConfig, IntegrationResult, IntegrationType, AuthMethod

logger = logging.getLogger(__name__)


@dataclass
class TaskItem:
    """Represents a task item for task management systems."""
    title: str
    description: str
    assignee: Optional[str] = None
    due_date: Optional[datetime] = None
    priority: str = "medium"  # low, medium, high
    labels: List[str] = None
    project_id: Optional[str] = None
    
    def __post_init__(self):
        if self.labels is None:
            self.labels = []


class TaskManagementIntegration(BaseIntegration):
    """
    Base class for task management integrations.
    
    Provides common functionality for integrating with task management tools
    like Trello, Asana, Jira, etc.
    """
    
    def __init__(self, config: IntegrationConfig):
        """
        Initialize the task management integration.
        
        Args:
            config: Configuration for this integration
        """
        super().__init__(config)
        self.base_url = self.settings.get('base_url', '')
        self.default_project = self.settings.get('default_project')
        self.session = requests.Session()
        self._setup_session()
    
    def _setup_session(self):
        """Set up the HTTP session with authentication headers."""
        if self.auth_method == AuthMethod.API_KEY:
            api_key = self.credentials.get('api_key')
            if api_key:
                self.session.headers.update({
                    'Authorization': f'Bearer {api_key}',
                    'Content-Type': 'application/json'
                })
        elif self.auth_method == AuthMethod.TOKEN:
            token = self.credentials.get('token')
            if token:
                self.session.headers.update({
                    'Authorization': f'Token {token}',
                    'Content-Type': 'application/json'
                })
    
    def authenticate(self) -> IntegrationResult:
        """
        Authenticate with the task management service.
        
        Returns:
            Result of the authentication operation
        """
        try:
            # Test authentication by making a simple API call
            response = self.session.get(f"{self.base_url}/user")
            
            if response.status_code == 200:
                self._authenticated = True
                user_info = response.json()
                return IntegrationResult(
                    success=True,
                    message="Authentication successful",
                    data={"user": user_info}
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
        Test the connection to the task management service.
        
        Returns:
            Result of the connection test
        """
        auth_result = self._ensure_authenticated()
        if not auth_result.success:
            return auth_result
        
        try:
            # Test connection by fetching user projects
            response = self.session.get(f"{self.base_url}/projects")
            
            if response.status_code == 200:
                projects = response.json()
                return IntegrationResult(
                    success=True,
                    message="Connection test successful",
                    data={"projects_count": len(projects)}
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
    
    def sync_action_items(self, action_items: List[Dict[str, Any]]) -> IntegrationResult:
        """
        Sync action items with the task management system.
        
        Args:
            action_items: List of action items from MoM
            
        Returns:
            Result of the sync operation
        """
        auth_result = self._ensure_authenticated()
        if not auth_result.success:
            return auth_result
        
        try:
            created_tasks = []
            failed_tasks = []
            
            for item in action_items:
                task = self._convert_action_item_to_task(item)
                result = self._create_task(task)
                
                if result.success:
                    created_tasks.append({
                        'title': task.title,
                        'task_id': result.data.get('id') if result.data else None
                    })
                else:
                    failed_tasks.append({
                        'title': task.title,
                        'error': result.error
                    })
            
            success = len(failed_tasks) == 0
            message = f"Created {len(created_tasks)} tasks"
            if failed_tasks:
                message += f", failed to create {len(failed_tasks)} tasks"
            
            return IntegrationResult(
                success=success,
                message=message,
                data={
                    'created_tasks': created_tasks,
                    'failed_tasks': failed_tasks
                }
            )
        
        except Exception as e:
            self.logger.error(f"Error syncing action items: {e}")
            return IntegrationResult(
                success=False,
                message="Failed to sync action items",
                error=str(e)
            )
    
    def _convert_action_item_to_task(self, action_item: Dict[str, Any]) -> TaskItem:
        """
        Convert an action item from MoM to a TaskItem.
        
        Args:
            action_item: Action item dictionary
            
        Returns:
            TaskItem object
        """
        # Parse due date if provided
        due_date = None
        if action_item.get('deadline'):
            try:
                if isinstance(action_item['deadline'], str):
                    due_date = datetime.fromisoformat(action_item['deadline'])
                elif isinstance(action_item['deadline'], datetime):
                    due_date = action_item['deadline']
            except (ValueError, TypeError):
                self.logger.warning(f"Invalid deadline format: {action_item.get('deadline')}")
        
        # Determine priority based on keywords
        priority = "medium"
        description = action_item.get('description', '').lower()
        if any(word in description for word in ['urgent', 'asap', 'critical']):
            priority = "high"
        elif any(word in description for word in ['low', 'minor', 'optional']):
            priority = "low"
        
        return TaskItem(
            title=action_item.get('description', 'Action Item'),
            description=action_item.get('context', ''),
            assignee=action_item.get('assignee'),
            due_date=due_date,
            priority=priority,
            labels=['meeting-action-item'],
            project_id=self.default_project
        )
    
    def _create_task(self, task: TaskItem) -> IntegrationResult:
        """
        Create a task in the task management system.
        
        Args:
            task: TaskItem to create
            
        Returns:
            Result of the task creation
        """
        try:
            task_data = {
                'name': task.title,
                'notes': task.description,
                'assignee': task.assignee,
                'due_on': task.due_date.isoformat() if task.due_date else None,
                'projects': [task.project_id] if task.project_id else [],
                'tags': task.labels
            }
            
            # Remove None values
            task_data = {k: v for k, v in task_data.items() if v is not None}
            
            response = self.session.post(f"{self.base_url}/tasks", json=task_data)
            
            if response.status_code in [200, 201]:
                task_info = response.json()
                return IntegrationResult(
                    success=True,
                    message=f"Task '{task.title}' created successfully",
                    data=task_info
                )
            else:
                return IntegrationResult(
                    success=False,
                    message=f"Failed to create task '{task.title}'",
                    error=f"HTTP {response.status_code}: {response.text}"
                )
        
        except Exception as e:
            self.logger.error(f"Error creating task '{task.title}': {e}")
            return IntegrationResult(
                success=False,
                message=f"Failed to create task '{task.title}'",
                error=str(e)
            )
    
    def update_task_status(self, task_id: str, status: str) -> IntegrationResult:
        """
        Update the status of a task.
        
        Args:
            task_id: ID of the task to update
            status: New status for the task
            
        Returns:
            Result of the status update
        """
        auth_result = self._ensure_authenticated()
        if not auth_result.success:
            return auth_result
        
        try:
            update_data = {'completed': status.lower() in ['completed', 'done', 'finished']}
            
            response = self.session.put(f"{self.base_url}/tasks/{task_id}", json=update_data)
            
            if response.status_code == 200:
                return IntegrationResult(
                    success=True,
                    message=f"Task status updated to '{status}'",
                    data=response.json()
                )
            else:
                return IntegrationResult(
                    success=False,
                    message="Failed to update task status",
                    error=f"HTTP {response.status_code}: {response.text}"
                )
        
        except Exception as e:
            self.logger.error(f"Error updating task status: {e}")
            return IntegrationResult(
                success=False,
                message="Failed to update task status",
                error=str(e)
            )
    
    def get_task_status(self, task_id: str) -> IntegrationResult:
        """
        Get the current status of a task.
        
        Args:
            task_id: ID of the task
            
        Returns:
            Result containing task status information
        """
        auth_result = self._ensure_authenticated()
        if not auth_result.success:
            return auth_result
        
        try:
            response = self.session.get(f"{self.base_url}/tasks/{task_id}")
            
            if response.status_code == 200:
                task_info = response.json()
                return IntegrationResult(
                    success=True,
                    message="Task status retrieved successfully",
                    data=task_info
                )
            else:
                return IntegrationResult(
                    success=False,
                    message="Failed to get task status",
                    error=f"HTTP {response.status_code}: {response.text}"
                )
        
        except Exception as e:
            self.logger.error(f"Error getting task status: {e}")
            return IntegrationResult(
                success=False,
                message="Failed to get task status",
                error=str(e)
            )


class AsanaIntegration(TaskManagementIntegration):
    """Specific integration for Asana task management."""
    
    def __init__(self, config: IntegrationConfig):
        """Initialize Asana integration."""
        if not config.settings.get('base_url'):
            config.settings['base_url'] = 'https://app.asana.com/api/1.0'
        super().__init__(config)


class TrelloIntegration(TaskManagementIntegration):
    """Specific integration for Trello task management."""
    
    def __init__(self, config: IntegrationConfig):
        """Initialize Trello integration."""
        if not config.settings.get('base_url'):
            config.settings['base_url'] = 'https://api.trello.com/1'
        super().__init__(config)
    
    def _setup_session(self):
        """Set up Trello-specific authentication."""
        api_key = self.credentials.get('api_key')
        token = self.credentials.get('token')
        
        if api_key and token:
            self.session.params.update({
                'key': api_key,
                'token': token
            })
    
    def _create_task(self, task: TaskItem) -> IntegrationResult:
        """Create a card in Trello."""
        try:
            card_data = {
                'name': task.title,
                'desc': task.description,
                'idList': task.project_id or self.default_project,
                'due': task.due_date.isoformat() if task.due_date else None
            }
            
            # Remove None values
            card_data = {k: v for k, v in card_data.items() if v is not None}
            
            response = self.session.post(f"{self.base_url}/cards", json=card_data)
            
            if response.status_code == 200:
                card_info = response.json()
                return IntegrationResult(
                    success=True,
                    message=f"Card '{task.title}' created successfully",
                    data=card_info
                )
            else:
                return IntegrationResult(
                    success=False,
                    message=f"Failed to create card '{task.title}'",
                    error=f"HTTP {response.status_code}: {response.text}"
                )
        
        except Exception as e:
            self.logger.error(f"Error creating Trello card '{task.title}': {e}")
            return IntegrationResult(
                success=False,
                message=f"Failed to create card '{task.title}'",
                error=str(e)
            )


class JiraIntegration(TaskManagementIntegration):
    """Specific integration for Jira task management."""
    
    def __init__(self, config: IntegrationConfig):
        """Initialize Jira integration."""
        super().__init__(config)
    
    def _setup_session(self):
        """Set up Jira-specific authentication."""
        if self.auth_method == AuthMethod.BASIC_AUTH:
            username = self.credentials.get('username')
            password = self.credentials.get('password')
            if username and password:
                self.session.auth = (username, password)
        else:
            super()._setup_session()
    
    def _create_task(self, task: TaskItem) -> IntegrationResult:
        """Create an issue in Jira."""
        try:
            issue_data = {
                'fields': {
                    'project': {'key': task.project_id or self.default_project},
                    'summary': task.title,
                    'description': task.description,
                    'issuetype': {'name': 'Task'},
                    'priority': {'name': task.priority.capitalize()}
                }
            }
            
            if task.assignee:
                issue_data['fields']['assignee'] = {'name': task.assignee}
            
            if task.due_date:
                issue_data['fields']['duedate'] = task.due_date.strftime('%Y-%m-%d')
            
            response = self.session.post(f"{self.base_url}/issue", json=issue_data)
            
            if response.status_code == 201:
                issue_info = response.json()
                return IntegrationResult(
                    success=True,
                    message=f"Issue '{task.title}' created successfully",
                    data=issue_info
                )
            else:
                return IntegrationResult(
                    success=False,
                    message=f"Failed to create issue '{task.title}'",
                    error=f"HTTP {response.status_code}: {response.text}"
                )
        
        except Exception as e:
            self.logger.error(f"Error creating Jira issue '{task.title}': {e}")
            return IntegrationResult(
                success=False,
                message=f"Failed to create issue '{task.title}'",
                error=str(e)
            )