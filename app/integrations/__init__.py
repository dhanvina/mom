"""
External integrations module for MoM Generator.

This module provides integrations with external services like task management tools,
calendar services, and email systems.
"""

from .base import ExternalIntegrations
from .task_management import TaskManagementIntegration
from .calendar import CalendarIntegration
from .email import EmailIntegration

__all__ = [
    'ExternalIntegrations',
    'TaskManagementIntegration', 
    'CalendarIntegration',
    'EmailIntegration'
]