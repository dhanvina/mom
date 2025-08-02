# External Integrations

This module provides external integrations for the MoM Generator, allowing it to connect with various third-party services for enhanced functionality.

## Supported Integrations

### Task Management
- **Asana**: Sync action items as tasks
- **Trello**: Create cards for action items
- **Jira**: Create issues for action items
- **Generic**: Works with any REST API-based task management system

### Calendar Services
- **Google Calendar**: Create events and reminders
- **Outlook Calendar**: Create events via Microsoft Graph API
- **Generic**: Works with any calendar service with REST API

### Email Services
- **SMTP**: Send emails via any SMTP server
- **Gmail**: Send emails via Gmail API
- **Outlook**: Send emails via Microsoft Graph API

## Configuration

Integrations are configured via JSON configuration files. See `config/integrations_example.json` for a complete example.

### Basic Structure

```json
{
  "integrations": {
    "task_management": {
      "integration_name": {
        "type": "asana|trello|jira|generic",
        "auth_method": "api_key|oauth2|basic_auth|token",
        "credentials": {
          "api_key": "your_api_key",
          "username": "your_username",
          "password": "your_password"
        },
        "settings": {
          "base_url": "https://api.service.com",
          "default_project": "project_id"
        },
        "enabled": true
      }
    },
    "calendar": {
      "integration_name": {
        "type": "google|outlook|generic",
        "auth_method": "oauth2|api_key",
        "credentials": {
          "access_token": "your_access_token",
          "refresh_token": "your_refresh_token"
        },
        "settings": {
          "base_url": "https://api.calendar.com",
          "default_calendar": "primary"
        },
        "enabled": true
      }
    },
    "email": {
      "integration_name": {
        "type": "smtp|gmail|outlook",
        "auth_method": "basic_auth|oauth2",
        "credentials": {
          "username": "your_email@example.com",
          "password": "your_password"
        },
        "settings": {
          "smtp_server": "smtp.gmail.com",
          "smtp_port": 587,
          "use_tls": true,
          "sender_email": "your_email@example.com",
          "sender_name": "Meeting Minutes Bot"
        },
        "enabled": true
      }
    }
  }
}
```

## Usage

### Basic Usage

```python
from app.main import MoMGenerator
import json

# Load configuration
with open('config/integrations.json', 'r') as f:
    config = json.load(f)

# Initialize generator with integrations
generator = MoMGenerator(config=config)

# Generate MoM with integrations
options = {
    'format_type': 'text',
    'sync_tasks': True,
    'task_integration': 'asana',
    'send_email': True,
    'email_integration': 'smtp_email',
    'email_recipients': ['team@example.com']
}

result = generator.generate_mom_with_integrations(transcript, options)
```

### Testing Integrations

```python
# Test all configured integrations
test_results = generator.test_integrations()

for name, result in test_results.items():
    if result['success']:
        print(f"✓ {name}: {result['message']}")
    else:
        print(f"✗ {name}: {result['error']}")
```

### Manual Integration Operations

```python
# Sync action items manually
action_items = [
    {
        "description": "Complete project documentation",
        "assignee": "john@example.com",
        "deadline": "2024-01-20T10:00:00"
    }
]

result = generator.sync_action_items(action_items, 'asana')

# Create calendar event manually
event_data = {
    "title": "Follow-up Meeting",
    "description": "Discuss project progress",
    "start_time": "2024-01-20T14:00:00",
    "end_time": "2024-01-20T15:00:00",
    "attendees": ["team@example.com"]
}

result = generator.integrations.create_calendar_event(event_data, 'google_calendar')

# Send email manually
email_data = {
    "to": ["team@example.com"],
    "subject": "Meeting Minutes",
    "body": "Please find the meeting minutes attached."
}

result = generator.integrations.send_email(email_data, 'smtp_email')
```

## Authentication

### API Key Authentication
Most task management tools use API key authentication:

```json
{
  "auth_method": "api_key",
  "credentials": {
    "api_key": "your_api_key_here"
  }
}
```

### OAuth2 Authentication
Calendar and email services typically use OAuth2:

```json
{
  "auth_method": "oauth2",
  "credentials": {
    "access_token": "your_access_token",
    "refresh_token": "your_refresh_token",
    "client_id": "your_client_id",
    "client_secret": "your_client_secret"
  }
}
```

### Basic Authentication
SMTP and some APIs use username/password:

```json
{
  "auth_method": "basic_auth",
  "credentials": {
    "username": "your_username",
    "password": "your_password"
  }
}
```

## Error Handling

All integration operations return a standardized result format:

```python
{
    "success": True/False,
    "message": "Human-readable message",
    "data": {...},  # Optional result data
    "error": "Error details if failed"
}
```

## Extending Integrations

To add a new integration:

1. Create a new class inheriting from the appropriate base class
2. Implement required abstract methods
3. Add configuration support in the main app
4. Add tests for the new integration

Example:

```python
from integrations.base import BaseIntegration
from integrations.task_management import TaskManagementIntegration

class CustomTaskIntegration(TaskManagementIntegration):
    def __init__(self, config):
        super().__init__(config)
        # Custom initialization
    
    def _create_task(self, task):
        # Custom task creation logic
        pass
```

## Security Considerations

- Store credentials securely (use environment variables or secure vaults)
- Use HTTPS for all API communications
- Implement proper token refresh for OAuth2
- Validate all input data before sending to external services
- Log security events appropriately

## Troubleshooting

### Common Issues

1. **Authentication Failures**
   - Verify credentials are correct
   - Check if tokens have expired
   - Ensure proper permissions are granted

2. **Network Errors**
   - Check internet connectivity
   - Verify API endpoints are accessible
   - Check for firewall restrictions

3. **Rate Limiting**
   - Implement retry logic with exponential backoff
   - Monitor API usage limits
   - Consider caching responses where appropriate

### Debug Mode

Enable debug logging to troubleshoot issues:

```python
import logging
logging.basicConfig(level=logging.DEBUG)
```

This will show detailed information about API requests and responses.