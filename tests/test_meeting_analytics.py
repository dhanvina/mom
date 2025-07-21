"""
Unit tests for the MeetingAnalytics class.
"""

import pytest
from unittest.mock import patch, MagicMock
from app.analyzer.meeting_analytics import MeetingAnalytics

class TestMeetingAnalytics:
    """Test cases for MeetingAnalytics class."""
    
    def setup_method(self):
        """Set up test fixtures."""
        self.analytics = MeetingAnalytics()
        
        # Create a test transcript
        self.transcript = """
John Smith: Good morning everyone. Today we'll discuss the project timeline.
Jane Doe: Thanks John. I've prepared a presentation on our progress.
John Smith: Great, let's start with the current status.
Jane Doe: We've completed the first phase and are now moving to the second phase.
John Smith: What challenges are we facing?
Jane Doe: The main challenge is resource allocation. We need more developers.
John Smith: I'll talk to the resource manager about getting more help.
Jane Doe: That would be great. We also need to discuss the budget.
John Smith: Let's schedule a separate meeting for budget discussion.
Jane Doe: Agreed. For now, let's focus on the timeline.
John Smith: Our deadline is next month. Are we on track?
Jane Doe: Yes, we're on track despite the resource constraints.
John Smith: Good to hear. Any other concerns?
Jane Doe: No, that's all from my side.
John Smith: Alright, let's summarize the action items.
Jane Doe: Action item for John: Talk to resource manager about additional developers.
John Smith: Action item for both of us: Prepare for the budget meeting next week.
Jane Doe: That's it for today. Thank you everyone.
        """.strip()
        
        # Define speakers
        self.speakers = ["John Smith", "Jane Doe"]
    
    def test_init(self):
        """Test initialization with default and custom config."""
        # Default config
        analytics = MeetingAnalytics()
        assert analytics.config == {}
        
        # Custom config
        custom_config = {"threshold": 0.5}
        analytics = MeetingAnalytics(config=custom_config)
        assert analytics.config == custom_config
    
    def test_analyze(self):
        """Test analyzing a transcript."""
        # Analyze transcript
        result = self.analytics.analyze(self.transcript, self.speakers)
        
        # Verify result structure
        assert "speaking_time" in result
        assert "topics" in result
        assert "efficiency_metrics" in result
        assert "suggestions" in result
        
        # Verify speaking time
        assert "John Smith" in result["speaking_time"]
        assert "Jane Doe" in result["speaking_time"]
        
        # Verify topics
        assert isinstance(result["topics"], list)
        assert len(result["topics"]) > 0
        
        # Verify efficiency metrics
        assert "total_words" in result["efficiency_metrics"]
        assert "total_sentences" in result["efficiency_metrics"]
        assert "avg_sentence_length" in result["efficiency_metrics"]
        assert "speaker_turns" in result["efficiency_metrics"]
        assert "participation_balance" in result["efficiency_metrics"]
        
        # Verify suggestions
        assert isinstance(result["suggestions"], list)
    
    def test_detect_speakers(self):
        """Test detecting speakers from a transcript."""
        # Detect speakers
        speakers = self.analytics._detect_speakers(self.transcript)
        
        # Verify detected speakers
        assert "John Smith" in speakers
        assert "Jane Doe" in speakers
    
    def test_calculate_speaking_time(self):
        """Test calculating speaking time distribution."""
        # Calculate speaking time
        speaking_time = self.analytics._calculate_speaking_time(self.transcript, self.speakers)
        
        # Verify speaking time
        assert "John Smith" in speaking_time
        assert "Jane Doe" in speaking_time
        assert "Unknown" in speaking_time
        
        # Verify percentages sum to approximately 100%
        total_percentage = sum(speaking_time.values())
        assert 99.5 <= total_percentage <= 100.5
    
    def test_identify_topics(self):
        """Test identifying topics from a transcript."""
        # Identify topics
        topics = self.analytics._identify_topics(self.transcript)
        
        # Verify topics
        assert isinstance(topics, list)
        assert len(topics) > 0
        
        # Verify topic structure
        for topic in topics:
            assert "topic" in topic
            assert "relevance" in topic
            assert "mentions" in topic
    
    def test_calculate_efficiency_metrics(self):
        """Test calculating efficiency metrics."""
        # Calculate efficiency metrics
        metrics = self.analytics._calculate_efficiency_metrics(self.transcript, self.speakers)
        
        # Verify metrics
        assert "total_words" in metrics
        assert metrics["total_words"] > 0
        
        assert "total_sentences" in metrics
        assert metrics["total_sentences"] > 0
        
        assert "avg_sentence_length" in metrics
        assert metrics["avg_sentence_length"] > 0
        
        assert "speaker_turns" in metrics
        assert metrics["speaker_turns"] > 0
        
        assert "participation_balance" in metrics
        assert 0 <= metrics["participation_balance"] <= 100
    
    def test_calculate_participation_balance(self):
        """Test calculating participation balance."""
        # Test with equal distribution
        speaking_time = {"Speaker1": 33.33, "Speaker2": 33.33, "Speaker3": 33.33}
        balance = self.analytics._calculate_participation_balance(speaking_time)
        assert 99.5 <= balance <= 100.0
        
        # Test with unequal distribution
        speaking_time = {"Speaker1": 80.0, "Speaker2": 15.0, "Speaker3": 5.0}
        balance = self.analytics._calculate_participation_balance(speaking_time)
        assert balance < 70.0
        
        # Test with empty dictionary
        speaking_time = {}
        balance = self.analytics._calculate_participation_balance(speaking_time)
        assert balance == 0.0
    
    def test_generate_improvement_suggestions(self):
        """Test generating improvement suggestions."""
        # Mock data
        speaking_time = {"John Smith": 60.0, "Jane Doe": 40.0}
        topics = [{"topic": "timeline", "relevance": 10.0, "mentions": 5}]
        efficiency_metrics = {
            "total_words": 200,
            "total_sentences": 20,
            "avg_sentence_length": 10.0,
            "speaker_turns": 10,
            "participation_balance": 80.0
        }
        
        # Generate suggestions
        suggestions = self.analytics._generate_improvement_suggestions(
            self.transcript, self.speakers, speaking_time, topics, efficiency_metrics
        )
        
        # Verify suggestions
        assert isinstance(suggestions, list)
        assert len(suggestions) > 0