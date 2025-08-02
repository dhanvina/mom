"""
Sentiment analyzer module for AI-powered MoM generator.

This module provides functionality for analyzing sentiment in meeting transcripts.
"""

import logging
import re
from typing import Dict, Any, Optional, List, Tuple
import nltk
from nltk.sentiment import SentimentIntensityAnalyzer
from nltk.tokenize import sent_tokenize

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class SentimentAnalyzer:
    """
    Analyzes sentiment in meeting transcripts.
    
    This class provides methods for analyzing sentiment in meeting transcripts
    and extracting sentiment-related insights.
    
    Attributes:
        config (Dict): Configuration options for the analyzer
        sia (SentimentIntensityAnalyzer): NLTK sentiment intensity analyzer
    """
    
    def __init__(self, config: Optional[Dict[str, Any]] = None):
        """
        Initialize the SentimentAnalyzer with optional configuration.
        
        Args:
            config (Dict, optional): Configuration options for the analyzer
        """
        self.config = config or {}
        
        # Initialize NLTK resources
        try:
            nltk.data.find('sentiment/vader_lexicon.zip')
        except LookupError:
            nltk.download('vader_lexicon')
        
        # Initialize sentiment analyzer
        self.sia = SentimentIntensityAnalyzer()
        
        logger.info("SentimentAnalyzer initialized")
    
    def analyze(self, transcript: str, speakers: Optional[List[str]] = None) -> Dict[str, Any]:
        """
        Analyze sentiment in a meeting transcript.
        
        Args:
            transcript (str): Meeting transcript
            speakers (List[str], optional): List of speaker names. If provided, sentiment will be analyzed per speaker.
            
        Returns:
            Dict[str, Any]: Sentiment analysis results
        """
        # Analyze overall sentiment
        overall_sentiment = self._analyze_overall_sentiment(transcript)
        
        # Analyze sentiment by speaker if speakers are provided
        speaker_sentiment = {}
        if speakers:
            speaker_sentiment = self._analyze_speaker_sentiment(transcript, speakers)
        
        # Analyze sentiment over time
        temporal_sentiment = self._analyze_temporal_sentiment(transcript)
        
        # Analyze sentiment by topic
        topic_sentiment = self._analyze_topic_sentiment(transcript)
        
        # Compile sentiment analysis results
        sentiment = {
            "overall": overall_sentiment,
            "speakers": speaker_sentiment,
            "temporal": temporal_sentiment,
            "topics": topic_sentiment
        }
        
        return sentiment
    
    def _analyze_overall_sentiment(self, transcript: str) -> Dict[str, float]:
        """
        Analyze overall sentiment in a transcript.
        
        Args:
            transcript (str): Meeting transcript
            
        Returns:
            Dict[str, float]: Overall sentiment scores
        """
        # Get sentiment scores
        scores = self.sia.polarity_scores(transcript)
        
        # Calculate sentiment label and confidence
        sentiment_label, confidence = self._get_sentiment_label(scores)
        
        # Compile overall sentiment
        overall_sentiment = {
            "compound": scores["compound"],
            "positive": scores["pos"],
            "neutral": scores["neu"],
            "negative": scores["neg"],
            "label": sentiment_label,
            "confidence": confidence
        }
        
        return overall_sentiment
    
    def _analyze_speaker_sentiment(self, transcript: str, speakers: List[str]) -> Dict[str, Dict[str, float]]:
        """
        Analyze sentiment by speaker.
        
        Args:
            transcript (str): Meeting transcript
            speakers (List[str]): List of speaker names
            
        Returns:
            Dict[str, Dict[str, float]]: Sentiment scores by speaker
        """
        # Initialize speaker sentiment
        speaker_sentiment = {}
        
        # Split transcript into lines
        lines = transcript.split('\n')
        
        # Group lines by speaker
        speaker_lines = {speaker: [] for speaker in speakers}
        speaker_lines["Unknown"] = []
        
        current_speaker = "Unknown"
        for line in lines:
            # Check if line starts with a speaker name
            speaker_found = False
            for speaker in speakers:
                if line.startswith(f"{speaker}:"):
                    current_speaker = speaker
                    # Remove speaker name from line
                    line = line[len(f"{speaker}:"):].strip()
                    speaker_found = True
                    break
            
            # Add line to current speaker
            if line:
                speaker_lines[current_speaker].append(line)
        
        # Analyze sentiment for each speaker
        for speaker, lines in speaker_lines.items():
            if lines:
                # Join lines for the speaker
                speaker_text = " ".join(lines)
                
                # Get sentiment scores
                scores = self.sia.polarity_scores(speaker_text)
                
                # Calculate sentiment label and confidence
                sentiment_label, confidence = self._get_sentiment_label(scores)
                
                # Add sentiment scores for the speaker
                speaker_sentiment[speaker] = {
                    "compound": scores["compound"],
                    "positive": scores["pos"],
                    "neutral": scores["neu"],
                    "negative": scores["neg"],
                    "label": sentiment_label,
                    "confidence": confidence
                }
        
        return speaker_sentiment
    
    def _analyze_temporal_sentiment(self, transcript: str) -> List[Dict[str, Any]]:
        """
        Analyze sentiment over time.
        
        Args:
            transcript (str): Meeting transcript
            
        Returns:
            List[Dict[str, Any]]: Sentiment scores over time
        """
        # Split transcript into sentences
        sentences = sent_tokenize(transcript)
        
        # Initialize temporal sentiment
        temporal_sentiment = []
        
        # Analyze sentiment for each sentence
        for i, sentence in enumerate(sentences):
            # Skip very short sentences
            if len(sentence.split()) < 3:
                continue
            
            # Get sentiment scores
            scores = self.sia.polarity_scores(sentence)
            
            # Calculate sentiment label and confidence
            sentiment_label, confidence = self._get_sentiment_label(scores)
            
            # Add sentiment scores for the sentence
            temporal_sentiment.append({
                "index": i,
                "text": sentence,
                "compound": scores["compound"],
                "positive": scores["pos"],
                "neutral": scores["neu"],
                "negative": scores["neg"],
                "label": sentiment_label,
                "confidence": confidence
            })
        
        return temporal_sentiment
    
    def _analyze_topic_sentiment(self, transcript: str) -> Dict[str, Dict[str, float]]:
        """
        Analyze sentiment by topic.
        
        Args:
            transcript (str): Meeting transcript
            
        Returns:
            Dict[str, Dict[str, float]]: Sentiment scores by topic
        """
        # Extract potential topics using simple keyword extraction
        topics = self._extract_topics(transcript)
        
        # Initialize topic sentiment
        topic_sentiment = {}
        
        # Analyze sentiment for each topic
        for topic, sentences in topics.items():
            if sentences:
                # Join sentences for the topic
                topic_text = " ".join(sentences)
                
                # Get sentiment scores
                scores = self.sia.polarity_scores(topic_text)
                
                # Calculate sentiment label and confidence
                sentiment_label, confidence = self._get_sentiment_label(scores)
                
                # Add sentiment scores for the topic
                topic_sentiment[topic] = {
                    "compound": scores["compound"],
                    "positive": scores["pos"],
                    "neutral": scores["neu"],
                    "negative": scores["neg"],
                    "label": sentiment_label,
                    "confidence": confidence
                }
        
        return topic_sentiment
    
    def _extract_topics(self, transcript: str) -> Dict[str, List[str]]:
        """
        Extract potential topics from a transcript.
        
        Args:
            transcript (str): Meeting transcript
            
        Returns:
            Dict[str, List[str]]: Dictionary mapping topics to related sentences
        """
        # Define common meeting topics
        common_topics = [
            "agenda", "timeline", "budget", "resources", "project",
            "deadline", "milestone", "decision", "action", "issue",
            "problem", "solution", "update", "status", "progress",
            "goal", "objective", "strategy", "plan", "risk"
        ]
        
        # Split transcript into sentences
        sentences = sent_tokenize(transcript)
        
        # Initialize topics
        topics = {topic: [] for topic in common_topics}
        
        # Group sentences by topic
        for sentence in sentences:
            sentence_lower = sentence.lower()
            for topic in common_topics:
                if topic in sentence_lower:
                    topics[topic].append(sentence)
        
        # Remove topics with no sentences
        topics = {topic: sentences for topic, sentences in topics.items() if sentences}
        
        return topics
    
    def _get_sentiment_label(self, scores: Dict[str, float]) -> Tuple[str, float]:
        """
        Get sentiment label and confidence from sentiment scores.
        
        Args:
            scores (Dict[str, float]): Sentiment scores
            
        Returns:
            Tuple[str, float]: Sentiment label and confidence
        """
        compound = scores["compound"]
        
        if compound >= 0.05:
            label = "positive"
            confidence = min(1.0, compound * 2)  # Scale to 0-1
        elif compound <= -0.05:
            label = "negative"
            confidence = min(1.0, abs(compound) * 2)  # Scale to 0-1
        else:
            label = "neutral"
            confidence = 1.0 - (abs(compound) * 10)  # Higher confidence for values closer to 0
        
        return label, confidence
    
    def get_sentiment_summary(self, sentiment: Dict[str, Any]) -> Dict[str, Any]:
        """
        Generate a summary of sentiment analysis results.
        
        Args:
            sentiment (Dict[str, Any]): Sentiment analysis results
            
        Returns:
            Dict[str, Any]: Sentiment summary
        """
        # Get overall sentiment
        overall = sentiment["overall"]
        
        # Get speaker sentiment
        speakers = sentiment["speakers"]
        
        # Get most positive and negative speakers
        most_positive_speaker = None
        most_negative_speaker = None
        max_positive = -1.0
        max_negative = -1.0
        
        for speaker, scores in speakers.items():
            if speaker != "Unknown":
                if scores["positive"] > max_positive:
                    max_positive = scores["positive"]
                    most_positive_speaker = speaker
                
                if scores["negative"] > max_negative:
                    max_negative = scores["negative"]
                    most_negative_speaker = speaker
        
        # Get sentiment trends
        temporal = sentiment["temporal"]
        sentiment_trend = "stable"
        
        if len(temporal) >= 10:
            # Calculate average compound score for first and last third
            first_third = temporal[:len(temporal)//3]
            last_third = temporal[-len(temporal)//3:]
            
            first_avg = sum(item["compound"] for item in first_third) / len(first_third)
            last_avg = sum(item["compound"] for item in last_third) / len(last_third)
            
            if last_avg - first_avg > 0.2:
                sentiment_trend = "improving"
            elif first_avg - last_avg > 0.2:
                sentiment_trend = "deteriorating"
        
        # Get topic sentiment
        topics = sentiment["topics"]
        
        # Get most positive and negative topics
        most_positive_topic = None
        most_negative_topic = None
        max_positive = -1.0
        max_negative = -1.0
        
        for topic, scores in topics.items():
            if scores["positive"] > max_positive:
                max_positive = scores["positive"]
                most_positive_topic = topic
            
            if scores["negative"] > max_negative:
                max_negative = scores["negative"]
                most_negative_topic = topic
        
        # Compile sentiment summary
        summary = {
            "overall_sentiment": overall["label"],
            "overall_confidence": overall["confidence"],
            "sentiment_trend": sentiment_trend,
            "most_positive_speaker": most_positive_speaker,
            "most_negative_speaker": most_negative_speaker,
            "most_positive_topic": most_positive_topic,
            "most_negative_topic": most_negative_topic
        }
        
        return summary
    
    def visualize_sentiment(self, sentiment: Dict[str, Any], visualization_type: str) -> Dict[str, Any]:
        """
        Create visualization data for sentiment analysis.
        
        Args:
            sentiment (Dict[str, Any]): Sentiment analysis results
            visualization_type (str): Type of visualization to create
            
        Returns:
            Dict[str, Any]: Visualization data
        """
        if visualization_type == "overall":
            # Create data for overall sentiment visualization
            overall = sentiment["overall"]
            return {
                "labels": ["Positive", "Neutral", "Negative"],
                "values": [overall["positive"], overall["neutral"], overall["negative"]]
            }
        
        elif visualization_type == "speakers":
            # Create data for speaker sentiment visualization
            speakers = sentiment["speakers"]
            return {
                "labels": [speaker for speaker in speakers.keys() if speaker != "Unknown"],
                "positive": [scores["positive"] for speaker, scores in speakers.items() if speaker != "Unknown"],
                "neutral": [scores["neutral"] for speaker, scores in speakers.items() if speaker != "Unknown"],
                "negative": [scores["negative"] for speaker, scores in speakers.items() if speaker != "Unknown"]
            }
        
        elif visualization_type == "temporal":
            # Create data for temporal sentiment visualization
            temporal = sentiment["temporal"]
            return {
                "indices": [item["index"] for item in temporal],
                "compound": [item["compound"] for item in temporal],
                "positive": [item["positive"] for item in temporal],
                "negative": [item["negative"] for item in temporal]
            }
        
        elif visualization_type == "topics":
            # Create data for topic sentiment visualization
            topics = sentiment["topics"]
            return {
                "labels": list(topics.keys()),
                "positive": [scores["positive"] for scores in topics.values()],
                "neutral": [scores["neutral"] for scores in topics.values()],
                "negative": [scores["negative"] for scores in topics.values()]
            }
        
        else:
            logger.warning(f"Unsupported visualization type: {visualization_type}")
            return {}