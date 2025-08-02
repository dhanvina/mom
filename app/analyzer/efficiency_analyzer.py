"""
Efficiency analyzer module for AI-powered MoM generator.

This module provides functionality for analyzing meeting efficiency.
"""

import logging
import re
from typing import Dict, Any, Optional, List, Tuple
from collections import Counter
import nltk
from nltk.tokenize import word_tokenize, sent_tokenize
import datetime

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class EfficiencyAnalyzer:
    """
    Analyzes meeting efficiency.
    
    This class provides methods for calculating meeting efficiency metrics.
    
    Attributes:
        config (Dict): Configuration options for the analyzer
    """
    
    def __init__(self, config: Optional[Dict[str, Any]] = None):
        """
        Initialize the EfficiencyAnalyzer with optional configuration.
        
        Args:
            config (Dict, optional): Configuration options for the analyzer
        """
        self.config = config or {}
        
        # Initialize NLTK resources
        try:
            nltk.data.find('tokenizers/punkt')
        except LookupError:
            try:
                nltk.download('punkt')
            except:
                pass
        
        try:
            nltk.data.find('tokenizers/punkt_tab')
        except LookupError:
            try:
                nltk.download('punkt_tab')
            except:
                pass
        
        logger.info("EfficiencyAnalyzer initialized")
    
    def calculate_metrics(self, transcript: str, speakers: List[str], 
                         start_time: Optional[str] = None, end_time: Optional[str] = None) -> Dict[str, Any]:
        """
        Calculate meeting efficiency metrics.
        
        Args:
            transcript (str): Meeting transcript
            speakers (List[str]): List of speaker names
            start_time (str, optional): Meeting start time in format "HH:MM"
            end_time (str, optional): Meeting end time in format "HH:MM"
            
        Returns:
            Dict[str, Any]: Dictionary of efficiency metrics
        """
        # Calculate basic metrics
        basic_metrics = self._calculate_basic_metrics(transcript, speakers)
        
        # Calculate time-based metrics if start and end times are provided
        time_metrics = {}
        if start_time and end_time:
            time_metrics = self._calculate_time_metrics(transcript, start_time, end_time)
        
        # Calculate content metrics
        content_metrics = self._calculate_content_metrics(transcript)
        
        # Calculate participation metrics
        participation_metrics = self._calculate_participation_metrics(transcript, speakers)
        
        # Calculate overall efficiency score
        efficiency_score = self._calculate_efficiency_score(
            basic_metrics, time_metrics, content_metrics, participation_metrics
        )
        
        # Combine all metrics
        metrics = {
            **basic_metrics,
            **time_metrics,
            **content_metrics,
            **participation_metrics,
            "efficiency_score": efficiency_score
        }
        
        return metrics
    
    def _calculate_basic_metrics(self, transcript: str, speakers: List[str]) -> Dict[str, Any]:
        """
        Calculate basic meeting metrics.
        
        Args:
            transcript (str): Meeting transcript
            speakers (List[str]): List of speaker names
            
        Returns:
            Dict[str, Any]: Dictionary of basic metrics
        """
        # Count total words
        try:
            words = word_tokenize(transcript)
        except Exception as e:
            logger.warning(f"NLTK word tokenization failed, using simple fallback: {e}")
            # Simple word splitting fallback
            words = transcript.split()
        total_words = len(words)
        
        # Count sentences
        try:
            sentences = sent_tokenize(transcript)
        except Exception as e:
            logger.warning(f"NLTK sentence tokenization failed, using simple fallback: {e}")
            # Simple sentence splitting fallback
            sentences = [s.strip() for s in transcript.split('.') if s.strip()]
        total_sentences = len(sentences)
        
        # Calculate average sentence length
        avg_sentence_length = total_words / total_sentences if total_sentences > 0 else 0
        
        # Calculate speaker turns
        speaker_turns = 0
        current_speaker = None
        
        # Split transcript into lines
        lines = transcript.split('\n')
        
        for line in lines:
            # Check if line starts with a speaker name
            for speaker in speakers:
                if line.startswith(f"{speaker}:"):
                    if current_speaker != speaker:
                        speaker_turns += 1
                        current_speaker = speaker
                    break
        
        # Calculate speaker turn rate
        speaker_turn_rate = speaker_turns / total_sentences if total_sentences > 0 else 0
        
        # Compile basic metrics
        metrics = {
            "total_words": total_words,
            "total_sentences": total_sentences,
            "avg_sentence_length": avg_sentence_length,
            "speaker_turns": speaker_turns,
            "speaker_turn_rate": speaker_turn_rate
        }
        
        return metrics
    
    def _calculate_time_metrics(self, transcript: str, start_time: str, end_time: str) -> Dict[str, Any]:
        """
        Calculate time-based meeting metrics.
        
        Args:
            transcript (str): Meeting transcript
            start_time (str): Meeting start time in format "HH:MM"
            end_time (str): Meeting end time in format "HH:MM"
            
        Returns:
            Dict[str, Any]: Dictionary of time-based metrics
        """
        try:
            # Parse start and end times
            start = datetime.datetime.strptime(start_time, "%H:%M")
            end = datetime.datetime.strptime(end_time, "%H:%M")
            
            # Calculate meeting duration in minutes
            duration = (end - start).total_seconds() / 60
            
            # Count total words
            total_words = len(word_tokenize(transcript))
            
            # Calculate words per minute
            words_per_minute = total_words / duration if duration > 0 else 0
            
            # Estimate optimal duration based on content
            # (rough estimate: 125 words per minute is a good pace)
            optimal_duration = total_words / 125
            
            # Calculate time efficiency
            time_efficiency = (optimal_duration / duration) * 100 if duration > 0 else 0
            
            # Cap time efficiency at 100%
            time_efficiency = min(time_efficiency, 100)
            
            # Compile time metrics
            metrics = {
                "duration_minutes": duration,
                "words_per_minute": words_per_minute,
                "optimal_duration": optimal_duration,
                "time_efficiency": time_efficiency
            }
            
            return metrics
            
        except ValueError:
            logger.warning("Invalid time format. Expected HH:MM.")
            return {}
    
    def _calculate_content_metrics(self, transcript: str) -> Dict[str, Any]:
        """
        Calculate content-based meeting metrics.
        
        Args:
            transcript (str): Meeting transcript
            
        Returns:
            Dict[str, Any]: Dictionary of content-based metrics
        """
        # Count action items
        action_item_indicators = ["action item", "task", "to-do", "follow up", "will do"]
        action_items = sum(transcript.lower().count(indicator) for indicator in action_item_indicators)
        
        # Count decisions
        decision_indicators = ["decided", "decision", "agree", "concluded", "resolved"]
        decisions = sum(transcript.lower().count(indicator) for indicator in decision_indicators)
        
        # Check for agenda
        has_agenda = "agenda" in transcript.lower()
        
        # Check for summary
        has_summary = any(indicator in transcript.lower() for indicator in ["summary", "summarize", "recap"])
        
        # Calculate content structure score
        content_structure_score = 0
        if has_agenda:
            content_structure_score += 50
        if has_summary:
            content_structure_score += 50
        
        # Calculate content density
        sentences = sent_tokenize(transcript)
        total_sentences = len(sentences)
        
        # Count sentences with substantive content
        substantive_indicators = [
            "discuss", "present", "explain", "analyze", "report", "update",
            "issue", "problem", "solution", "strategy", "plan", "result"
        ]
        
        substantive_sentences = sum(
            1 for sentence in sentences
            if any(indicator in sentence.lower() for indicator in substantive_indicators)
        )
        
        content_density = (substantive_sentences / total_sentences) * 100 if total_sentences > 0 else 0
        
        # Compile content metrics
        metrics = {
            "action_items": action_items,
            "decisions": decisions,
            "has_agenda": has_agenda,
            "has_summary": has_summary,
            "content_structure_score": content_structure_score,
            "content_density": content_density
        }
        
        return metrics
    
    def _calculate_participation_metrics(self, transcript: str, speakers: List[str]) -> Dict[str, Any]:
        """
        Calculate participation-based meeting metrics.
        
        Args:
            transcript (str): Meeting transcript
            speakers (List[str]): List of speaker names
            
        Returns:
            Dict[str, Any]: Dictionary of participation-based metrics
        """
        # Initialize speaking time counter
        speaking_time = {speaker: 0 for speaker in speakers}
        
        # Add "Unknown" speaker for unattributed text
        speaking_time["Unknown"] = 0
        
        # Split transcript into lines
        lines = transcript.split('\n')
        
        current_speaker = "Unknown"
        for line in lines:
            # Check if line starts with a speaker name
            for speaker in speakers:
                if line.startswith(f"{speaker}:"):
                    current_speaker = speaker
                    # Remove speaker name from line
                    line = line[len(f"{speaker}:"):].strip()
                    break
            
            # Count words spoken by current speaker
            words = len(line.split())
            speaking_time[current_speaker] += words
        
        # Calculate total words
        total_words = sum(speaking_time.values())
        
        # Convert word counts to percentages
        if total_words > 0:
            speaking_percentages = {
                speaker: (count / total_words) * 100
                for speaker, count in speaking_time.items()
            }
        else:
            speaking_percentages = {speaker: 0 for speaker in speaking_time}
        
        # Calculate participation balance
        participation_balance = self._calculate_participation_balance(speaking_percentages)
        
        # Calculate engagement score
        engagement_score = self._calculate_engagement_score(transcript, speakers)
        
        # Compile participation metrics
        metrics = {
            "speaking_percentages": speaking_percentages,
            "participation_balance": participation_balance,
            "engagement_score": engagement_score
        }
        
        return metrics
    
    def _calculate_participation_balance(self, speaking_percentages: Dict[str, float]) -> float:
        """
        Calculate participation balance based on speaking time distribution.
        
        Args:
            speaking_percentages (Dict[str, float]): Dictionary mapping speaker names to their speaking time percentage
            
        Returns:
            float: Participation balance score (0-100, higher is more balanced)
        """
        # Remove "Unknown" speaker
        if "Unknown" in speaking_percentages:
            speaking_percentages = {k: v for k, v in speaking_percentages.items() if k != "Unknown"}
        
        # If no speakers, return 0
        if not speaking_percentages:
            return 0
        
        # Calculate ideal equal distribution
        ideal_percentage = 100 / len(speaking_percentages)
        
        # Calculate deviation from ideal
        deviation = sum(abs(percentage - ideal_percentage) for percentage in speaking_percentages.values())
        
        # Normalize to 0-100 scale (0 = completely unbalanced, 100 = perfectly balanced)
        max_deviation = 2 * (100 - ideal_percentage)  # Maximum possible deviation
        balance_score = 100 - (deviation / max_deviation * 100) if max_deviation > 0 else 100
        
        return balance_score
    
    def _calculate_engagement_score(self, transcript: str, speakers: List[str]) -> float:
        """
        Calculate engagement score based on interaction patterns.
        
        Args:
            transcript (str): Meeting transcript
            speakers (List[str]): List of speaker names
            
        Returns:
            float: Engagement score (0-100, higher is more engaged)
        """
        # Count questions
        question_count = transcript.count("?")
        
        # Count responses (lines that follow questions)
        response_count = 0
        lines = transcript.split('\n')
        for i in range(len(lines) - 1):
            if "?" in lines[i]:
                response_count += 1
        
        # Calculate question-response ratio
        question_response_ratio = response_count / question_count if question_count > 0 else 0
        
        # Count speaker transitions
        speaker_transitions = 0
        current_speaker = None
        
        for line in lines:
            # Check if line starts with a speaker name
            for speaker in speakers:
                if line.startswith(f"{speaker}:"):
                    if current_speaker != speaker:
                        speaker_transitions += 1
                        current_speaker = speaker
                    break
        
        # Calculate speaker transition rate
        transition_rate = speaker_transitions / len(lines) if len(lines) > 0 else 0
        
        # Calculate engagement score
        # (50% based on question-response ratio, 50% based on transition rate)
        engagement_score = (question_response_ratio * 50) + (transition_rate * 100)
        
        # Cap at 100
        engagement_score = min(engagement_score, 100)
        
        return engagement_score
    
    def _calculate_efficiency_score(self, basic_metrics: Dict[str, Any], 
                                   time_metrics: Dict[str, Any],
                                   content_metrics: Dict[str, Any],
                                   participation_metrics: Dict[str, Any]) -> float:
        """
        Calculate overall meeting efficiency score.
        
        Args:
            basic_metrics (Dict[str, Any]): Basic meeting metrics
            time_metrics (Dict[str, Any]): Time-based meeting metrics
            content_metrics (Dict[str, Any]): Content-based meeting metrics
            participation_metrics (Dict[str, Any]): Participation-based meeting metrics
            
        Returns:
            float: Overall efficiency score (0-100, higher is more efficient)
        """
        # Initialize score components
        components = []
        
        # Add time efficiency if available
        if "time_efficiency" in time_metrics:
            components.append(time_metrics["time_efficiency"])
        
        # Add content structure score
        components.append(content_metrics["content_structure_score"])
        
        # Add content density
        components.append(content_metrics["content_density"])
        
        # Add participation balance
        components.append(participation_metrics["participation_balance"])
        
        # Add engagement score
        components.append(participation_metrics["engagement_score"])
        
        # Calculate overall score (average of components)
        efficiency_score = sum(components) / len(components) if components else 0
        
        return efficiency_score
    
    def compare_with_past_meetings(self, current_metrics: Dict[str, Any], 
                                  past_metrics: List[Dict[str, Any]]) -> Dict[str, Any]:
        """
        Compare current meeting metrics with past meetings.
        
        Args:
            current_metrics (Dict[str, Any]): Current meeting metrics
            past_metrics (List[Dict[str, Any]]): List of past meeting metrics
            
        Returns:
            Dict[str, Any]: Comparison results
        """
        if not past_metrics:
            return {"comparison": "No past meetings to compare with"}
        
        # Calculate average metrics from past meetings
        avg_metrics = {}
        for key in current_metrics:
            if key in past_metrics[0] and isinstance(current_metrics[key], (int, float)):
                avg_metrics[key] = sum(m.get(key, 0) for m in past_metrics) / len(past_metrics)
        
        # Calculate percentage changes
        changes = {}
        for key, avg_value in avg_metrics.items():
            if avg_value != 0:
                changes[key] = ((current_metrics[key] - avg_value) / avg_value) * 100
            else:
                changes[key] = 0
        
        # Determine improvements and regressions
        improvements = {k: v for k, v in changes.items() if v > 0}
        regressions = {k: v for k, v in changes.items() if v < 0}
        
        # Calculate trend analysis
        trend_analysis = self._calculate_trend_analysis(past_metrics)
        
        # Compile comparison results
        comparison = {
            "avg_past_metrics": avg_metrics,
            "changes": changes,
            "improvements": improvements,
            "regressions": regressions,
            "trend_analysis": trend_analysis
        }
        
        return comparison
    
    def _calculate_trend_analysis(self, past_metrics: List[Dict[str, Any]]) -> Dict[str, Any]:
        """
        Calculate trend analysis from past meetings.
        
        Args:
            past_metrics (List[Dict[str, Any]]): List of past meeting metrics
            
        Returns:
            Dict[str, Any]: Trend analysis results
        """
        if len(past_metrics) < 2:
            return {"trend": "Insufficient data for trend analysis"}
        
        # Sort metrics by date if available
        sorted_metrics = past_metrics.copy()
        
        # Calculate trends for key metrics
        trends = {}
        key_metrics = ["efficiency_score", "participation_balance", "engagement_score", "content_density"]
        
        for metric in key_metrics:
            if metric in sorted_metrics[0]:
                values = [m.get(metric, 0) for m in sorted_metrics]
                
                # Calculate simple linear trend
                n = len(values)
                x_sum = sum(range(n))
                y_sum = sum(values)
                xy_sum = sum(i * values[i] for i in range(n))
                x2_sum = sum(i * i for i in range(n))
                
                # Calculate slope
                if n * x2_sum - x_sum * x_sum != 0:
                    slope = (n * xy_sum - x_sum * y_sum) / (n * x2_sum - x_sum * x_sum)
                    
                    if slope > 0.5:
                        trends[metric] = "improving"
                    elif slope < -0.5:
                        trends[metric] = "declining"
                    else:
                        trends[metric] = "stable"
                else:
                    trends[metric] = "stable"
        
        return {"trends": trends}
    
    def create_visualization_data(self, metrics: Dict[str, Any]) -> Dict[str, Any]:
        """
        Create visualization data for meeting efficiency metrics.
        
        Args:
            metrics (Dict[str, Any]): Meeting efficiency metrics
            
        Returns:
            Dict[str, Any]: Visualization data
        """
        visualization_data = {}
        
        # Speaking time pie chart data
        if "speaking_percentages" in metrics:
            speaking_data = metrics["speaking_percentages"]
            # Remove Unknown speaker if it has 0%
            speaking_data = {k: v for k, v in speaking_data.items() if k != "Unknown" or v > 0}
            
            visualization_data["speaking_time"] = {
                "type": "pie",
                "title": "Speaking Time Distribution",
                "labels": list(speaking_data.keys()),
                "values": list(speaking_data.values()),
                "colors": ["#FF6B6B", "#4ECDC4", "#45B7D1", "#96CEB4", "#FFEAA7", "#DDA0DD"]
            }
        
        # Efficiency metrics radar chart
        efficiency_metrics = {
            "Time Efficiency": metrics.get("time_efficiency", 0),
            "Content Structure": metrics.get("content_structure_score", 0),
            "Content Density": metrics.get("content_density", 0),
            "Participation Balance": metrics.get("participation_balance", 0),
            "Engagement Score": metrics.get("engagement_score", 0)
        }
        
        visualization_data["efficiency_radar"] = {
            "type": "radar",
            "title": "Meeting Efficiency Metrics",
            "labels": list(efficiency_metrics.keys()),
            "values": list(efficiency_metrics.values()),
            "max_value": 100
        }
        
        # Overall efficiency gauge
        visualization_data["efficiency_gauge"] = {
            "type": "gauge",
            "title": "Overall Efficiency Score",
            "value": metrics.get("efficiency_score", 0),
            "max_value": 100,
            "thresholds": [
                {"value": 30, "color": "#FF6B6B", "label": "Poor"},
                {"value": 60, "color": "#FFEAA7", "label": "Fair"},
                {"value": 80, "color": "#96CEB4", "label": "Good"},
                {"value": 100, "color": "#4ECDC4", "label": "Excellent"}
            ]
        }
        
        # Meeting timeline (if duration is available)
        if "duration_minutes" in metrics:
            duration = metrics["duration_minutes"]
            visualization_data["meeting_timeline"] = {
                "type": "timeline",
                "title": "Meeting Timeline",
                "duration": duration,
                "segments": [
                    {"label": "Opening", "duration": min(5, duration * 0.1), "color": "#45B7D1"},
                    {"label": "Discussion", "duration": duration * 0.7, "color": "#4ECDC4"},
                    {"label": "Action Items", "duration": duration * 0.15, "color": "#96CEB4"},
                    {"label": "Closing", "duration": min(5, duration * 0.05), "color": "#FFEAA7"}
                ]
            }
        
        # Content metrics bar chart
        content_metrics = {
            "Action Items": metrics.get("action_items", 0),
            "Decisions": metrics.get("decisions", 0),
            "Speaker Turns": metrics.get("speaker_turns", 0)
        }
        
        visualization_data["content_metrics"] = {
            "type": "bar",
            "title": "Content Metrics",
            "labels": list(content_metrics.keys()),
            "values": list(content_metrics.values()),
            "colors": ["#FF6B6B", "#4ECDC4", "#45B7D1"]
        }
        
        return visualization_data
    
    def generate_efficiency_report(self, metrics: Dict[str, Any]) -> Dict[str, Any]:
        """
        Generate a comprehensive efficiency report.
        
        Args:
            metrics (Dict[str, Any]): Meeting efficiency metrics
            
        Returns:
            Dict[str, Any]: Efficiency report
        """
        # Calculate overall rating
        efficiency_score = metrics.get("efficiency_score", 0)
        
        if efficiency_score >= 80:
            rating = "Excellent"
            rating_color = "#4ECDC4"
        elif efficiency_score >= 60:
            rating = "Good"
            rating_color = "#96CEB4"
        elif efficiency_score >= 40:
            rating = "Fair"
            rating_color = "#FFEAA7"
        else:
            rating = "Poor"
            rating_color = "#FF6B6B"
        
        # Identify strengths and weaknesses
        strengths = []
        weaknesses = []
        
        if metrics.get("participation_balance", 0) >= 70:
            strengths.append("Well-balanced participation")
        else:
            weaknesses.append("Unbalanced participation")
        
        if metrics.get("engagement_score", 0) >= 70:
            strengths.append("High engagement level")
        else:
            weaknesses.append("Low engagement level")
        
        if metrics.get("content_structure_score", 0) >= 50:
            strengths.append("Good meeting structure")
        else:
            weaknesses.append("Poor meeting structure")
        
        if metrics.get("content_density", 0) >= 60:
            strengths.append("High content density")
        else:
            weaknesses.append("Low content density")
        
        if metrics.get("time_efficiency", 0) >= 70:
            strengths.append("Efficient time usage")
        else:
            weaknesses.append("Inefficient time usage")
        
        # Generate key insights
        insights = []
        
        if metrics.get("action_items", 0) == 0:
            insights.append("No action items identified - consider defining clear next steps")
        
        if metrics.get("decisions", 0) == 0:
            insights.append("No decisions recorded - ensure decision-making is documented")
        
        if not metrics.get("has_agenda", False):
            insights.append("No agenda detected - structured agendas improve meeting efficiency")
        
        if not metrics.get("has_summary", False):
            insights.append("No summary detected - meeting summaries help reinforce key points")
        
        # Compile report
        report = {
            "overall_rating": {
                "score": efficiency_score,
                "rating": rating,
                "color": rating_color
            },
            "strengths": strengths,
            "weaknesses": weaknesses,
            "key_insights": insights,
            "metrics_summary": {
                "duration": metrics.get("duration_minutes", "N/A"),
                "participants": len([k for k in metrics.get("speaking_percentages", {}).keys() if k != "Unknown"]),
                "action_items": metrics.get("action_items", 0),
                "decisions": metrics.get("decisions", 0),
                "engagement": f"{metrics.get('engagement_score', 0):.1f}%",
                "participation_balance": f"{metrics.get('participation_balance', 0):.1f}%"
            }
        }
        
        return report