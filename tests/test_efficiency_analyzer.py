"""
Unit tests for the EfficiencyAnalyzer class.
"""

import pytest
from unittest.mock import patch, MagicMock
from app.analyzer.efficiency_analyzer import EfficiencyAnalyzer

class TestEfficiencyAnalyzer:
    """Test cases for EfficiencyAnalyzer class."""
    
    def setup_method(self):
        """Set up test fixtures."""
        self.analyzer = EfficiencyAnalyzer()
        
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
        analyzer = EfficiencyAnalyzer()
        assert analyzer.config == {}
        
        # Custom config
        custom_config = {"threshold": 0.5}
        analyzer = EfficiencyAnalyzer(config=custom_config)
        assert analyzer.config == custom_config
    
    def test_calculate_metrics(self):
        """Test calculating meeting efficiency metrics."""
        # Calculate metrics
        metrics = self.analyzer.calculate_metrics(
            self.transcript, self.speakers, start_time="09:00", end_time="09:30"
        )
        
        # Verify metrics structure
        assert "total_words" in metrics
        assert "total_sentences" in metrics
        assert "avg_sentence_length" in metrics
        assert "speaker_turns" in metrics
        assert "speaker_turn_rate" in metrics
        assert "duration_minutes" in metrics
        assert "words_per_minute" in metrics
        assert "optimal_duration" in metrics
        assert "time_efficiency" in metrics
        assert "action_items" in metrics
        assert "decisions" in metrics
        assert "has_agenda" in metrics
        assert "has_summary" in metrics
        assert "content_structure_score" in metrics
        assert "content_density" in metrics
        assert "speaking_percentages" in metrics
        assert "participation_balance" in metrics
        assert "engagement_score" in metrics
        assert "efficiency_score" in metrics
    
    def test_calculate_basic_metrics(self):
        """Test calculating basic meeting metrics."""
        # Calculate basic metrics
        metrics = self.analyzer._calculate_basic_metrics(self.transcript, self.speakers)
        
        # Verify metrics
        assert "total_words" in metrics
        assert metrics["total_words"] > 0
        
        assert "total_sentences" in metrics
        assert metrics["total_sentences"] > 0
        
        assert "avg_sentence_length" in metrics
        assert metrics["avg_sentence_length"] > 0
        
        assert "speaker_turns" in metrics
        assert metrics["speaker_turns"] > 0
        
        assert "speaker_turn_rate" in metrics
        assert metrics["speaker_turn_rate"] > 0
    
    def test_calculate_time_metrics(self):
        """Test calculating time-based meeting metrics."""
        # Calculate time metrics
        metrics = self.analyzer._calculate_time_metrics(self.transcript, "09:00", "09:30")
        
        # Verify metrics
        assert "duration_minutes" in metrics
        assert metrics["duration_minutes"] == 30
        
        assert "words_per_minute" in metrics
        assert metrics["words_per_minute"] > 0
        
        assert "optimal_duration" in metrics
        assert metrics["optimal_duration"] > 0
        
        assert "time_efficiency" in metrics
        assert 0 <= metrics["time_efficiency"] <= 100
    
    def test_calculate_time_metrics_invalid_format(self):
        """Test calculating time metrics with invalid time format."""
        # Calculate time metrics with invalid format
        metrics = self.analyzer._calculate_time_metrics(self.transcript, "9:00", "9:30")
        
        # Verify empty metrics
        assert metrics == {}
    
    def test_calculate_content_metrics(self):
        """Test calculating content-based meeting metrics."""
        # Calculate content metrics
        metrics = self.analyzer._calculate_content_metrics(self.transcript)
        
        # Verify metrics
        assert "action_items" in metrics
        assert metrics["action_items"] > 0
        
        assert "decisions" in metrics
        
        assert "has_agenda" in metrics
        assert isinstance(metrics["has_agenda"], bool)
        
        assert "has_summary" in metrics
        assert isinstance(metrics["has_summary"], bool)
        
        assert "content_structure_score" in metrics
        assert 0 <= metrics["content_structure_score"] <= 100
        
        assert "content_density" in metrics
        assert 0 <= metrics["content_density"] <= 100
    
    def test_calculate_participation_metrics(self):
        """Test calculating participation-based meeting metrics."""
        # Calculate participation metrics
        metrics = self.analyzer._calculate_participation_metrics(self.transcript, self.speakers)
        
        # Verify metrics
        assert "speaking_percentages" in metrics
        assert "John Smith" in metrics["speaking_percentages"]
        assert "Jane Doe" in metrics["speaking_percentages"]
        
        assert "participation_balance" in metrics
        assert 0 <= metrics["participation_balance"] <= 100
        
        assert "engagement_score" in metrics
        assert 0 <= metrics["engagement_score"] <= 100
    
    def test_calculate_participation_balance(self):
        """Test calculating participation balance."""
        # Test with equal distribution
        speaking_percentages = {"Speaker1": 33.33, "Speaker2": 33.33, "Speaker3": 33.33}
        balance = self.analyzer._calculate_participation_balance(speaking_percentages)
        assert 99.5 <= balance <= 100.0
        
        # Test with unequal distribution
        speaking_percentages = {"Speaker1": 80.0, "Speaker2": 15.0, "Speaker3": 5.0}
        balance = self.analyzer._calculate_participation_balance(speaking_percentages)
        assert balance < 70.0
        
        # Test with empty dictionary
        speaking_percentages = {}
        balance = self.analyzer._calculate_participation_balance(speaking_percentages)
        assert balance == 0.0
    
    def test_calculate_engagement_score(self):
        """Test calculating engagement score."""
        # Calculate engagement score
        score = self.analyzer._calculate_engagement_score(self.transcript, self.speakers)
        
        # Verify score
        assert 0 <= score <= 100
    
    def test_calculate_efficiency_score(self):
        """Test calculating overall efficiency score."""
        # Create test metrics
        basic_metrics = {
            "total_words": 200,
            "total_sentences": 20,
            "avg_sentence_length": 10.0,
            "speaker_turns": 10,
            "speaker_turn_rate": 0.5
        }
        
        time_metrics = {
            "duration_minutes": 30,
            "words_per_minute": 6.67,
            "optimal_duration": 1.6,
            "time_efficiency": 80.0
        }
        
        content_metrics = {
            "action_items": 2,
            "decisions": 1,
            "has_agenda": True,
            "has_summary": True,
            "content_structure_score": 100.0,
            "content_density": 70.0
        }
        
        participation_metrics = {
            "speaking_percentages": {"John Smith": 50.0, "Jane Doe": 50.0},
            "participation_balance": 100.0,
            "engagement_score": 85.0
        }
        
        # Calculate efficiency score
        score = self.analyzer._calculate_efficiency_score(
            basic_metrics, time_metrics, content_metrics, participation_metrics
        )
        
        # Verify score
        assert 0 <= score <= 100
    
    def test_compare_with_past_meetings(self):
        """Test comparing with past meetings."""
        # Create current metrics
        current_metrics = {
            "total_words": 200,
            "total_sentences": 20,
            "efficiency_score": 85.0
        }
        
        # Create past metrics
        past_metrics = [
            {
                "total_words": 180,
                "total_sentences": 18,
                "efficiency_score": 80.0
            },
            {
                "total_words": 220,
                "total_sentences": 22,
                "efficiency_score": 75.0
            }
        ]
        
        # Compare with past meetings
        comparison = self.analyzer.compare_with_past_meetings(current_metrics, past_metrics)
        
        # Verify comparison
        assert "avg_past_metrics" in comparison
        assert "changes" in comparison
        assert "improvements" in comparison
        assert "regressions" in comparison
        
        # Verify average metrics
        assert comparison["avg_past_metrics"]["total_words"] == 200
        assert comparison["avg_past_metrics"]["total_sentences"] == 20
        assert comparison["avg_past_metrics"]["efficiency_score"] == 77.5
        
        # Verify changes
        assert "efficiency_score" in comparison["changes"]
        assert comparison["changes"]["efficiency_score"] > 0
        
        # Verify improvements
        assert "efficiency_score" in comparison["improvements"]
    
    def test_compare_with_no_past_meetings(self):
        """Test comparing with no past meetings."""
        # Create current metrics
        current_metrics = {
            "total_words": 200,
            "total_sentences": 20,
            "efficiency_score": 85.0
        }
        
        # Compare with no past meetings
        comparison = self.analyzer.compare_with_past_meetings(current_metrics, [])
        
        # Verify comparison
        assert comparison == {"comparison": "No past meetings to compare with"}