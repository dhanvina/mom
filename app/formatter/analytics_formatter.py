"""
Analytics formatter module for AI-powered MoM generator.

This module provides functionality for formatting meeting analytics for inclusion in MoM output.
"""

import logging
from typing import Dict, Any, Optional, List, Union

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class AnalyticsFormatter:
    """
    Formats meeting analytics for inclusion in MoM output.
    
    This class provides methods for formatting meeting analytics in various output formats.
    
    Attributes:
        config (Dict): Configuration options for the formatter
    """
    
    def __init__(self, config: Optional[Dict[str, Any]] = None):
        """
        Initialize the AnalyticsFormatter with optional configuration.
        
        Args:
            config (Dict, optional): Configuration options for the formatter
        """
        self.config = config or {}
        logger.info("AnalyticsFormatter initialized")
    
    def format_analytics(self, analytics: Dict[str, Any], format_type: str = "text") -> str:
        """
        Format meeting analytics in the specified format.
        
        Args:
            analytics (Dict[str, Any]): Meeting analytics
            format_type (str, optional): Output format type. Defaults to "text".
            
        Returns:
            str: Formatted analytics
        """
        if format_type == "text":
            return self._format_text(analytics)
        elif format_type == "html":
            return self._format_html(analytics)
        elif format_type == "markdown":
            return self._format_markdown(analytics)
        else:
            logger.warning(f"Unsupported format type: {format_type}. Using text format.")
            return self._format_text(analytics)
    
    def _format_text(self, analytics: Dict[str, Any]) -> str:
        """
        Format meeting analytics as plain text.
        
        Args:
            analytics (Dict[str, Any]): Meeting analytics
            
        Returns:
            str: Text-formatted analytics
        """
        lines = []
        
        # Add header
        lines.append("MEETING ANALYTICS")
        lines.append("=" * 20)
        lines.append("")
        
        # Add speaking time distribution
        lines.append("SPEAKING TIME DISTRIBUTION")
        lines.append("-" * 20)
        
        speaking_time = analytics.get("speaking_time", {})
        for speaker, percentage in speaking_time.items():
            if speaker != "Unknown":
                lines.append(f"{speaker}: {percentage:.1f}%")
        lines.append("")
        
        # Add topics
        lines.append("MAIN TOPICS DISCUSSED")
        lines.append("-" * 20)
        
        topics = analytics.get("topics", [])
        for topic in topics[:5]:  # Top 5 topics
            lines.append(f"{topic['topic']}: {topic.get('relevance', 0):.1f}%")
        lines.append("")
        
        # Add efficiency metrics
        lines.append("MEETING EFFICIENCY")
        lines.append("-" * 20)
        
        efficiency_metrics = analytics.get("efficiency_metrics", {})
        
        if "efficiency_score" in efficiency_metrics:
            lines.append(f"Overall Efficiency Score: {efficiency_metrics['efficiency_score']:.1f}/100")
        
        if "participation_balance" in efficiency_metrics:
            lines.append(f"Participation Balance: {efficiency_metrics['participation_balance']:.1f}/100")
        
        if "engagement_score" in efficiency_metrics:
            lines.append(f"Engagement Score: {efficiency_metrics['engagement_score']:.1f}/100")
        
        if "content_density" in efficiency_metrics:
            lines.append(f"Content Density: {efficiency_metrics['content_density']:.1f}%")
        
        if "time_efficiency" in efficiency_metrics:
            lines.append(f"Time Efficiency: {efficiency_metrics['time_efficiency']:.1f}%")
        lines.append("")
        
        # Add improvement suggestions
        lines.append("SUGGESTIONS FOR IMPROVEMENT")
        lines.append("-" * 20)
        
        suggestions = analytics.get("suggestions", [])
        for i, suggestion in enumerate(suggestions[:5], 1):  # Top 5 suggestions
            lines.append(f"{i}. {suggestion['suggestion']}")
        
        return "\n".join(lines)
    
    def _format_html(self, analytics: Dict[str, Any]) -> str:
        """
        Format meeting analytics as HTML.
        
        Args:
            analytics (Dict[str, Any]): Meeting analytics
            
        Returns:
            str: HTML-formatted analytics
        """
        html = []
        
        # Add header
        html.append("<div class='analytics-section'>")
        html.append("<h2>Meeting Analytics</h2>")
        
        # Add speaking time distribution
        html.append("<div class='analytics-subsection'>")
        html.append("<h3>Speaking Time Distribution</h3>")
        html.append("<div class='chart-container'>")
        
        speaking_time = analytics.get("speaking_time", {})
        html.append("<div class='bar-chart'>")
        for speaker, percentage in speaking_time.items():
            if speaker != "Unknown":
                html.append(f"<div class='bar-item'>")
                html.append(f"<div class='bar-label'>{speaker}</div>")
                html.append(f"<div class='bar' style='width: {percentage}%;'></div>")
                html.append(f"<div class='bar-value'>{percentage:.1f}%</div>")
                html.append("</div>")
        html.append("</div>")
        html.append("</div>")
        html.append("</div>")
        
        # Add topics
        html.append("<div class='analytics-subsection'>")
        html.append("<h3>Main Topics Discussed</h3>")
        html.append("<ul class='topic-list'>")
        
        topics = analytics.get("topics", [])
        for topic in topics[:5]:  # Top 5 topics
            html.append(f"<li><strong>{topic['topic']}</strong>: {topic.get('relevance', 0):.1f}%</li>")
        html.append("</ul>")
        html.append("</div>")
        
        # Add efficiency metrics
        html.append("<div class='analytics-subsection'>")
        html.append("<h3>Meeting Efficiency</h3>")
        html.append("<div class='metrics-grid'>")
        
        efficiency_metrics = analytics.get("efficiency_metrics", {})
        
        if "efficiency_score" in efficiency_metrics:
            html.append("<div class='metric'>")
            html.append("<div class='metric-label'>Overall Efficiency</div>")
            html.append(f"<div class='metric-value'>{efficiency_metrics['efficiency_score']:.1f}/100</div>")
            html.append("</div>")
        
        if "participation_balance" in efficiency_metrics:
            html.append("<div class='metric'>")
            html.append("<div class='metric-label'>Participation Balance</div>")
            html.append(f"<div class='metric-value'>{efficiency_metrics['participation_balance']:.1f}/100</div>")
            html.append("</div>")
        
        if "engagement_score" in efficiency_metrics:
            html.append("<div class='metric'>")
            html.append("<div class='metric-label'>Engagement</div>")
            html.append(f"<div class='metric-value'>{efficiency_metrics['engagement_score']:.1f}/100</div>")
            html.append("</div>")
        
        if "content_density" in efficiency_metrics:
            html.append("<div class='metric'>")
            html.append("<div class='metric-label'>Content Density</div>")
            html.append(f"<div class='metric-value'>{efficiency_metrics['content_density']:.1f}%</div>")
            html.append("</div>")
        
        if "time_efficiency" in efficiency_metrics:
            html.append("<div class='metric'>")
            html.append("<div class='metric-label'>Time Efficiency</div>")
            html.append(f"<div class='metric-value'>{efficiency_metrics['time_efficiency']:.1f}%</div>")
            html.append("</div>")
        
        html.append("</div>")
        html.append("</div>")
        
        # Add improvement suggestions
        html.append("<div class='analytics-subsection'>")
        html.append("<h3>Suggestions for Improvement</h3>")
        html.append("<ol class='suggestions-list'>")
        
        suggestions = analytics.get("suggestions", [])
        for suggestion in suggestions[:5]:  # Top 5 suggestions
            html.append(f"<li>")
            html.append(f"<div class='suggestion'>{suggestion['suggestion']}</div>")
            html.append(f"<div class='suggestion-reason'>{suggestion.get('reason', '')}</div>")
            html.append("</li>")
        
        html.append("</ol>")
        html.append("</div>")
        
        html.append("</div>")
        
        # Add CSS styles
        html.append("<style>")
        html.append("""
            .analytics-section {
                margin-top: 30px;
                padding: 20px;
                background-color: #f9f9f9;
                border-radius: 5px;
            }
            .analytics-subsection {
                margin-bottom: 20px;
            }
            .bar-chart {
                width: 100%;
            }
            .bar-item {
                display: flex;
                align-items: center;
                margin-bottom: 5px;
            }
            .bar-label {
                width: 150px;
                text-align: right;
                padding-right: 10px;
            }
            .bar {
                height: 20px;
                background-color: #3498db;
                border-radius: 3px;
            }
            .bar-value {
                padding-left: 10px;
                width: 50px;
            }
            .metrics-grid {
                display: grid;
                grid-template-columns: repeat(auto-fill, minmax(200px, 1fr));
                gap: 15px;
            }
            .metric {
                background-color: #fff;
                padding: 10px;
                border-radius: 5px;
                box-shadow: 0 1px 3px rgba(0,0,0,0.1);
            }
            .metric-label {
                font-weight: bold;
                margin-bottom: 5px;
            }
            .metric-value {
                font-size: 1.2em;
                color: #2c3e50;
            }
            .suggestions-list li {
                margin-bottom: 10px;
            }
            .suggestion {
                font-weight: bold;
            }
            .suggestion-reason {
                font-style: italic;
                color: #666;
                margin-top: 3px;
            }
        """)
        html.append("</style>")
        
        return "\n".join(html)
    
    def _format_markdown(self, analytics: Dict[str, Any]) -> str:
        """
        Format meeting analytics as Markdown.
        
        Args:
            analytics (Dict[str, Any]): Meeting analytics
            
        Returns:
            str: Markdown-formatted analytics
        """
        md = []
        
        # Add header
        md.append("## Meeting Analytics")
        md.append("")
        
        # Add speaking time distribution
        md.append("### Speaking Time Distribution")
        md.append("")
        
        speaking_time = analytics.get("speaking_time", {})
        for speaker, percentage in speaking_time.items():
            if speaker != "Unknown":
                md.append(f"- **{speaker}**: {percentage:.1f}%")
        md.append("")
        
        # Add topics
        md.append("### Main Topics Discussed")
        md.append("")
        
        topics = analytics.get("topics", [])
        for topic in topics[:5]:  # Top 5 topics
            md.append(f"- **{topic['topic']}**: {topic.get('relevance', 0):.1f}%")
        md.append("")
        
        # Add efficiency metrics
        md.append("### Meeting Efficiency")
        md.append("")
        
        efficiency_metrics = analytics.get("efficiency_metrics", {})
        
        if "efficiency_score" in efficiency_metrics:
            md.append(f"- **Overall Efficiency Score**: {efficiency_metrics['efficiency_score']:.1f}/100")
        
        if "participation_balance" in efficiency_metrics:
            md.append(f"- **Participation Balance**: {efficiency_metrics['participation_balance']:.1f}/100")
        
        if "engagement_score" in efficiency_metrics:
            md.append(f"- **Engagement Score**: {efficiency_metrics['engagement_score']:.1f}/100")
        
        if "content_density" in efficiency_metrics:
            md.append(f"- **Content Density**: {efficiency_metrics['content_density']:.1f}%")
        
        if "time_efficiency" in efficiency_metrics:
            md.append(f"- **Time Efficiency**: {efficiency_metrics['time_efficiency']:.1f}%")
        md.append("")
        
        # Add improvement suggestions
        md.append("### Suggestions for Improvement")
        md.append("")
        
        suggestions = analytics.get("suggestions", [])
        for i, suggestion in enumerate(suggestions[:5], 1):  # Top 5 suggestions
            md.append(f"{i}. **{suggestion['suggestion']}**")
            if "reason" in suggestion:
                md.append(f"   - *{suggestion['reason']}*")
        
        return "\n".join(md)
    
    def create_visualization_data(self, analytics: Dict[str, Any]) -> Dict[str, Any]:
        """
        Create data for visualizations.
        
        Args:
            analytics (Dict[str, Any]): Meeting analytics
            
        Returns:
            Dict[str, Any]: Visualization data
        """
        visualization_data = {}
        
        # Speaking time distribution data
        speaking_time = analytics.get("speaking_time", {})
        visualization_data["speaking_time"] = {
            "labels": [speaker for speaker in speaking_time.keys() if speaker != "Unknown"],
            "values": [percentage for speaker, percentage in speaking_time.items() if speaker != "Unknown"]
        }
        
        # Topic distribution data
        topics = analytics.get("topics", [])
        visualization_data["topics"] = {
            "labels": [topic["topic"] for topic in topics[:5]],
            "values": [topic.get("relevance", 0) for topic in topics[:5]]
        }
        
        # Efficiency metrics data
        efficiency_metrics = analytics.get("efficiency_metrics", {})
        visualization_data["efficiency"] = {
            "labels": ["Overall", "Participation", "Engagement", "Content", "Time"],
            "values": [
                efficiency_metrics.get("efficiency_score", 0),
                efficiency_metrics.get("participation_balance", 0),
                efficiency_metrics.get("engagement_score", 0),
                efficiency_metrics.get("content_density", 0),
                efficiency_metrics.get("time_efficiency", 0)
            ]
        }
        
        return visualization_data
    
    def format_analytics_summary(self, analytics: Dict[str, Any]) -> Dict[str, Any]:
        """
        Create a summary of analytics for inclusion in MoM.
        
        Args:
            analytics (Dict[str, Any]): Meeting analytics
            
        Returns:
            Dict[str, Any]: Analytics summary
        """
        summary = {}
        
        # Overall efficiency rating
        efficiency_score = analytics.get("efficiency_metrics", {}).get("efficiency_score", 0)
        if efficiency_score >= 80:
            summary["efficiency_rating"] = "Excellent"
        elif efficiency_score >= 60:
            summary["efficiency_rating"] = "Good"
        elif efficiency_score >= 40:
            summary["efficiency_rating"] = "Fair"
        else:
            summary["efficiency_rating"] = "Poor"
        
        summary["efficiency_score"] = efficiency_score
        
        # Key metrics
        efficiency_metrics = analytics.get("efficiency_metrics", {})
        summary["key_metrics"] = {
            "participation_balance": efficiency_metrics.get("participation_balance", 0),
            "engagement_score": efficiency_metrics.get("engagement_score", 0),
            "content_density": efficiency_metrics.get("content_density", 0),
            "time_efficiency": efficiency_metrics.get("time_efficiency", 0)
        }
        
        # Top topics
        topics = analytics.get("topics", [])
        summary["top_topics"] = [topic["topic"] for topic in topics[:3]]
        
        # Top suggestions
        suggestions = analytics.get("suggestions", [])
        summary["top_suggestions"] = [suggestion["suggestion"] for suggestion in suggestions[:3]]
        
        # Speaking time leaders
        speaking_time = analytics.get("speaking_time", {})
        sorted_speakers = sorted(
            [(speaker, percentage) for speaker, percentage in speaking_time.items() if speaker != "Unknown"],
            key=lambda x: x[1],
            reverse=True
        )
        summary["speaking_leaders"] = [speaker for speaker, _ in sorted_speakers[:3]]
        
        return summary
    
    def create_analytics_section(self, analytics: Dict[str, Any], format_type: str = "text", 
                                include_visualizations: bool = False) -> Dict[str, Any]:
        """
        Create a complete analytics section for MoM output.
        
        Args:
            analytics (Dict[str, Any]): Meeting analytics
            format_type (str): Output format type
            include_visualizations (bool): Whether to include visualization data
            
        Returns:
            Dict[str, Any]: Complete analytics section
        """
        section = {
            "title": "Meeting Analytics",
            "content": self.format_analytics(analytics, format_type),
            "summary": self.format_analytics_summary(analytics)
        }
        
        if include_visualizations:
            section["visualizations"] = self.create_visualization_data(analytics)
        
        # Add efficiency report
        if "efficiency_metrics" in analytics:
            from app.analyzer.efficiency_analyzer import EfficiencyAnalyzer
            efficiency_analyzer = EfficiencyAnalyzer()
            section["efficiency_report"] = efficiency_analyzer.generate_efficiency_report(analytics["efficiency_metrics"])
        
        return section
    
    def integrate_with_mom_data(self, mom_data: Dict[str, Any], analytics: Dict[str, Any]) -> Dict[str, Any]:
        """
        Integrate analytics data with MoM data.
        
        Args:
            mom_data (Dict[str, Any]): Original MoM data
            analytics (Dict[str, Any]): Meeting analytics
            
        Returns:
            Dict[str, Any]: MoM data with integrated analytics
        """
        # Create a copy of the original MoM data
        integrated_data = mom_data.copy()
        
        # Add analytics summary to metadata
        if "metadata" not in integrated_data:
            integrated_data["metadata"] = {}
        
        integrated_data["metadata"]["analytics_summary"] = self.format_analytics_summary(analytics)
        
        # Enhance action items with analytics insights
        if "action_items" in integrated_data and "suggestions" in analytics:
            # Add suggestions as potential action items
            suggestions = analytics["suggestions"]
            for suggestion in suggestions[:3]:  # Top 3 suggestions
                if suggestion["category"] in ["structure", "content"]:
                    suggested_action = {
                        "description": f"Process Improvement: {suggestion['suggestion']}",
                        "assignee": "Meeting Organizer",
                        "deadline": "Next Meeting",
                        "status": "suggested",
                        "type": "process_improvement",
                        "rationale": suggestion.get("reason", "")
                    }
                    integrated_data["action_items"].append(suggested_action)
        
        # Enhance attendees with participation data
        if "attendees" in integrated_data and "speaking_time" in analytics:
            speaking_time = analytics["speaking_time"]
            enhanced_attendees = []
            
            for attendee in integrated_data["attendees"]:
                if isinstance(attendee, str):
                    # Simple string format
                    attendee_name = attendee
                    enhanced_attendee = {
                        "name": attendee_name,
                        "participation_percentage": speaking_time.get(attendee_name, 0)
                    }
                elif isinstance(attendee, dict):
                    # Dictionary format
                    enhanced_attendee = attendee.copy()
                    attendee_name = attendee.get("name", "")
                    enhanced_attendee["participation_percentage"] = speaking_time.get(attendee_name, 0)
                else:
                    enhanced_attendee = attendee
                
                enhanced_attendees.append(enhanced_attendee)
            
            integrated_data["attendees"] = enhanced_attendees
        
        # Add topic analysis to discussion points
        if "discussion_points" in integrated_data and "topics" in analytics:
            topics = analytics["topics"]
            
            # Add topic relevance to existing discussion points
            for discussion in integrated_data["discussion_points"]:
                if isinstance(discussion, dict) and "topic" in discussion:
                    topic_name = discussion["topic"]
                    # Find matching topic in analytics
                    for topic in topics:
                        if topic["topic"].lower() in topic_name.lower() or topic_name.lower() in topic["topic"].lower():
                            discussion["relevance_score"] = topic.get("relevance", 0)
                            discussion["time_spent"] = topic.get("time_spent", "")
                            break
        
        # Add full analytics section
        integrated_data["analytics"] = self.create_analytics_section(analytics, "text", True)
        
        return integrated_data