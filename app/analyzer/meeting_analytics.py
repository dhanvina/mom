"""
Meeting analytics module for AI-powered MoM generator.

This module provides functionality for analyzing meeting transcripts and extracting analytics.
"""

import logging
import re
from typing import Dict, Any, Optional, List, Tuple
from collections import Counter
import nltk
from nltk.tokenize import word_tokenize, sent_tokenize
from nltk.corpus import stopwords
from .topic_analyzer import TopicAnalyzer
from .efficiency_analyzer import EfficiencyAnalyzer
from .suggestion_generator import SuggestionGenerator

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class MeetingAnalytics:
    """
    Analyzes meeting transcripts and extracts analytics.
    
    This class provides methods for analyzing meeting transcripts and extracting
    analytics such as speaking time distribution, topic identification, and
    meeting efficiency metrics.
    
    Attributes:
        config (Dict): Configuration options for the analyzer
    """
    
    def __init__(self, config: Optional[Dict[str, Any]] = None):
        """
        Initialize the MeetingAnalytics with optional configuration.
        
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
            
        try:
            nltk.data.find('corpora/stopwords')
        except LookupError:
            try:
                nltk.download('stopwords')
            except:
                pass
        
        # Initialize topic analyzer
        self.topic_analyzer = TopicAnalyzer(self.config.get("topic_analyzer", {}))
        
        # Initialize efficiency analyzer
        self.efficiency_analyzer = EfficiencyAnalyzer(self.config.get("efficiency_analyzer", {}))
        
        # Initialize suggestion generator
        self.suggestion_generator = SuggestionGenerator(self.config.get("suggestion_generator", {}))
        
        logger.info("MeetingAnalytics initialized")
    
    def analyze(self, transcript: str, speakers: Optional[List[str]] = None) -> Dict[str, Any]:
        """
        Analyze a meeting transcript and extract analytics.
        
        Args:
            transcript (str): Meeting transcript
            speakers (List[str], optional): List of speaker names. If None, speakers will be detected from the transcript.
            
        Returns:
            Dict[str, Any]: Meeting analytics
        """
        # Detect speakers if not provided
        if speakers is None:
            speakers = self._detect_speakers(transcript)
        
        # Calculate speaking time distribution
        speaking_time = self._calculate_speaking_time(transcript, speakers)
        
        # Identify topics
        topics = self._identify_topics(transcript)
        
        # Calculate meeting efficiency metrics
        efficiency_metrics = self._calculate_efficiency_metrics(transcript, speakers)
        
        # Generate improvement suggestions
        suggestions = self._generate_improvement_suggestions(
            transcript, speakers, speaking_time, topics, efficiency_metrics
        )
        
        # Compile analytics
        analytics = {
            "speaking_time": speaking_time,
            "topics": topics,
            "efficiency_metrics": efficiency_metrics,
            "suggestions": suggestions
        }
        
        return analytics
    
    def _detect_speakers(self, transcript: str) -> List[str]:
        """
        Detect speakers from a transcript.
        
        Args:
            transcript (str): Meeting transcript
            
        Returns:
            List[str]: List of detected speaker names
        """
        # Simple pattern matching for speaker detection
        # This is a basic implementation and can be improved with NER or other techniques
        speaker_pattern = r'([A-Z][a-z]+ [A-Z][a-z]+):'
        speakers = set(re.findall(speaker_pattern, transcript))
        
        return list(speakers)
    
    def _calculate_speaking_time(self, transcript: str, speakers: List[str]) -> Dict[str, float]:
        """
        Calculate speaking time distribution among participants.
        
        Args:
            transcript (str): Meeting transcript
            speakers (List[str]): List of speaker names
            
        Returns:
            Dict[str, float]: Dictionary mapping speaker names to their speaking time percentage
        """
        # Initialize speaking time counter
        speaking_time = {speaker: 0 for speaker in speakers}
        
        # Add "Unknown" speaker for unattributed text
        speaking_time["Unknown"] = 0
        
        # Split transcript into lines
        lines = transcript.split('\n')
        
        current_speaker = "Unknown"
        for line in lines:
            line = line.strip()
            if not line:
                continue
                
            # Check if line starts with a speaker name
            speaker_found = False
            for speaker in speakers:
                if line.startswith(f"{speaker}:"):
                    current_speaker = speaker
                    # Remove speaker name from line
                    line = line[len(f"{speaker}:"):].strip()
                    speaker_found = True
                    break
            
            # If no speaker found but line has content, continue with current speaker
            if not speaker_found and line:
                # Count words spoken by current speaker
                words = len(line.split())
                speaking_time[current_speaker] += words
            elif speaker_found and line:
                # Count words for the new speaker
                words = len(line.split())
                speaking_time[current_speaker] += words
        
        # Calculate total words
        total_words = sum(speaking_time.values())
        
        # Convert word counts to percentages
        if total_words > 0:
            speaking_time = {
                speaker: (count / total_words) * 100
                for speaker, count in speaking_time.items()
            }
        else:
            # If no words found, distribute equally
            equal_percentage = 100.0 / len(speakers) if speakers else 0
            speaking_time = {speaker: equal_percentage for speaker in speakers}
            speaking_time["Unknown"] = 0
        
        return speaking_time
    
    def _identify_topics(self, transcript: str) -> List[Dict[str, Any]]:
        """
        Identify recurring topics or themes in the transcript.
        
        Args:
            transcript (str): Meeting transcript
            
        Returns:
            List[Dict[str, Any]]: List of identified topics with relevance scores
        """
        # Use the TopicAnalyzer to identify topics
        num_topics = self.config.get("num_topics", 10)
        topics = self.topic_analyzer.identify_topics(transcript, num_topics=num_topics)
        
        # Generate topic distribution for visualization
        topic_distribution = self.topic_analyzer.generate_topic_distribution(topics)
        
        # Add distribution data to each topic
        for topic in topics:
            topic["distribution"] = topic_distribution.get(topic["topic"], 0)
        
        return topics
    
    def _calculate_efficiency_metrics(self, transcript: str, speakers: List[str]) -> Dict[str, Any]:
        """
        Calculate meeting efficiency metrics.
        
        Args:
            transcript (str): Meeting transcript
            speakers (List[str]): List of speaker names
            
        Returns:
            Dict[str, Any]: Dictionary of efficiency metrics
        """
        # Use the EfficiencyAnalyzer to calculate metrics
        # Extract start and end times from transcript if available
        start_time, end_time = self._extract_meeting_times(transcript)
        
        # Calculate metrics using the efficiency analyzer
        metrics = self.efficiency_analyzer.calculate_metrics(
            transcript, speakers, start_time, end_time
        )
        
        # Compare with past meetings if available
        past_metrics = self.config.get("past_metrics", [])
        if past_metrics:
            comparison = self.efficiency_analyzer.compare_with_past_meetings(metrics, past_metrics)
            metrics["comparison"] = comparison
        
        return metrics
        
    def _extract_meeting_times(self, transcript: str) -> Tuple[Optional[str], Optional[str]]:
        """
        Extract meeting start and end times from transcript.
        
        Args:
            transcript (str): Meeting transcript
            
        Returns:
            Tuple[Optional[str], Optional[str]]: Meeting start and end times in format "HH:MM"
        """
        # Try to find start time
        start_time_patterns = [
            r'start(?:ed|ing)?\s+at\s+(\d{1,2}:\d{2})',
            r'begin(?:s|ning)?\s+at\s+(\d{1,2}:\d{2})',
            r'meeting\s+start(?:ed|ing)?\s+at\s+(\d{1,2}:\d{2})'
        ]
        
        start_time = None
        for pattern in start_time_patterns:
            match = re.search(pattern, transcript.lower())
            if match:
                start_time = match.group(1)
                # Ensure HH:MM format
                if len(start_time.split(':')[0]) == 1:
                    start_time = f"0{start_time}"
                break
        
        # Try to find end time
        end_time_patterns = [
            r'end(?:ed|ing)?\s+at\s+(\d{1,2}:\d{2})',
            r'adjourn(?:ed)?\s+at\s+(\d{1,2}:\d{2})',
            r'meeting\s+end(?:ed|ing)?\s+at\s+(\d{1,2}:\d{2})'
        ]
        
        end_time = None
        for pattern in end_time_patterns:
            match = re.search(pattern, transcript.lower())
            if match:
                end_time = match.group(1)
                # Ensure HH:MM format
                if len(end_time.split(':')[0]) == 1:
                    end_time = f"0{end_time}"
                break
        
        return start_time, end_time
    
    def _calculate_participation_balance(self, speaking_time: Dict[str, float]) -> float:
        """
        Calculate participation balance based on speaking time distribution.
        
        Args:
            speaking_time (Dict[str, float]): Dictionary mapping speaker names to their speaking time percentage
            
        Returns:
            float: Participation balance score (0-100, higher is more balanced)
        """
        # Remove "Unknown" speaker
        if "Unknown" in speaking_time:
            speaking_time = {k: v for k, v in speaking_time.items() if k != "Unknown"}
        
        # If no speakers, return 0
        if not speaking_time:
            return 0
        
        # Calculate ideal equal distribution
        ideal_percentage = 100 / len(speaking_time)
        
        # Calculate deviation from ideal
        deviation = sum(abs(percentage - ideal_percentage) for percentage in speaking_time.values())
        
        # Normalize to 0-100 scale (0 = completely unbalanced, 100 = perfectly balanced)
        max_deviation = 2 * (100 - ideal_percentage)  # Maximum possible deviation
        balance_score = 100 - (deviation / max_deviation * 100) if max_deviation > 0 else 100
        
        return balance_score
    
    def _generate_improvement_suggestions(self, transcript: str, speakers: List[str],
                                         speaking_time: Dict[str, float], topics: List[Dict[str, Any]],
                                         efficiency_metrics: Dict[str, Any]) -> List[Dict[str, Any]]:
        """
        Generate suggestions for improving future meetings.
        
        Args:
            transcript (str): Meeting transcript
            speakers (List[str]): List of speaker names
            speaking_time (Dict[str, float]): Speaking time distribution
            topics (List[Dict[str, Any]]): Identified topics
            efficiency_metrics (Dict[str, Any]): Efficiency metrics
            
        Returns:
            List[Dict[str, Any]]: List of improvement suggestions
        """
        # Compile analytics for the suggestion generator
        analytics = {
            "speaking_time": speaking_time,
            "topics": topics,
            "efficiency_metrics": efficiency_metrics
        }
        
        # Use the SuggestionGenerator to generate suggestions
        suggestions = self.suggestion_generator.generate_suggestions(transcript, analytics)
        
        # Apply user preferences if available
        user_preferences = self.config.get("user_preferences", {})
        if user_preferences:
            suggestions = self.suggestion_generator.generate_personalized_suggestions(
                transcript, analytics, user_preferences
            )
        
        return suggestions