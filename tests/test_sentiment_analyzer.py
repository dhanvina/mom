"""
Unit tests for the SentimentAnalyzer class.
"""

import pytest
from unittest.mock import patch, MagicMock
from app.analyzer.sentiment_analyzer import SentimentAnalyzer

class TestSentimentAnalyzer:
    """Test cases for SentimentAnalyzer class."""
    
    def setup_method(self):
        """Set up test fixtures."""
        self.analyzer = SentimentAnalyzer()
        
        # Create a test transcript
        self.transcript = """
John Smith: Good morning everyone. I'm really excited about our progress on the project.
Jane Doe: Thanks John. I've prepared a presentation on our achievements.
John Smith: Great, let's start with the current status.
Jane Doe: We've successfully completed the first phase ahead of schedule.
John Smith: That's excellent news! What challenges are we facing?
Jane Doe: Unfortunately, we have some resource allocation issues. We need more developers.
John Smith: I'm concerned about that. I'll talk to the resource manager about getting more help.
Jane Doe: That would be great. We also need to discuss the budget constraints.
John Smith: I'm afraid we might have to cut some features due to the limited budget.
Jane Doe: I understand, but I'm confident we can still deliver a quality product.
John Smith: I appreciate your optimism. Let's focus on the timeline.
Jane Doe: Despite the challenges, we're still on track to meet the deadline.
John Smith: That's reassuring. Any other concerns?
Jane Doe: No, that's all from my side.
John Smith: Excellent. Let's summarize the action items.
Jane Doe: Action item for John: Talk to resource manager about additional developers.
John Smith: Action item for both of us: Prepare for the budget meeting next week.
Jane Doe: I'm looking forward to our next meeting. Thank you everyone.
        """.strip()
        
        # Define speakers
        self.speakers = ["John Smith", "Jane Doe"]
    
    def test_init(self):
        """Test initialization with default and custom config."""
        # Default config
        analyzer = SentimentAnalyzer()
        assert analyzer.config == {}
        
        # Custom config
        custom_config = {"threshold": 0.5}
        analyzer = SentimentAnalyzer(config=custom_config)
        assert analyzer.config == custom_config
    
    def test_analyze(self):
        """Test analyzing sentiment in a transcript."""
        # Analyze sentiment
        sentiment = self.analyzer.analyze(self.transcript, self.speakers)
        
        # Verify sentiment structure
        assert "overall" in sentiment
        assert "speakers" in sentiment
        assert "temporal" in sentiment
        assert "topics" in sentiment
        
        # Verify overall sentiment
        assert "compound" in sentiment["overall"]
        assert "positive" in sentiment["overall"]
        assert "neutral" in sentiment["overall"]
        assert "negative" in sentiment["overall"]
        assert "label" in sentiment["overall"]
        assert "confidence" in sentiment["overall"]
        
        # Verify speaker sentiment
        assert "John Smith" in sentiment["speakers"]
        assert "Jane Doe" in sentiment["speakers"]
        
        # Verify temporal sentiment
        assert isinstance(sentiment["temporal"], list)
        assert len(sentiment["temporal"]) > 0
        
        # Verify topic sentiment
        assert isinstance(sentiment["topics"], dict)
    
    def test_analyze_overall_sentiment(self):
        """Test analyzing overall sentiment."""
        # Analyze overall sentiment
        overall = self.analyzer._analyze_overall_sentiment(self.transcript)
        
        # Verify overall sentiment
        assert "compound" in overall
        assert "positive" in overall
        assert "neutral" in overall
        assert "negative" in overall
        assert "label" in overall
        assert "confidence" in overall
        
        # Verify sentiment scores are in valid range
        assert -1.0 <= overall["compound"] <= 1.0
        assert 0.0 <= overall["positive"] <= 1.0
        assert 0.0 <= overall["neutral"] <= 1.0
        assert 0.0 <= overall["negative"] <= 1.0
        assert 0.0 <= overall["confidence"] <= 1.0
        
        # Verify sentiment label is valid
        assert overall["label"] in ["positive", "neutral", "negative"]
    
    def test_analyze_speaker_sentiment(self):
        """Test analyzing sentiment by speaker."""
        # Analyze speaker sentiment
        speaker_sentiment = self.analyzer._analyze_speaker_sentiment(self.transcript, self.speakers)
        
        # Verify speaker sentiment
        assert "John Smith" in speaker_sentiment
        assert "Jane Doe" in speaker_sentiment
        
        # Verify sentiment scores for each speaker
        for speaker, scores in speaker_sentiment.items():
            assert "compound" in scores
            assert "positive" in scores
            assert "neutral" in scores
            assert "negative" in scores
            assert "label" in scores
            assert "confidence" in scores
            
            # Verify sentiment scores are in valid range
            assert -1.0 <= scores["compound"] <= 1.0
            assert 0.0 <= scores["positive"] <= 1.0
            assert 0.0 <= scores["neutral"] <= 1.0
            assert 0.0 <= scores["negative"] <= 1.0
            assert 0.0 <= scores["confidence"] <= 1.0
            
            # Verify sentiment label is valid
            assert scores["label"] in ["positive", "neutral", "negative"]
    
    def test_analyze_temporal_sentiment(self):
        """Test analyzing sentiment over time."""
        # Analyze temporal sentiment
        temporal_sentiment = self.analyzer._analyze_temporal_sentiment(self.transcript)
        
        # Verify temporal sentiment
        assert isinstance(temporal_sentiment, list)
        assert len(temporal_sentiment) > 0
        
        # Verify sentiment scores for each time point
        for item in temporal_sentiment:
            assert "index" in item
            assert "text" in item
            assert "compound" in item
            assert "positive" in item
            assert "neutral" in item
            assert "negative" in item
            assert "label" in item
            assert "confidence" in item
            
            # Verify sentiment scores are in valid range
            assert -1.0 <= item["compound"] <= 1.0
            assert 0.0 <= item["positive"] <= 1.0
            assert 0.0 <= item["neutral"] <= 1.0
            assert 0.0 <= item["negative"] <= 1.0
            assert 0.0 <= item["confidence"] <= 1.0
            
            # Verify sentiment label is valid
            assert item["label"] in ["positive", "neutral", "negative"]
    
    def test_analyze_topic_sentiment(self):
        """Test analyzing sentiment by topic."""
        # Analyze topic sentiment
        topic_sentiment = self.analyzer._analyze_topic_sentiment(self.transcript)
        
        # Verify topic sentiment
        assert isinstance(topic_sentiment, dict)
        
        # Verify sentiment scores for each topic
        for topic, scores in topic_sentiment.items():
            assert "compound" in scores
            assert "positive" in scores
            assert "neutral" in scores
            assert "negative" in scores
            assert "label" in scores
            assert "confidence" in scores
            
            # Verify sentiment scores are in valid range
            assert -1.0 <= scores["compound"] <= 1.0
            assert 0.0 <= scores["positive"] <= 1.0
            assert 0.0 <= scores["neutral"] <= 1.0
            assert 0.0 <= scores["negative"] <= 1.0
            assert 0.0 <= scores["confidence"] <= 1.0
            
            # Verify sentiment label is valid
            assert scores["label"] in ["positive", "neutral", "negative"]
    
    def test_extract_topics(self):
        """Test extracting topics from a transcript."""
        # Extract topics
        topics = self.analyzer._extract_topics(self.transcript)
        
        # Verify topics
        assert isinstance(topics, dict)
        
        # Verify common topics are extracted
        common_topics = ["budget", "project", "resource"]
        for topic in common_topics:
            assert any(topic in t for t in topics.keys())
        
        # Verify each topic has associated sentences
        for topic, sentences in topics.items():
            assert isinstance(sentences, list)
            assert len(sentences) > 0
            assert all(isinstance(s, str) for s in sentences)
    
    def test_get_sentiment_label(self):
        """Test getting sentiment label and confidence from scores."""
        # Test positive sentiment
        scores = {"compound": 0.5, "pos": 0.6, "neu": 0.3, "neg": 0.1}
        label, confidence = self.analyzer._get_sentiment_label(scores)
        assert label == "positive"
        assert 0.0 <= confidence <= 1.0
        
        # Test negative sentiment
        scores = {"compound": -0.5, "pos": 0.1, "neu": 0.3, "neg": 0.6}
        label, confidence = self.analyzer._get_sentiment_label(scores)
        assert label == "negative"
        assert 0.0 <= confidence <= 1.0
        
        # Test neutral sentiment
        scores = {"compound": 0.0, "pos": 0.3, "neu": 0.6, "neg": 0.1}
        label, confidence = self.analyzer._get_sentiment_label(scores)
        assert label == "neutral"
        assert 0.0 <= confidence <= 1.0
    
    def test_get_sentiment_summary(self):
        """Test generating a sentiment summary."""
        # Create test sentiment data
        sentiment = {
            "overall": {
                "compound": 0.2,
                "positive": 0.4,
                "neutral": 0.5,
                "negative": 0.1,
                "label": "positive",
                "confidence": 0.8
            },
            "speakers": {
                "John Smith": {
                    "compound": 0.3,
                    "positive": 0.5,
                    "neutral": 0.4,
                    "negative": 0.1,
                    "label": "positive",
                    "confidence": 0.9
                },
                "Jane Doe": {
                    "compound": 0.1,
                    "positive": 0.3,
                    "neutral": 0.5,
                    "negative": 0.2,
                    "label": "positive",
                    "confidence": 0.7
                }
            },
            "temporal": [
                {"index": 0, "compound": 0.1, "positive": 0.3, "neutral": 0.6, "negative": 0.1, "label": "positive", "confidence": 0.6},
                {"index": 1, "compound": 0.2, "positive": 0.4, "neutral": 0.5, "negative": 0.1, "label": "positive", "confidence": 0.7},
                {"index": 2, "compound": 0.3, "positive": 0.5, "neutral": 0.4, "negative": 0.1, "label": "positive", "confidence": 0.8}
            ],
            "topics": {
                "project": {
                    "compound": 0.4,
                    "positive": 0.6,
                    "neutral": 0.3,
                    "negative": 0.1,
                    "label": "positive",
                    "confidence": 0.9
                },
                "budget": {
                    "compound": -0.2,
                    "positive": 0.2,
                    "neutral": 0.4,
                    "negative": 0.4,
                    "label": "negative",
                    "confidence": 0.8
                }
            }
        }
        
        # Generate sentiment summary
        summary = self.analyzer.get_sentiment_summary(sentiment)
        
        # Verify summary structure
        assert "overall_sentiment" in summary
        assert "overall_confidence" in summary
        assert "sentiment_trend" in summary
        assert "most_positive_speaker" in summary
        assert "most_negative_speaker" in summary
        assert "most_positive_topic" in summary
        assert "most_negative_topic" in summary
        
        # Verify summary values
        assert summary["overall_sentiment"] == "positive"
        assert summary["overall_confidence"] == 0.8
        assert summary["most_positive_speaker"] == "John Smith"
        assert summary["most_negative_speaker"] == "Jane Doe"
        assert summary["most_positive_topic"] == "project"
        assert summary["most_negative_topic"] == "budget"
    
    def test_visualize_sentiment_overall(self):
        """Test creating visualization data for overall sentiment."""
        # Create test sentiment data
        sentiment = {
            "overall": {
                "compound": 0.2,
                "positive": 0.4,
                "neutral": 0.5,
                "negative": 0.1,
                "label": "positive",
                "confidence": 0.8
            },
            "speakers": {},
            "temporal": [],
            "topics": {}
        }
        
        # Create visualization data
        data = self.analyzer.visualize_sentiment(sentiment, "overall")
        
        # Verify data structure
        assert "labels" in data
        assert "values" in data
        assert data["labels"] == ["Positive", "Neutral", "Negative"]
        assert data["values"] == [0.4, 0.5, 0.1]
    
    def test_visualize_sentiment_speakers(self):
        """Test creating visualization data for speaker sentiment."""
        # Create test sentiment data
        sentiment = {
            "overall": {},
            "speakers": {
                "John Smith": {
                    "compound": 0.3,
                    "positive": 0.5,
                    "neutral": 0.4,
                    "negative": 0.1,
                    "label": "positive",
                    "confidence": 0.9
                },
                "Jane Doe": {
                    "compound": 0.1,
                    "positive": 0.3,
                    "neutral": 0.5,
                    "negative": 0.2,
                    "label": "positive",
                    "confidence": 0.7
                }
            },
            "temporal": [],
            "topics": {}
        }
        
        # Create visualization data
        data = self.analyzer.visualize_sentiment(sentiment, "speakers")
        
        # Verify data structure
        assert "labels" in data
        assert "positive" in data
        assert "neutral" in data
        assert "negative" in data
        assert data["labels"] == ["John Smith", "Jane Doe"]
        assert data["positive"] == [0.5, 0.3]
        assert data["neutral"] == [0.4, 0.5]
        assert data["negative"] == [0.1, 0.2]
    
    def test_visualize_sentiment_unsupported(self):
        """Test creating visualization data for unsupported type."""
        # Create test sentiment data
        sentiment = {
            "overall": {},
            "speakers": {},
            "temporal": [],
            "topics": {}
        }
        
        # Create visualization data
        data = self.analyzer.visualize_sentiment(sentiment, "unsupported")
        
        # Verify data is empty
        assert data == {}