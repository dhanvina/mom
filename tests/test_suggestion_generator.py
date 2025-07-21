"""
Unit tests for the SuggestionGenerator class.
"""

import pytest
from unittest.mock import patch, MagicMock
from app.analyzer.suggestion_generator import SuggestionGenerator

class TestSuggestionGenerator:
    """Test cases for SuggestionGenerator class."""
    
    def setup_method(self):
        """Set up test fixtures."""
        self.generator = SuggestionGenerator()
        
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
        
        # Create test analytics
        self.analytics = {
            "efficiency_metrics": {
                "has_agenda": False,
                "has_summary": True,
                "participation_balance": 80.0,
                "engagement_score": 70.0,
                "speaking_percentages": {
                    "John Smith": 55.0,
                    "Jane Doe": 45.0
                },
                "action_items": 2,
                "decisions": 1,
                "content_density": 60.0,
                "avg_sentence_length": 15.0,
                "time_efficiency": 75.0,
                "words_per_minute": 120.0,
                "optimal_duration": 20.0,
                "duration_minutes": 30.0
            },
            "topics": [
                {"topic": "project timeline", "relevance": 10.0},
                {"topic": "resource allocation", "relevance": 8.0},
                {"topic": "budget discussion", "relevance": 6.0},
                {"topic": "action items", "relevance": 4.0}
            ]
        }
    
    def test_init(self):
        """Test initialization with default and custom config."""
        # Default config
        generator = SuggestionGenerator()
        assert generator.config == {}
        
        # Custom config
        custom_config = {"threshold": 0.5}
        generator = SuggestionGenerator(config=custom_config)
        assert generator.config == custom_config
    
    def test_generate_suggestions(self):
        """Test generating meeting improvement suggestions."""
        # Generate suggestions
        suggestions = self.generator.generate_suggestions(self.transcript, self.analytics)
        
        # Verify suggestions
        assert isinstance(suggestions, list)
        assert len(suggestions) > 0
        
        # Verify suggestion structure
        for suggestion in suggestions:
            assert "category" in suggestion
            assert "suggestion" in suggestion
            assert "reason" in suggestion
            assert "benefit" in suggestion
            assert "priority" in suggestion
    
    def test_generate_structure_suggestions(self):
        """Test generating structure-related suggestions."""
        # Generate structure suggestions
        suggestions = self.generator._generate_structure_suggestions(self.transcript, self.analytics)
        
        # Verify suggestions
        assert isinstance(suggestions, list)
        
        # Verify suggestion structure
        for suggestion in suggestions:
            assert "category" in suggestion
            assert suggestion["category"] == "structure"
            assert "suggestion" in suggestion
            assert "reason" in suggestion
            assert "benefit" in suggestion
    
    def test_generate_participation_suggestions(self):
        """Test generating participation-related suggestions."""
        # Generate participation suggestions
        suggestions = self.generator._generate_participation_suggestions(self.analytics)
        
        # Verify suggestions
        assert isinstance(suggestions, list)
        
        # Verify suggestion structure
        for suggestion in suggestions:
            assert "category" in suggestion
            assert suggestion["category"] == "participation"
            assert "suggestion" in suggestion
            assert "reason" in suggestion
            assert "benefit" in suggestion
    
    def test_generate_content_suggestions(self):
        """Test generating content-related suggestions."""
        # Generate content suggestions
        suggestions = self.generator._generate_content_suggestions(self.analytics)
        
        # Verify suggestions
        assert isinstance(suggestions, list)
        
        # Verify suggestion structure
        for suggestion in suggestions:
            assert "category" in suggestion
            assert suggestion["category"] == "content"
            assert "suggestion" in suggestion
            assert "reason" in suggestion
            assert "benefit" in suggestion
    
    def test_generate_time_suggestions(self):
        """Test generating time-related suggestions."""
        # Generate time suggestions
        suggestions = self.generator._generate_time_suggestions(self.analytics)
        
        # Verify suggestions
        assert isinstance(suggestions, list)
        
        # Verify suggestion structure
        for suggestion in suggestions:
            assert "category" in suggestion
            assert suggestion["category"] == "time"
            assert "suggestion" in suggestion
            assert "reason" in suggestion
            assert "benefit" in suggestion
    
    def test_generate_followup_suggestions(self):
        """Test generating follow-up-related suggestions."""
        # Generate followup suggestions
        suggestions = self.generator._generate_followup_suggestions(self.transcript, self.analytics)
        
        # Verify suggestions
        assert isinstance(suggestions, list)
        
        # Verify suggestion structure
        for suggestion in suggestions:
            assert "category" in suggestion
            assert suggestion["category"] == "followup"
            assert "suggestion" in suggestion
            assert "reason" in suggestion
            assert "benefit" in suggestion
    
    def test_prioritize_suggestions(self):
        """Test prioritizing suggestions."""
        # Create test suggestions
        suggestions = [
            {"category": "followup", "suggestion": "Test followup suggestion", "reason": "Test reason", "benefit": "Test benefit"},
            {"category": "structure", "suggestion": "Test structure suggestion", "reason": "Test reason", "benefit": "Test benefit"},
            {"category": "content", "suggestion": "Test content suggestion", "reason": "Test reason", "benefit": "Test benefit"}
        ]
        
        # Prioritize suggestions
        prioritized = self.generator._prioritize_suggestions(suggestions)
        
        # Verify priorities
        assert prioritized[0]["priority"] < prioritized[1]["priority"]
        assert prioritized[1]["priority"] < prioritized[2]["priority"]
    
    def test_generate_personalized_suggestions(self):
        """Test generating personalized suggestions."""
        # Create user preferences
        user_preferences = {
            "preferred_categories": ["structure", "content"],
            "max_suggestions": 2
        }
        
        # Generate personalized suggestions
        suggestions = self.generator.generate_personalized_suggestions(
            self.transcript, self.analytics, user_preferences
        )
        
        # Verify suggestions
        assert isinstance(suggestions, list)
        assert len(suggestions) <= 2
        
        # Verify categories
        for suggestion in suggestions:
            assert suggestion["category"] in user_preferences["preferred_categories"]