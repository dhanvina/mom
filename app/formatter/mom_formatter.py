import json
from typing import Dict

class MoMFormatter:
    """
    Formats Minutes of Meeting (MoM) data into various output formats.
    """

    def format(self, mom_data: Dict, format_type: str = "text") -> str:
        """
        Format MoM data into the specified output format.

        Args:
            mom_data (Dict): Structured MoM data (from LLM).
            format_type (str): Output format: 'text', 'json', or 'html'.

        Returns:
            str: Formatted MoM as a string.
        """

        if format_type == 'json':
            return json.dumps(mom_data, indent=2)
        elif format_type == "html":
            return self._format_html(mom_data)
        else:
            return self._format_text(mom_data)
        
    def _format_text(self, mom_data: Dict) -> str:
        """Format MoM as plain text."""

        return f"""
            MINUTES OF MEETING

            Meeting Title: {mom_data.get('meeting_title', 'N/A')}
            Date & Time: {mom_data.get('date_time', 'N/A')}

            Attendees:
            {mom_data.get('attendees', 'N/A')}

            Agenda:
            {mom_data.get('agenda', 'N/A')}

            Key Discussion Points:
            {mom_data.get('discussion_points', 'N/A')}

            Action Items:
            {mom_data.get('action_items', 'N/A')}

            Decisions Made:
            {mom_data.get('decisions', 'N/A')}

            Next Steps:
            {mom_data.get('next_steps', 'N/A')}
                    """.strip()

    def _format_html(self, mom_data: Dict) -> str:
        """Format MoM as HTML."""
        
        return f"""
        <html>
        <head><title>Minutes of Meeting</title></head>
        <body>
        <h1>Minutes of Meeting</h1>
        <h2>Meeting Title: {mom_data.get('meeting_title', 'N/A')}</h2>
        <p><strong>Date & Time:</strong> {mom_data.get('date_time', 'N/A')}</p>
        <h3>Attendees:</h3>
        <p>{mom_data.get('attendees', 'N/A')}</p>
        <h3>Agenda:</h3>
        <p>{mom_data.get('agenda', 'N/A')}</p>
        <h3>Key Discussion Points:</h3>
        <p>{mom_data.get('discussion_points', 'N/A')}</p>
        <h3>Action Items:</h3>
        <p>{mom_data.get('action_items', 'N/A')}</p>
        <h3>Decisions Made:</h3>
        <p>{mom_data.get('decisions', 'N/A')}</p>
        <h3>Next Steps:</h3>
        <p>{mom_data.get('next_steps', 'N/A')}</p>
        </body>
        </html>
        """.strip()


