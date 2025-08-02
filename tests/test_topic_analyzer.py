"""
Unit tests for the TopicAnalyzer class.
"""

import pytest
from unittest.mock import patch, MagicMock
from app.analyzer.topic_analyzer import TopicAnalyzer

class TestTopicAnalyzer:
    """Test cases for TopicAnalyzer class."""
    
    def setup_method(self):
        """Set up test fixtures."""
        # Create analyzer with default config
        self.analyzer = TopicAnalyzer()
        
        # Create analyzer with LLM config
        self.llm_config = {"use_llm": True, "llm": {"model": "test-model"}}
        self.llm_analyzer = TopicAnalyzer(self.llm_config)
        
        # Test transcript
        self.transcript = """
        John: Good morning everyone. Let's start our project status meeting.
        Jane: Good morning. I've prepared the latest timeline for the mobile app development.
        John: Great. Let's also review the budget constraints for Q3.
        Jane: We might need to increase the budget for the next phase of development.
        John: I think that's reasonable. Let's approve that.
        Jane: Perfect. Now about the UI design, we need to finalize it by next week.
        Mark: I've been working on the UI mockups and should have them ready by Friday.
        Jane: That's great Mark. John, can you update the timeline by January 15th?
        John: Sure, I'll take care of it.
        Jane: Let's also discuss the API integration issues we've been having.
        Mark: Yes, we're having trouble with the payment gateway integration.
        John: Let's schedule a separate technical meeting to address those issues.
        Jane: Agreed. Let's schedule a follow-up meeting to review progress next week.
        John: Sounds good. Thanks everyone.
        """
    
    def test_preprocess_text(self):
        """Test preprocessing text for topic identification."""
        # Preprocess text
        tokens = self.analyzer._preprocess_text("Hello world! This is a test.")
        
        # Verify tokens
        assert "hello" in tokens
        assert "world" in tokens
        assert "test" in tokens
        assert "!" not in tokens  # Punctuation should be removed
        assert "is" not in tokens  # Stopwords should be removed
    
    def test_extract_keywords(self):
        """Test extracting keywords based on frequency."""
        # Extract keywords
        tokens = self.analyzer._preprocess_text(self.transcript)
        keywords = self.analyzer._extract_keywords(tokens)
        
        # Verify keywords
        assert len(keywords) > 0
        assert all(isinstance(keyword, dict) for keyword in keywords)
        assert all("topic" in keyword for keyword in keywords)
        assert all("relevance" in keyword for keyword in keywords)
        assert all("mentions" in keyword for keyword in keywords)
        assert all("type" in keyword for keyword in keywords)
        assert all(keyword["type"] == "keyword" for keyword in keywords)
    
    def test_extract_bigrams(self):
        """Test extracting bigrams as potential topics."""
        # Extract bigrams
        tokens = self.analyzer._preprocess_text(self.transcript)
        bigrams = self.analyzer._extract_bigrams(tokens)
        
        # Verify bigrams
        assert len(bigrams) >= 0  # May be empty if no significant bigrams found
        if bigrams:
            assert all(isinstance(bigram, dict) for bigram in bigrams)
            assert all("topic" in bigram for bigram in bigrams)
            assert all("relevance" in bigram for bigram in bigrams)
            assert all("mentions" in bigram for bigram in bigrams)
            assert all("type" in bigram for bigram in bigrams)
            assert all(bigram["type"] == "bigram" for bigram in bigrams)
            assert all(" " in bigram["topic"] for bigram in bigrams)  # Bigrams should contain a space
    
    @patch('sklearn.feature_extraction.text.TfidfVectorizer')
    @patch('sklearn.cluster.KMeans')
    def test_extract_tfidf_topics(self, mock_kmeans, mock_vectorizer):
        """Test extracting topics using TF-IDF and clustering."""
        # Mock vectorizer
        mock_vectorizer_instance = MagicMock()
        mock_vectorizer.return_value = mock_vectorizer_instance
        mock_vectorizer_instance.fit_transform.return_value = MagicMock()
        mock_vectorizer_instance.get_feature_names_out.return_value = ["project", "budget", "meeting", "timeline", "design"]
        
        # Mock KMeans
        mock_kmeans_instance = MagicMock()
        mock_kmeans.return_value = mock_kmeans_instance
        mock_kmeans_instance.cluster_centers_ = [[0.1, 0.2, 0.3, 0.4, 0.5], [0.5, 0.4, 0.3, 0.2, 0.1]]
        mock_kmeans_instance.labels_ = [0, 0, 1, 0, 1]
        
        # Extract TF-IDF topics
        sentences = self.transcript.split("\n")
        topics = self.analyzer._extract_tfidf_topics(sentences, 2)
        
        # Verify topics
        assert len(topics) == 2
        assert all(isinstance(topic, dict) for topic in topics)
        assert all("topic" in topic for topic in topics)
        assert all("relevance" in topic for topic in topics)
        assert all("mentions" in topic for topic in topics)
        assert all("type" in topic for topic in topics)
        assert all(topic["type"] == "cluster" for topic in topics)
        assert all("related_terms" in topic for topic in topics)
    
    @patch('app.analyzer.topic_analyzer.TopicAnalyzer._extract_llm_topics')
    def test_identify_topics_with_llm(self, mock_extract_llm_topics):
        """Test identifying topics with LLM."""
        # Mock LLM topics
        mock_llm_topics = [
            {
                "topic": "Budget Discussion",
                "relevance": 80,
                "mentions": 5,
                "type": "llm",
                "time_spent": "10 minutes"
            },
            {
                "topic": "UI Design",
                "relevance": 60,
                "mentions": 3,
                "type": "llm",
                "time_spent": "5 minutes"
            }
        ]
        mock_extract_llm_topics.return_value = mock_llm_topics
        
        # Identify topics
        topics = self.llm_analyzer.identify_topics(self.transcript, num_topics=3)
        
        # Verify topics
        assert len(topics) >= 2  # Should include at least the LLM topics
        assert any(topic["topic"] == "Budget Discussion" for topic in topics)
        assert any(topic["topic"] == "UI Design" for topic in topics)
        
        # Verify LLM topics are prioritized
        assert topics[0]["type"] == "llm"
        assert topics[1]["type"] == "llm"
    
    @patch('app.llm.llm_client.LLMClient')
    @patch('app.prompt.prompt_manager.PromptManager')
    def test_extract_llm_topics(self, mock_prompt_manager_class, mock_llm_client_class):
        """Test extracting topics using LLM."""
        # Mock LLM client
        mock_llm_client = MagicMock()
        mock_llm_client_class.return_value = mock_llm_client
        mock_llm_client.generate.return_value = """
        {
          "topics": [
            {
              "name": "Budget Constraints",
              "relevance": 80,
              "time_spent": "10 minutes",
              "frequency": 5,
              "key_participants": ["John", "Jane"],
              "summary": "Discussion about increasing the budget for the next phase",
              "related_decisions": ["Approved budget increase"],
              "related_action_items": []
            },
            {
              "name": "UI Design",
              "relevance": 60,
              "time_spent": "5 minutes",
              "frequency": 3,
              "key_participants": ["Mark", "Jane"],
              "summary": "Discussion about finalizing UI design by next week",
              "related_decisions": [],
              "related_action_items": ["Mark to prepare UI mockups by Friday"]
            },
            {
              "name": "API Integration",
              "relevance": 40,
              "time_spent": "3 minutes",
              "frequency": 2,
              "key_participants": ["Mark", "John", "Jane"],
              "summary": "Discussion about issues with payment gateway integration",
              "related_decisions": ["Schedule a separate technical meeting"],
              "related_action_items": []
            }
          ],
          "main_focus": "Budget Constraints",
          "underdiscussed_topics": ["API Integration"],
          "debate_topics": []
        }
        """
        
        # Mock prompt manager
        mock_prompt_manager = MagicMock()
        mock_prompt_manager_class.return_value = mock_prompt_manager
        mock_prompt_manager.get_prompt.return_value = "Test prompt template"
        mock_prompt_manager.format_prompt.return_value = "Formatted test prompt"
        
        # Extract LLM topics
        topics = self.llm_analyzer._extract_llm_topics(self.transcript, num_topics=3)
        
        # Verify topics
        assert len(topics) == 3
        assert topics[0]["topic"] == "Budget Constraints"
        assert topics[1]["topic"] == "UI Design"
        assert topics[2]["topic"] == "API Integration"
        assert topics[0]["relevance"] == 80
        assert topics[0]["time_spent"] == "10 minutes"
        assert topics[0]["mentions"] == 5
        assert topics[0]["type"] == "llm"
        assert "key_participants" in topics[0]
        assert "summary" in topics[0]
        assert "related_decisions" in topics[0]
        assert "related_action_items" in topics[0]
    
    def test_estimate_time_spent(self):
        """Test estimating time spent on each topic."""
        # Create topics
        topics = [
            {"topic": "budget", "relevance": 80},
            {"topic": "design", "relevance": 60}
        ]
        
        # Estimate time spent
        topics_with_time = self.analyzer._estimate_time_spent(topics, self.transcript)
        
        # Verify time spent
        assert len(topics_with_time) == 2
        assert all("time_spent" in topic for topic in topics_with_time)
        assert all("time_percentage" in topic for topic in topics_with_time)
    
    def test_identify_key_participants(self):
        """Test identifying key participants for each topic."""
        # Create topics
        topics = [
            {"topic": "budget", "relevance": 80},
            {"topic": "design", "relevance": 60}
        ]
        
        # Identify key participants
        topics_with_participants = self.analyzer._identify_key_participants(topics, self.transcript)
        
        # Verify key participants
        assert len(topics_with_participants) == 2
        assert all("key_participants" in topic for topic in topics_with_participants)
        
        # Budget topic should have John and Jane as participants
        budget_topic = next(topic for topic in topics_with_participants if topic["topic"] == "budget")
        assert "John" in budget_topic["key_participants"] or "Jane" in budget_topic["key_participants"]
        
        # Design topic should have Mark as a participant
        design_topic = next(topic for topic in topics_with_participants if topic["topic"] == "design")
        assert "Mark" in design_topic["key_participants"]
    
    def test_identify_related_topics(self):
        """Test identifying related topics."""
        # Create topics with context
        topics = [
            {
                "topic": "budget constraints",
                "relevance": 80,
                "context": ["We need to review the budget constraints for Q3.", 
                           "We might need to increase the budget for development."]
            },
            {
                "topic": "development phase",
                "relevance": 60,
                "context": ["We might need to increase the budget for the next phase of development.",
                           "The development phase needs to be completed on time."]
            },
            {
                "topic": "ui design",
                "relevance": 40,
                "context": ["We need to finalize the UI design by next week.",
                           "Mark has been working on the UI mockups."]
            }
        ]
        
        # Identify related topics
        topics_with_relations = self.analyzer._identify_related_topics(topics)
        
        # Verify related topics
        assert len(topics_with_relations) == 3
        assert all("related_topics" in topic for topic in topics_with_relations)
        
        # Budget and development should be related
        budget_topic = next(topic for topic in topics_with_relations if topic["topic"] == "budget constraints")
        assert "development phase" in budget_topic["related_topics"]
        
        # Development and budget should be related
        dev_topic = next(topic for topic in topics_with_relations if topic["topic"] == "development phase")
        assert "budget constraints" in dev_topic["related_topics"]
    
    def test_combine_topics(self):
        """Test combining topics from different extraction methods."""
        # Create topics from different methods
        keyword_topics = [
            {"topic": "budget", "relevance": 70, "mentions": 5, "type": "keyword"},
            {"topic": "design", "relevance": 50, "mentions": 3, "type": "keyword"}
        ]
        
        bigram_topics = [
            {"topic": "ui design", "relevance": 60, "mentions": 3, "type": "bigram"},
            {"topic": "project status", "relevance": 40, "mentions": 2, "type": "bigram"}
        ]
        
        tfidf_topics = [
            {"topic": "budget constraints", "relevance": 80, "mentions": 5, "type": "cluster"},
            {"topic": "api integration", "relevance": 40, "mentions": 2, "type": "cluster"}
        ]
        
        llm_topics = [
            {"topic": "Budget Constraints", "relevance": 85, "mentions": 5, "type": "llm"},
            {"topic": "UI Design", "relevance": 65, "mentions": 3, "type": "llm"}
        ]
        
        # Combine topics
        combined_topics = self.analyzer._combine_topics(keyword_topics, bigram_topics, tfidf_topics, llm_topics)
        
        # Verify combined topics
        assert len(combined_topics) >= 4  # Should have at least 4 unique topics
        
        # Verify LLM topics are prioritized
        assert combined_topics[0]["type"] == "llm"
        assert combined_topics[1]["type"] == "llm"
        
        # Verify topics are sorted by relevance
        relevance_values = [topic["relevance"] for topic in combined_topics]
        assert all(relevance_values[i] >= relevance_values[i+1] for i in range(len(relevance_values)-1))
        
        # Verify duplicate topics are removed (case-insensitive)
        topic_names = [topic["topic"].lower() for topic in combined_topics]
        assert len(topic_names) == len(set(topic_names))
    
    def test_generate_topic_distribution(self):
        """Test generating topic distribution data for visualization."""
        # Create topics
        topics = [
            {"topic": "Budget", "relevance": 80},
            {"topic": "Design", "relevance": 60},
            {"topic": "API", "relevance": 40}
        ]
        
        # Generate distribution
        distribution = self.analyzer.generate_topic_distribution(topics)
        
        # Verify distribution
        assert len(distribution) == 3
        assert "Budget" in distribution
        assert "Design" in distribution
        assert "API" in distribution
        assert abs(sum(distribution.values()) - 100) < 0.01  # Should sum to approximately 100%
        assert distribution["Budget"] > distribution["Design"] > distribution["API"]  # Should maintain relative proportions