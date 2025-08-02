"""
Email Integration for MoM Generator.

This module provides integrations with email services for sending
meeting minutes and notifications.
"""

import logging
import smtplib
import ssl
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from email.mime.base import MIMEBase
from email import encoders
from typing import Dict, Any, List, Optional
from dataclasses import dataclass
from pathlib import Path
from .base import BaseIntegration, IntegrationConfig, IntegrationResult, IntegrationType, AuthMethod

logger = logging.getLogger(__name__)


@dataclass
class EmailMessage:
    """Represents an email message."""
    to: List[str]
    subject: str
    body: str
    cc: List[str] = None
    bcc: List[str] = None
    attachments: List[str] = None
    html_body: Optional[str] = None
    reply_to: Optional[str] = None
    
    def __post_init__(self):
        if self.cc is None:
            self.cc = []
        if self.bcc is None:
            self.bcc = []
        if self.attachments is None:
            self.attachments = []


@dataclass
class EmailTemplate:
    """Represents an email template."""
    name: str
    subject_template: str
    body_template: str
    html_template: Optional[str] = None
    variables: List[str] = None
    
    def __post_init__(self):
        if self.variables is None:
            self.variables = []


class EmailIntegration(BaseIntegration):
    """
    Base class for email integrations.
    
    Provides functionality for sending emails through various email services
    including SMTP, Gmail API, Outlook API, etc.
    """
    
    def __init__(self, config: IntegrationConfig):
        """
        Initialize the email integration.
        
        Args:
            config: Configuration for this integration
        """
        super().__init__(config)
        self.smtp_server = self.settings.get('smtp_server', 'localhost')
        self.smtp_port = self.settings.get('smtp_port', 587)
        self.use_tls = self.settings.get('use_tls', True)
        self.sender_email = self.settings.get('sender_email', '')
        self.sender_name = self.settings.get('sender_name', '')
        self.templates = {}
        self._load_templates()
    
    def _load_templates(self):
        """Load email templates from configuration."""
        template_configs = self.settings.get('templates', {})
        for name, template_config in template_configs.items():
            template = EmailTemplate(
                name=name,
                subject_template=template_config.get('subject', ''),
                body_template=template_config.get('body', ''),
                html_template=template_config.get('html'),
                variables=template_config.get('variables', [])
            )
            self.templates[name] = template
    
    def authenticate(self) -> IntegrationResult:
        """
        Authenticate with the email service.
        
        Returns:
            Result of the authentication operation
        """
        try:
            # Test SMTP connection
            context = ssl.create_default_context()
            
            with smtplib.SMTP(self.smtp_server, self.smtp_port) as server:
                if self.use_tls:
                    server.starttls(context=context)
                
                if self.auth_method == AuthMethod.BASIC_AUTH:
                    username = self.credentials.get('username')
                    password = self.credentials.get('password')
                    if username and password:
                        server.login(username, password)
                
                self._authenticated = True
                return IntegrationResult(
                    success=True,
                    message="Email authentication successful"
                )
        
        except Exception as e:
            self.logger.error(f"Email authentication error: {e}")
            return IntegrationResult(
                success=False,
                message="Email authentication failed",
                error=str(e)
            )
    
    def test_connection(self) -> IntegrationResult:
        """
        Test the connection to the email service.
        
        Returns:
            Result of the connection test
        """
        auth_result = self._ensure_authenticated()
        if not auth_result.success:
            return auth_result
        
        try:
            # Test by connecting to SMTP server
            context = ssl.create_default_context()
            
            with smtplib.SMTP(self.smtp_server, self.smtp_port) as server:
                if self.use_tls:
                    server.starttls(context=context)
                
                return IntegrationResult(
                    success=True,
                    message="Email connection test successful",
                    data={"smtp_server": self.smtp_server, "port": self.smtp_port}
                )
        
        except Exception as e:
            self.logger.error(f"Email connection test error: {e}")
            return IntegrationResult(
                success=False,
                message="Email connection test failed",
                error=str(e)
            )
    
    def send_email(self, email_data: Dict[str, Any]) -> IntegrationResult:
        """
        Send an email.
        
        Args:
            email_data: Email data dictionary
            
        Returns:
            Result of the email sending operation
        """
        auth_result = self._ensure_authenticated()
        if not auth_result.success:
            return auth_result
        
        try:
            email_message = self._convert_email_data(email_data)
            result = self._send_email_message(email_message)
            return result
        
        except Exception as e:
            self.logger.error(f"Error sending email: {e}")
            return IntegrationResult(
                success=False,
                message="Failed to send email",
                error=str(e)
            )
    
    def _convert_email_data(self, email_data: Dict[str, Any]) -> EmailMessage:
        """
        Convert email data dictionary to EmailMessage object.
        
        Args:
            email_data: Email data dictionary
            
        Returns:
            EmailMessage object
        """
        # Parse recipients
        to_emails = email_data.get('to', [])
        if isinstance(to_emails, str):
            to_emails = [email.strip() for email in to_emails.split(',')]
        
        cc_emails = email_data.get('cc', [])
        if isinstance(cc_emails, str):
            cc_emails = [email.strip() for email in cc_emails.split(',')]
        
        bcc_emails = email_data.get('bcc', [])
        if isinstance(bcc_emails, str):
            bcc_emails = [email.strip() for email in bcc_emails.split(',')]
        
        # Parse attachments
        attachments = email_data.get('attachments', [])
        if isinstance(attachments, str):
            attachments = [attachments]
        
        return EmailMessage(
            to=to_emails,
            subject=email_data.get('subject', 'Meeting Minutes'),
            body=email_data.get('body', ''),
            cc=cc_emails,
            bcc=bcc_emails,
            attachments=attachments,
            html_body=email_data.get('html_body'),
            reply_to=email_data.get('reply_to')
        )
    
    def _send_email_message(self, email_message: EmailMessage) -> IntegrationResult:
        """
        Send an email message using SMTP.
        
        Args:
            email_message: EmailMessage to send
            
        Returns:
            Result of the email sending operation
        """
        try:
            # Create message
            msg = MIMEMultipart('alternative')
            msg['From'] = f"{self.sender_name} <{self.sender_email}>" if self.sender_name else self.sender_email
            msg['To'] = ', '.join(email_message.to)
            msg['Subject'] = email_message.subject
            
            if email_message.cc:
                msg['Cc'] = ', '.join(email_message.cc)
            
            if email_message.reply_to:
                msg['Reply-To'] = email_message.reply_to
            
            # Add body
            if email_message.body:
                text_part = MIMEText(email_message.body, 'plain')
                msg.attach(text_part)
            
            if email_message.html_body:
                html_part = MIMEText(email_message.html_body, 'html')
                msg.attach(html_part)
            
            # Add attachments
            for attachment_path in email_message.attachments:
                if Path(attachment_path).exists():
                    with open(attachment_path, 'rb') as attachment:
                        part = MIMEBase('application', 'octet-stream')
                        part.set_payload(attachment.read())
                    
                    encoders.encode_base64(part)
                    part.add_header(
                        'Content-Disposition',
                        f'attachment; filename= {Path(attachment_path).name}'
                    )
                    msg.attach(part)
            
            # Send email
            context = ssl.create_default_context()
            all_recipients = email_message.to + email_message.cc + email_message.bcc
            
            with smtplib.SMTP(self.smtp_server, self.smtp_port) as server:
                if self.use_tls:
                    server.starttls(context=context)
                
                if self.auth_method == AuthMethod.BASIC_AUTH:
                    username = self.credentials.get('username')
                    password = self.credentials.get('password')
                    if username and password:
                        server.login(username, password)
                
                server.send_message(msg, to_addrs=all_recipients)
            
            return IntegrationResult(
                success=True,
                message=f"Email sent successfully to {len(all_recipients)} recipients",
                data={
                    'recipients': all_recipients,
                    'subject': email_message.subject
                }
            )
        
        except Exception as e:
            self.logger.error(f"Error sending email message: {e}")
            return IntegrationResult(
                success=False,
                message="Failed to send email message",
                error=str(e)
            )
    
    def send_mom_email(self, mom_data: Dict[str, Any], recipients: List[str], 
                       template_name: str = 'default') -> IntegrationResult:
        """
        Send meeting minutes via email using a template.
        
        Args:
            mom_data: Meeting minutes data
            recipients: List of email recipients
            template_name: Name of the email template to use
            
        Returns:
            Result of the email sending operation
        """
        try:
            template = self.templates.get(template_name)
            if not template:
                # Use default template
                template = EmailTemplate(
                    name='default',
                    subject_template='Meeting Minutes - {meeting_title}',
                    body_template='{mom_content}',
                    variables=['meeting_title', 'mom_content']
                )
            
            # Prepare template variables
            template_vars = {
                'meeting_title': mom_data.get('meeting_title', 'Meeting'),
                'meeting_date': mom_data.get('date_time', ''),
                'attendees': ', '.join([att.get('name', '') for att in mom_data.get('attendees', [])]),
                'mom_content': self._format_mom_for_email(mom_data)
            }
            
            # Format subject and body
            subject = template.subject_template.format(**template_vars)
            body = template.body_template.format(**template_vars)
            html_body = None
            
            if template.html_template:
                html_body = template.html_template.format(**template_vars)
            
            # Create email data
            email_data = {
                'to': recipients,
                'subject': subject,
                'body': body,
                'html_body': html_body
            }
            
            return self.send_email(email_data)
        
        except Exception as e:
            self.logger.error(f"Error sending MoM email: {e}")
            return IntegrationResult(
                success=False,
                message="Failed to send MoM email",
                error=str(e)
            )
    
    def _format_mom_for_email(self, mom_data: Dict[str, Any]) -> str:
        """
        Format meeting minutes data for email body.
        
        Args:
            mom_data: Meeting minutes data
            
        Returns:
            Formatted text for email body
        """
        lines = []
        
        # Meeting info
        if mom_data.get('meeting_title'):
            lines.append(f"Meeting: {mom_data['meeting_title']}")
        if mom_data.get('date_time'):
            lines.append(f"Date: {mom_data['date_time']}")
        if mom_data.get('location'):
            lines.append(f"Location: {mom_data['location']}")
        
        lines.append("")  # Empty line
        
        # Attendees
        if mom_data.get('attendees'):
            lines.append("Attendees:")
            for attendee in mom_data['attendees']:
                name = attendee.get('name', '')
                role = attendee.get('role', '')
                if role:
                    lines.append(f"  - {name} ({role})")
                else:
                    lines.append(f"  - {name}")
            lines.append("")
        
        # Agenda
        if mom_data.get('agenda'):
            lines.append("Agenda:")
            for i, item in enumerate(mom_data['agenda'], 1):
                lines.append(f"  {i}. {item}")
            lines.append("")
        
        # Discussion Points
        if mom_data.get('discussion_points'):
            lines.append("Discussion Points:")
            for point in mom_data['discussion_points']:
                lines.append(f"  - {point}")
            lines.append("")
        
        # Action Items
        if mom_data.get('action_items'):
            lines.append("Action Items:")
            for item in mom_data['action_items']:
                assignee = item.get('assignee', 'Unassigned')
                deadline = item.get('deadline', '')
                description = item.get('description', '')
                
                line = f"  - {description}"
                if assignee != 'Unassigned':
                    line += f" (Assigned to: {assignee})"
                if deadline:
                    line += f" (Due: {deadline})"
                lines.append(line)
            lines.append("")
        
        # Decisions
        if mom_data.get('decisions'):
            lines.append("Decisions:")
            for decision in mom_data['decisions']:
                lines.append(f"  - {decision}")
            lines.append("")
        
        # Next Steps
        if mom_data.get('next_steps'):
            lines.append("Next Steps:")
            for step in mom_data['next_steps']:
                lines.append(f"  - {step}")
        
        return '\n'.join(lines)
    
    def add_template(self, template: EmailTemplate):
        """
        Add an email template.
        
        Args:
            template: EmailTemplate to add
        """
        self.templates[template.name] = template
        self.logger.info(f"Added email template: {template.name}")
    
    def get_template(self, name: str) -> Optional[EmailTemplate]:
        """
        Get an email template by name.
        
        Args:
            name: Name of the template
            
        Returns:
            EmailTemplate or None if not found
        """
        return self.templates.get(name)
    
    def list_templates(self) -> List[str]:
        """
        List all available email template names.
        
        Returns:
            List of template names
        """
        return list(self.templates.keys())


class GmailIntegration(EmailIntegration):
    """Specific integration for Gmail using Gmail API."""
    
    def __init__(self, config: IntegrationConfig):
        """Initialize Gmail integration."""
        super().__init__(config)
        # Gmail API specific settings would go here
        # This would typically use Google's API client libraries
    
    def authenticate(self) -> IntegrationResult:
        """Authenticate with Gmail API."""
        # This would implement OAuth2 flow for Gmail API
        # For now, fall back to SMTP
        return super().authenticate()


class OutlookEmailIntegration(EmailIntegration):
    """Specific integration for Outlook using Microsoft Graph API."""
    
    def __init__(self, config: IntegrationConfig):
        """Initialize Outlook email integration."""
        super().__init__(config)
        # Outlook API specific settings would go here
        # This would typically use Microsoft Graph API
    
    def authenticate(self) -> IntegrationResult:
        """Authenticate with Microsoft Graph API."""
        # This would implement OAuth2 flow for Microsoft Graph
        # For now, fall back to SMTP
        return super().authenticate()


class SMTPIntegration(EmailIntegration):
    """Generic SMTP integration for any email provider."""
    
    def __init__(self, config: IntegrationConfig):
        """Initialize SMTP integration."""
        super().__init__(config)
        # SMTP is the default implementation in the base class