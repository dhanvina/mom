"""
Unit tests for the enhanced MoMExtractor class.
"""

import pytest
from unittest.mock import patch, MagicMock
from app.extractor.mom_extractor import MoMExtractor

class TestEnhancedMoMExtractor:
    """Test cases for enhanced MoMExtractor class."""
    
    @patch('app.llm.ollama_manager.OllamaManager')
    def setup_method(self, _, mock_ollama_manager):
        """Set up test fixtures."""
        # Mock OllamaManager
        self.mock_ollama_manager_instance = MagicMock()
        mock_ollama_manager.return_value = self.mock_ollama_manager_instance
        
        # Create MoMExtractor instance
        self.extractor = MoMExtractor(model_name="test-model")
        
        # Sample transcript
        self.transcript = """
        John Smith: Good morning everyone. Let's start our weekly project meeting. Today is May 15, 2023, and it's 10:00 AM.
        
        Jane Doe: Good morning. I'd like to add a discussion about the new UI design to the agenda.
        
        John Smith: Sure, let's add that. So our agenda today is:
        1. Project status updates
        2. Budget review
        3. New UI design discussion
        4. Next steps
        
        Let's start with project status updates. Jane, can you give us an update?
        
        Jane Doe: Yes, we've completed the backend API development and are now working on frontend integration. We're on track to meet our June 1st deadline.
        
        John Smith: That's great news. Any blockers or issues?
        
        Jane Doe: We need to finalize the authentication flow. I suggest we use OAuth 2.0 with JWT tokens.
        
        Bob Johnson: I agree with Jane's suggestion. OAuth 2.0 is more secure and scalable.
        
        John Smith: Alright, let's decide on that. We'll use OAuth 2.0 with JWT tokens for authentication. Moving on to the budget review.
        
        Bob Johnson: We're currently under budget by about 10%. The cost-saving measures we implemented last month are working well.
        
        John Smith: Excellent. Let's discuss the new UI design now.
        
        Jane Doe: I've prepared some mockups based on user feedback. The main change is a simplified navigation menu and a more intuitive dashboard layout.
        
        John Smith: I like the direction. Bob, what do you think?
        
        Bob Johnson: It looks good, but I'm concerned about accessibility. We need to ensure the color contrast meets WCAG standards.
        
        Jane Doe: Good point. I'll work with the design team to address that.
        
        John Smith: Great. Jane, please update the mockups by Friday and share them with the team.
        
        Jane Doe: Will do.
        
        John Smith: For next steps, let's schedule a user testing session for the new UI next week. Bob, can you coordinate that?
        
        Bob Johnson: Yes, I'll set it up for Wednesday and send out invites.
        
        John Smith: Perfect. Any other items we need to discuss?
        
        Jane Doe: No, I think we've covered everything.
        
        John Smith: Alright then. Our next meeting will be next Monday at the same time. Thanks everyone!
        """
    
    def test_extract_with_enhanced_prompts(self):
        """Test extracting MoM data with enhanced prompts."""
        # Mock LLM response
        self.mock_ollama_manager_instance.generate.return_value = """
        {
          "meeting_title": "Weekly Project Meeting",
          "date_time": "2023-05-15 10:00 AM",
          "attendees": ["John Smith (Chair)", "Jane Doe", "Bob Johnson"],
          "agenda": ["Project status updates", "Budget review", "New UI design discussion", "Next steps"],
          "discussion_points": [
            {"topic": "Project status updates", "details": "Backend API development completed, working on frontend integration. On track for June 1st deadline.", "speakers": ["Jane Doe"]},
            {"topic": "Authentication flow", "details": "Decision to use OAuth 2.0 with JWT tokens.", "speakers": ["Jane Doe", "Bob Johnson"]},
            {"topic": "Budget review", "details": "Currently under budget by 10%. Cost-saving measures working well.", "speakers": ["Bob Johnson"]},
            {"topic": "New UI design", "details": "Mockups prepared with simplified navigation and intuitive dashboard. Concerns about accessibility and WCAG standards raised.", "speakers": ["Jane Doe", "Bob Johnson"]}
          ],
          "action_items": [
            {"description": "Update UI mockups to address accessibility concerns", "assignee": "Jane Doe", "deadline": "2023-05-19", "status": "pending"},
            {"description": "Coordinate user testing session for new UI", "assignee": "Bob Johnson", "deadline": "2023-05-24", "status": "pending"}
          ],
          "decisions": [
            {"decision": "Use OAuth 2.0 with JWT tokens for authentication", "context": "Discussion about authentication flow options", "proposed_by": "Jane Doe", "approved_by": ["John Smith", "Bob Johnson"], "unanimous": true}
          ],
          "next_steps": ["Schedule user testing session for the new UI next week"],
          "next_meeting": "Next Monday at the same time",
          "sentiment": {
            "overall": {"score": 0.8, "label": "Positive"},
            "topics": [
              {"topic": "Project status", "sentiment": "Positive"},
              {"topic": "UI design", "sentiment": "Neutral"}
            ]
          }
        }
        """
        
        # Test extraction with enhanced prompts
        result = self.extractor.extract(self.transcript, use_enhanced_prompts=True)
        
        # Verify LLM was called with enhanced prompt
        self.mock_ollama_manager_instance.generate.assert_called_once()
        
        # Verify result
        assert result["meeting_title"] == "Weekly Project Meeting"
        assert result["date_time"] == "2023-05-15 10:00 AM"
        assert len(result["attendees"]) == 3
        assert "John Smith (Chair)" in result["attendees"]
        assert len(result["agenda"]) == 4
        assert len(result["discussion_points"]) == 4
        assert len(result["action_items"]) == 2
        assert result["action_items"][0]["assignee"] == "Jane Doe"
        assert result["action_items"][0]["deadline"] == "2023-05-19"
        assert len(result["decisions"]) == 1
        assert result["decisions"][0]["proposed_by"] == "Jane Doe"
        assert "sentiment" in result
        assert result["sentiment"]["overall"]["label"] == "Positive"
    
    def test_extract_with_enhanced_structured_output(self):
        """Test extracting MoM data with enhanced structured output."""
        # Mock LLM response
        self.mock_ollama_manager_instance.generate.return_value = """
        {
          "meeting_title": "Weekly Project Meeting",
          "date_time": "2023-05-15 10:00 AM",
          "location": "Not specified",
          "attendees": [
            {"name": "John Smith", "role": "Chair", "is_chair": true},
            {"name": "Jane Doe", "role": "", "is_chair": false},
            {"name": "Bob Johnson", "role": "", "is_chair": false}
          ],
          "agenda": ["Project status updates", "Budget review", "New UI design discussion", "Next steps"],
          "discussion_points": [
            {
              "topic": "Project status updates", 
              "details": "Backend API development completed, working on frontend integration. On track for June 1st deadline.",
              "speakers": ["Jane Doe"],
              "concerns": []
            },
            {
              "topic": "Authentication flow", 
              "details": "Decision to use OAuth 2.0 with JWT tokens.",
              "speakers": ["Jane Doe", "Bob Johnson"],
              "concerns": []
            },
            {
              "topic": "Budget review", 
              "details": "Currently under budget by 10%. Cost-saving measures working well.",
              "speakers": ["Bob Johnson"],
              "concerns": []
            },
            {
              "topic": "New UI design", 
              "details": "Mockups prepared with simplified navigation and intuitive dashboard.",
              "speakers": ["Jane Doe", "Bob Johnson"],
              "concerns": ["Accessibility and WCAG standards compliance"]
            }
          ],
          "action_items": [
            {
              "description": "Update UI mockups to address accessibility concerns", 
              "assignee": "Jane Doe", 
              "deadline": "2023-05-19", 
              "priority": "High",
              "status": "pending"
            },
            {
              "description": "Coordinate user testing session for new UI", 
              "assignee": "Bob Johnson", 
              "deadline": "2023-05-24", 
              "priority": "Medium",
              "status": "pending"
            }
          ],
          "decisions": [
            {
              "decision": "Use OAuth 2.0 with JWT tokens for authentication", 
              "context": "Discussion about authentication flow options", 
              "proposed_by": "Jane Doe",
              "approved_by": ["John Smith", "Bob Johnson"],
              "unanimous": true,
              "objections": []
            }
          ],
          "next_steps": ["Schedule user testing session for the new UI next week"],
          "next_meeting": "Next Monday at the same time",
          "sentiment": {
            "overall": {"score": 0.8, "label": "Positive"},
            "topics": [
              {"topic": "Project status", "sentiment": "Positive"},
              {"topic": "UI design", "sentiment": "Neutral"}
            ],
            "participants": {
              "John Smith": {"score": 0.7, "label": "Positive"},
              "Jane Doe": {"score": 0.8, "label": "Positive"},
              "Bob Johnson": {"score": 0.6, "label": "Neutral"}
            }
          }
        }
        """
        
        # Test extraction with enhanced structured output
        result = self.extractor.extract(self.transcript, structured_output=True, use_enhanced_prompts=True)
        
        # Verify LLM was called with enhanced structured prompt
        self.mock_ollama_manager_instance.generate.assert_called_once()
        
        # Verify result
        assert result["meeting_title"] == "Weekly Project Meeting"
        assert result["date_time"] == "2023-05-15 10:00 AM"
        assert len(result["attendees"]) == 3
        assert result["attendees"][0]["name"] == "John Smith"
        assert result["attendees"][0]["is_chair"] == True
        assert len(result["agenda"]) == 4
        assert len(result["discussion_points"]) == 4
        assert "concerns" in result["discussion_points"][3]
        assert len(result["action_items"]) == 2
        assert "priority" in result["action_items"][0]
        assert result["action_items"][0]["priority"] == "High"
        assert len(result["decisions"]) == 1
        assert "proposed_by" in result["decisions"][0]
        assert "approved_by" in result["decisions"][0]
        assert "sentiment" in result
        assert "participants" in result["sentiment"]
    
    def test_extract_without_enhanced_prompts(self):
        """Test extracting MoM data without enhanced prompts."""
        # Mock LLM response
        self.mock_ollama_manager_instance.generate.return_value = """
        {
          "meeting_title": "Weekly Project Meeting",
          "date_time": "2023-05-15 10:00 AM",
          "attendees": ["John Smith", "Jane Doe", "Bob Johnson"],
          "agenda": ["Project status updates", "Budget review", "New UI design discussion", "Next steps"],
          "discussion_points": [
            {"topic": "Project status updates", "details": "Backend API development completed, working on frontend integration."},
            {"topic": "Budget review", "details": "Currently under budget by 10%."},
            {"topic": "New UI design", "details": "Mockups prepared with simplified navigation."}
          ],
          "action_items": [
            {"task": "Update UI mockups", "assignee": "Jane Doe", "due": "Friday"},
            {"task": "Coordinate user testing", "assignee": "Bob Johnson", "due": "Wednesday"}
          ],
          "decisions": [
            {"decision": "Use OAuth 2.0 with JWT tokens", "context": "Authentication flow discussion"}
          ],
          "next_steps": ["Schedule user testing session"]
        }
        """
        
        # Test extraction without enhanced prompts
        result = self.extractor.extract(self.transcript, structured_output=True, use_enhanced_prompts=False)
        
        # Verify LLM was called with standard prompt
        self.mock_ollama_manager_instance.generate.assert_called_once()
        
        # Verify result
        assert result["meeting_title"] == "Weekly Project Meeting"
        assert result["date_time"] == "2023-05-15 10:00 AM"
        assert len(result["attendees"]) == 3
        assert len(result["agenda"]) == 4
        assert len(result["discussion_points"]) == 3
        assert len(result["action_items"]) == 2
        assert "task" in result["action_items"][0]
        assert "due" in result["action_items"][0]
        assert len(result["decisions"]) == 1
        assert "decision" in result["decisions"][0]
        assert "context" in result["decisions"][0]
    
    def test_extract_with_language_detection(self):
        """Test extracting MoM data with language detection and enhanced prompts."""
        # Mock language detection
        with patch('app.multilingual.multilingual_manager.MultilingualManager.detect_language') as mock_detect_language:
            mock_detect_language.return_value = ("en", 0.95)
            
            # Mock LLM response
            self.mock_ollama_manager_instance.generate.return_value = '{"meeting_title": "Weekly Project Meeting"}'
            
            # Test extraction with language detection and enhanced prompts
            result = self.extractor.extract(self.transcript, use_enhanced_prompts=True)
            
            # Verify language detection was called
            mock_detect_language.assert_called_once_with(self.transcript)
            
            # Verify LLM was called with enhanced prompt
            self.mock_ollama_manager_instance.generate.assert_called_once()
            
            # Verify result
            assert result["meeting_title"] == "Weekly Project Meeting"