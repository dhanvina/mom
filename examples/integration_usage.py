"""
Example usage of external integrations with MoM Generator.

This example demonstrates how to use the external integrations
to sync action items, create calendar events, and send emails.
"""

import json
from pathlib import Path
from app.main import MoMGenerator


def load_config():
    """Load integration configuration from file."""
    config_path = Path(__file__).parent.parent / "config" / "integrations_example.json"
    
    if config_path.exists():
        with open(config_path, 'r') as f:
            return json.load(f)
    else:
        # Return minimal config for demonstration
        return {
            "integrations": {
                "email": {
                    "smtp_email": {
                        "type": "smtp",
                        "auth_method": "basic_auth",
                        "credentials": {
                            "username": "your_email@example.com",
                            "password": "your_password"
                        },
                        "settings": {
                            "smtp_server": "smtp.gmail.com",
                            "smtp_port": 587,
                            "use_tls": True,
                            "sender_email": "your_email@example.com",
                            "sender_name": "Meeting Minutes Bot"
                        },
                        "enabled": False  # Disabled for demo
                    }
                }
            }
        }


def main():
    """Demonstrate integration usage."""
    print("MoM Generator - External Integrations Demo")
    print("=" * 50)
    
    # Load configuration
    config = load_config()
    
    # Initialize MoM Generator with integrations
    mom_generator = MoMGenerator(config=config)
    
    # Check setup
    setup_success, setup_message = mom_generator.setup()
    if not setup_success:
        print(f"Setup failed: {setup_message}")
        return
    
    print(f"Setup successful: {setup_message}")
    
    # Get integration status
    print("\nIntegration Status:")
    status = mom_generator.get_integration_status()
    print(f"Total integrations: {status['total_integrations']}")
    
    for name, info in status['integrations'].items():
        print(f"  - {name}: {info['type']} (enabled: {info['enabled']}, authenticated: {info['authenticated']})")
    
    # Test integrations
    print("\nTesting Integrations:")
    test_results = mom_generator.test_integrations()
    
    for name, result in test_results.items():
        status_text = "✓ PASS" if result['success'] else "✗ FAIL"
        print(f"  - {name}: {status_text} - {result['message']}")
        if result.get('error'):
            print(f"    Error: {result['error']}")
    
    # Sample transcript for demonstration
    sample_transcript = """
    Meeting: Weekly Team Standup
    Date: January 15, 2024
    Attendees: John Doe (Developer), Jane Smith (Manager), Bob Wilson (Designer)
    
    John: Good morning everyone. Let me start with my updates.
    I completed the user authentication module last week.
    This week I'll be working on the dashboard implementation.
    I need help from Bob on the UI design for the dashboard.
    
    Jane: Thanks John. Bob, can you help John with the dashboard design by Wednesday?
    
    Bob: Absolutely. I'll have the mockups ready by Tuesday and we can review them together.
    
    Jane: Perfect. Let's also schedule a follow-up meeting for Friday to review the progress.
    We need to make sure we're on track for the January 30th deadline.
    
    John: Sounds good. I'll send out a calendar invite for Friday.
    
    Jane: Great. Any other items? No? Alright, meeting adjourned.
    """
    
    print(f"\nGenerating MoM from sample transcript...")
    
    # Generate MoM with integration options
    options = {
        'format_type': 'text',
        'structured_output': False,
        'sync_tasks': False,  # Disabled for demo
        'task_integration': 'asana',
        'create_calendar_events': False,  # Disabled for demo
        'calendar_integration': 'google_calendar',
        'send_email': False,  # Disabled for demo
        'email_integration': 'smtp_email',
        'email_recipients': ['team@example.com']
    }
    
    try:
        result = mom_generator.generate_mom_with_integrations(sample_transcript, options)
        
        print("\nGenerated MoM:")
        print("-" * 30)
        print(result['mom_output'])
        
        print("\nIntegration Results:")
        for integration_type, integration_result in result['integration_results'].items():
            print(f"  - {integration_type}: {integration_result}")
    
    except Exception as e:
        print(f"Error generating MoM: {e}")
    
    print("\nDemo completed!")


if __name__ == "__main__":
    main()