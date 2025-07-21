"""
Suggestion generator module for AI-powered MoM generator.

This module provides functionality for generating meeting improvement suggestions.
"""

import logging
from typing import Dict, Any, Optional, List, Tuple

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class SuggestionGenerator:
    """
    Generates meeting improvement suggestions.
    
    This class provides methods for generating suggestions to improve future meetings
    based on meeting analytics.
    
    Attributes:
        config (Dict): Configuration options for the generator
    """
    
    def __init__(self, config: Optional[Dict[str, Any]] = None):
        """
        Initialize the SuggestionGenerator with optional configuration.
        
        Args:
            config (Dict, optional): Configuration options for the generator
        """
        self.config = config or {}
        logger.info("SuggestionGenerator initialized")
    
    def generate_suggestions(self, transcript: str, analytics: Dict[str, Any]) -> List[Dict[str, Any]]:
        """
        Generate meeting improvement suggestions based on analytics.
        
        Args:
            transcript (str): Meeting transcript
            analytics (Dict[str, Any]): Meeting analytics
            
        Returns:
            List[Dict[str, Any]]: List of improvement suggestions
        """
        suggestions = []
        
        # Generate structure suggestions
        structure_suggestions = self._generate_structure_suggestions(transcript, analytics)
        suggestions.extend(structure_suggestions)
        
        # Generate participation suggestions
        participation_suggestions = self._generate_participation_suggestions(analytics)
        suggestions.extend(participation_suggestions)
        
        # Generate content suggestions
        content_suggestions = self._generate_content_suggestions(analytics)
        suggestions.extend(content_suggestions)
        
        # Generate time management suggestions
        time_suggestions = self._generate_time_suggestions(analytics)
        suggestions.extend(time_suggestions)
        
        # Generate follow-up suggestions
        followup_suggestions = self._generate_followup_suggestions(transcript, analytics)
        suggestions.extend(followup_suggestions)
        
        # Add priority levels to suggestions
        suggestions = self._prioritize_suggestions(suggestions)
        
        # Sort suggestions by priority
        suggestions.sort(key=lambda x: x["priority"])
        
        return suggestions
    
    def _generate_structure_suggestions(self, transcript: str, analytics: Dict[str, Any]) -> List[Dict[str, Any]]:
        """
        Generate suggestions related to meeting structure.
        
        Args:
            transcript (str): Meeting transcript
            analytics (Dict[str, Any]): Meeting analytics
            
        Returns:
            List[Dict[str, Any]]: List of structure-related suggestions
        """
        suggestions = []
        
        # Check for agenda
        if not analytics["efficiency_metrics"].get("has_agenda", False):
            suggestions.append({
                "category": "structure",
                "suggestion": "Start meetings with a clear agenda to keep discussions focused and on track.",
                "reason": "No clear agenda was detected in the meeting transcript.",
                "benefit": "A well-structured agenda helps participants prepare and ensures all important topics are covered."
            })
        
        # Check for summary
        if not analytics["efficiency_metrics"].get("has_summary", False):
            suggestions.append({
                "category": "structure",
                "suggestion": "End meetings with a summary of key points and action items.",
                "reason": "No clear summary was detected at the end of the meeting.",
                "benefit": "Summaries ensure everyone leaves with the same understanding of what was discussed and what needs to be done."
            })
        
        # Check for topic focus
        topics = analytics.get("topics", [])
        if len(topics) > 7:
            suggestions.append({
                "category": "structure",
                "suggestion": "Focus on fewer topics per meeting for more in-depth discussion.",
                "reason": f"The meeting covered {len(topics)} different topics, which may be too many for a single meeting.",
                "benefit": "Focusing on fewer topics allows for more thorough discussion and better outcomes."
            })
        
        return suggestions
    
    def _generate_participation_suggestions(self, analytics: Dict[str, Any]) -> List[Dict[str, Any]]:
        """
        Generate suggestions related to participant engagement.
        
        Args:
            analytics (Dict[str, Any]): Meeting analytics
            
        Returns:
            List[Dict[str, Any]]: List of participation-related suggestions
        """
        suggestions = []
        
        # Check participation balance
        balance_score = analytics["efficiency_metrics"].get("participation_balance", 0)
        if balance_score < 70:
            suggestions.append({
                "category": "participation",
                "suggestion": "Encourage more balanced participation among attendees.",
                "reason": "Some participants dominated the conversation while others had limited input.",
                "benefit": "Balanced participation ensures all perspectives are heard and increases engagement."
            })
        
        # Check engagement score
        engagement_score = analytics["efficiency_metrics"].get("engagement_score", 0)
        if engagement_score < 60:
            suggestions.append({
                "category": "participation",
                "suggestion": "Increase interaction by asking more questions and encouraging responses.",
                "reason": "The meeting had limited back-and-forth discussion between participants.",
                "benefit": "Interactive discussions lead to better idea generation and problem-solving."
            })
        
        # Check for excessive monologues
        speaking_percentages = analytics["efficiency_metrics"].get("speaking_percentages", {})
        if any(percentage > 60 for speaker, percentage in speaking_percentages.items() if speaker != "Unknown"):
            suggestions.append({
                "category": "participation",
                "suggestion": "Limit extended monologues and encourage concise contributions.",
                "reason": "One or more participants spoke for a disproportionate amount of time.",
                "benefit": "Concise contributions keep meetings focused and allow more voices to be heard."
            })
        
        return suggestions
    
    def _generate_content_suggestions(self, analytics: Dict[str, Any]) -> List[Dict[str, Any]]:
        """
        Generate suggestions related to meeting content.
        
        Args:
            analytics (Dict[str, Any]): Meeting analytics
            
        Returns:
            List[Dict[str, Any]]: List of content-related suggestions
        """
        suggestions = []
        
        # Check for action items
        action_items = analytics["efficiency_metrics"].get("action_items", 0)
        if action_items == 0:
            suggestions.append({
                "category": "content",
                "suggestion": "Clearly define action items with assigned owners and deadlines.",
                "reason": "No clear action items were identified in the meeting.",
                "benefit": "Well-defined action items ensure that discussions lead to concrete outcomes."
            })
        
        # Check for decisions
        decisions = analytics["efficiency_metrics"].get("decisions", 0)
        if decisions == 0:
            suggestions.append({
                "category": "content",
                "suggestion": "Explicitly state decisions made during the meeting.",
                "reason": "No clear decisions were identified in the meeting.",
                "benefit": "Explicitly stating decisions ensures everyone understands what was agreed upon."
            })
        
        # Check content density
        content_density = analytics["efficiency_metrics"].get("content_density", 0)
        if content_density < 50:
            suggestions.append({
                "category": "content",
                "suggestion": "Focus on substantive content and minimize small talk or tangents.",
                "reason": "The meeting had a relatively low density of substantive content.",
                "benefit": "Focusing on substantive content makes meetings more productive and valuable."
            })
        
        # Check average sentence length
        avg_sentence_length = analytics["efficiency_metrics"].get("avg_sentence_length", 0)
        if avg_sentence_length > 25:
            suggestions.append({
                "category": "content",
                "suggestion": "Encourage clearer and more concise communication.",
                "reason": "The average sentence length was quite high, which can make communication less clear.",
                "benefit": "Clear, concise communication improves understanding and reduces meeting time."
            })
        
        return suggestions
    
    def _generate_time_suggestions(self, analytics: Dict[str, Any]) -> List[Dict[str, Any]]:
        """
        Generate suggestions related to time management.
        
        Args:
            analytics (Dict[str, Any]): Meeting analytics
            
        Returns:
            List[Dict[str, Any]]: List of time-related suggestions
        """
        suggestions = []
        
        # Check time efficiency
        time_efficiency = analytics["efficiency_metrics"].get("time_efficiency", 0)
        if time_efficiency < 70:
            suggestions.append({
                "category": "time",
                "suggestion": "Keep meetings shorter and more focused.",
                "reason": "The meeting was longer than optimal for the content covered.",
                "benefit": "Shorter, focused meetings respect participants' time and maintain engagement."
            })
        
        # Check words per minute
        words_per_minute = analytics["efficiency_metrics"].get("words_per_minute", 0)
        if words_per_minute < 100:
            suggestions.append({
                "category": "time",
                "suggestion": "Maintain a brisker pace to cover content more efficiently.",
                "reason": "The meeting had a relatively slow pace of discussion.",
                "benefit": "A brisker pace keeps participants engaged and makes better use of meeting time."
            })
        elif words_per_minute > 180:
            suggestions.append({
                "category": "time",
                "suggestion": "Slow down the pace to ensure understanding and allow for questions.",
                "reason": "The meeting had a very rapid pace of discussion.",
                "benefit": "A moderate pace ensures everyone can follow the discussion and contribute effectively."
            })
        
        # Check optimal duration
        optimal_duration = analytics["efficiency_metrics"].get("optimal_duration", 0)
        actual_duration = analytics["efficiency_metrics"].get("duration_minutes", 0)
        if actual_duration > 0 and optimal_duration / actual_duration < 0.5:
            suggestions.append({
                "category": "time",
                "suggestion": "Consider breaking longer meetings into multiple shorter sessions.",
                "reason": "The meeting was significantly longer than needed for the content covered.",
                "benefit": "Shorter meetings maintain focus and energy, leading to better outcomes."
            })
        
        return suggestions
    
    def _generate_followup_suggestions(self, transcript: str, analytics: Dict[str, Any]) -> List[Dict[str, Any]]:
        """
        Generate suggestions related to meeting follow-up.
        
        Args:
            transcript (str): Meeting transcript
            analytics (Dict[str, Any]): Meeting analytics
            
        Returns:
            List[Dict[str, Any]]: List of follow-up-related suggestions
        """
        suggestions = []
        
        # Check for action item follow-up
        if "action item" in transcript.lower() and "follow up" not in transcript.lower():
            suggestions.append({
                "category": "followup",
                "suggestion": "Establish a clear process for following up on action items.",
                "reason": "Action items were identified but no follow-up process was discussed.",
                "benefit": "A clear follow-up process ensures action items are completed and progress is made."
            })
        
        # Check for meeting notes distribution
        if "send" not in transcript.lower() and "minutes" in transcript.lower():
            suggestions.append({
                "category": "followup",
                "suggestion": "Distribute meeting minutes promptly after the meeting.",
                "reason": "Meeting minutes were mentioned but no distribution plan was discussed.",
                "benefit": "Prompt distribution of minutes reinforces decisions and action items."
            })
        
        # Check for next meeting scheduling
        if "next meeting" in transcript.lower() and "schedule" not in transcript.lower():
            suggestions.append({
                "category": "followup",
                "suggestion": "Schedule the next meeting before concluding the current one.",
                "reason": "A next meeting was mentioned but not scheduled during the current meeting.",
                "benefit": "Scheduling the next meeting while everyone is present saves time and ensures participation."
            })
        
        return suggestions
    
    def _prioritize_suggestions(self, suggestions: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """
        Add priority levels to suggestions.
        
        Args:
            suggestions (List[Dict[str, Any]]): List of suggestions
            
        Returns:
            List[Dict[str, Any]]: List of suggestions with priority levels
        """
        # Define category priorities (lower number = higher priority)
        category_priorities = {
            "structure": 1,
            "content": 2,
            "participation": 3,
            "time": 4,
            "followup": 5
        }
        
        # Add priority to each suggestion
        for suggestion in suggestions:
            category = suggestion["category"]
            suggestion["priority"] = category_priorities.get(category, 99)
        
        return suggestions
    
    def generate_personalized_suggestions(self, transcript: str, analytics: Dict[str, Any], 
                                         user_preferences: Dict[str, Any]) -> List[Dict[str, Any]]:
        """
        Generate personalized meeting improvement suggestions based on user preferences.
        
        Args:
            transcript (str): Meeting transcript
            analytics (Dict[str, Any]): Meeting analytics
            user_preferences (Dict[str, Any]): User preferences
            
        Returns:
            List[Dict[str, Any]]: List of personalized improvement suggestions
        """
        # Generate base suggestions
        suggestions = self.generate_suggestions(transcript, analytics)
        
        # Filter and sort suggestions based on user preferences
        if "preferred_categories" in user_preferences:
            # Filter suggestions to preferred categories
            preferred_categories = user_preferences["preferred_categories"]
            suggestions = [s for s in suggestions if s["category"] in preferred_categories]
        
        if "max_suggestions" in user_preferences:
            # Limit number of suggestions
            max_suggestions = user_preferences["max_suggestions"]
            suggestions = suggestions[:max_suggestions]
        
        # Add personalized context based on user role
        if "role" in user_preferences:
            suggestions = self._add_role_specific_context(suggestions, user_preferences["role"])
        
        return suggestions
    
    def _add_role_specific_context(self, suggestions: List[Dict[str, Any]], role: str) -> List[Dict[str, Any]]:
        """
        Add role-specific context to suggestions.
        
        Args:
            suggestions (List[Dict[str, Any]]): List of suggestions
            role (str): User role (e.g., "manager", "facilitator", "participant")
            
        Returns:
            List[Dict[str, Any]]: Suggestions with role-specific context
        """
        role_contexts = {
            "manager": {
                "structure": "As a manager, you can set the tone by establishing clear agendas and time boundaries.",
                "participation": "Consider actively facilitating to ensure all team members contribute.",
                "content": "Focus on driving decisions and action items that move projects forward.",
                "time": "Model efficient time management to respect your team's schedules.",
                "followup": "Take ownership of ensuring action items are tracked and completed."
            },
            "facilitator": {
                "structure": "Your role is crucial in maintaining meeting structure and flow.",
                "participation": "Use facilitation techniques to encourage balanced participation.",
                "content": "Guide discussions to stay on topic and reach concrete outcomes.",
                "time": "Keep meetings on track and within scheduled time limits.",
                "followup": "Ensure clear next steps and accountability measures are established."
            },
            "participant": {
                "structure": "Suggest agenda items in advance to help structure meetings.",
                "participation": "Actively contribute your expertise and ask clarifying questions.",
                "content": "Come prepared with relevant information and be ready to make decisions.",
                "time": "Help keep discussions focused by staying on topic.",
                "followup": "Take ownership of your action items and provide status updates."
            }
        }
        
        if role in role_contexts:
            for suggestion in suggestions:
                category = suggestion["category"]
                if category in role_contexts[role]:
                    suggestion["role_context"] = role_contexts[role][category]
        
        return suggestions
    
    def generate_llm_suggestions(self, transcript: str, analytics: Dict[str, Any]) -> List[Dict[str, Any]]:
        """
        Generate suggestions using LLM analysis.
        
        Args:
            transcript (str): Meeting transcript
            analytics (Dict[str, Any]): Meeting analytics
            
        Returns:
            List[Dict[str, Any]]: List of LLM-generated suggestions
        """
        try:
            # Import LLM client and prompt manager
            from app.llm.llm_client import LLMClient
            from app.prompt.prompt_manager import PromptManager
            
            # Initialize LLM client and prompt manager
            llm_client = LLMClient(self.config.get("llm", {}))
            prompt_manager = PromptManager(self.config.get("prompt", {}))
            
            # Get suggestion generation prompt
            prompt_template = prompt_manager.get_prompt("suggestion_generation")
            
            # Prepare variables for prompt
            prompt_vars = {
                "transcript": transcript,
                "analytics": str(analytics),
                "format": "json"
            }
            
            # Format prompt with variables
            prompt = prompt_manager.format_prompt(prompt_template, prompt_vars)
            
            # Generate suggestions using LLM
            response = llm_client.generate(prompt)
            
            # Parse response
            import json
            import re
            
            # Extract JSON from response
            json_match = re.search(r'\{[\s\S]*\}', response)
            if json_match:
                json_str = json_match.group(0)
                suggestions_data = json.loads(json_str)
                
                # Convert to our suggestion format
                suggestions = []
                
                # Process different suggestion categories
                for category in ["structure_suggestions", "participation_suggestions", 
                               "time_management_suggestions", "decision_making_suggestions", 
                               "action_item_suggestions"]:
                    if category in suggestions_data:
                        category_name = category.replace("_suggestions", "").replace("_", " ")
                        
                        for suggestion_data in suggestions_data[category]:
                            if isinstance(suggestion_data, dict):
                                suggestion = {
                                    "category": category_name,
                                    "suggestion": suggestion_data.get("suggestion", ""),
                                    "reason": suggestion_data.get("rationale", ""),
                                    "benefit": suggestion_data.get("benefit", ""),
                                    "implementation": suggestion_data.get("implementation", ""),
                                    "priority": self._determine_priority(suggestion_data),
                                    "source": "llm"
                                }
                                suggestions.append(suggestion)
                            elif isinstance(suggestion_data, str):
                                suggestion = {
                                    "category": category_name,
                                    "suggestion": suggestion_data,
                                    "reason": "Identified through AI analysis",
                                    "benefit": "Will improve meeting effectiveness",
                                    "priority": 3,
                                    "source": "llm"
                                }
                                suggestions.append(suggestion)
                
                # Add priority suggestions if available
                if "priority_improvements" in suggestions_data:
                    for priority_suggestion in suggestions_data["priority_improvements"]:
                        suggestion = {
                            "category": "priority",
                            "suggestion": priority_suggestion,
                            "reason": "Identified as a priority improvement area",
                            "benefit": "High impact on meeting effectiveness",
                            "priority": 1,
                            "source": "llm"
                        }
                        suggestions.append(suggestion)
                
                return suggestions
            
            return []
            
        except Exception as e:
            logger.warning(f"Error in LLM suggestion generation: {e}")
            return []
    
    def _determine_priority(self, suggestion_data: Dict[str, Any]) -> int:
        """
        Determine priority level for a suggestion.
        
        Args:
            suggestion_data (Dict[str, Any]): Suggestion data
            
        Returns:
            int: Priority level (1 = highest, 5 = lowest)
        """
        # Check for priority indicators in the suggestion text
        suggestion_text = suggestion_data.get("suggestion", "").lower()
        
        high_priority_keywords = ["critical", "urgent", "immediately", "essential", "must"]
        medium_priority_keywords = ["important", "should", "recommend", "consider"]
        low_priority_keywords = ["could", "might", "optional", "nice to have"]
        
        if any(keyword in suggestion_text for keyword in high_priority_keywords):
            return 1
        elif any(keyword in suggestion_text for keyword in medium_priority_keywords):
            return 2
        elif any(keyword in suggestion_text for keyword in low_priority_keywords):
            return 4
        else:
            return 3  # Default priority
    
    def combine_suggestions(self, rule_based: List[Dict[str, Any]], 
                           llm_based: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """
        Combine rule-based and LLM-based suggestions, removing duplicates.
        
        Args:
            rule_based (List[Dict[str, Any]]): Rule-based suggestions
            llm_based (List[Dict[str, Any]]): LLM-based suggestions
            
        Returns:
            List[Dict[str, Any]]: Combined list of unique suggestions
        """
        # Start with rule-based suggestions
        combined = rule_based.copy()
        
        # Add LLM suggestions that don't duplicate rule-based ones
        for llm_suggestion in llm_based:
            is_duplicate = False
            
            for existing_suggestion in combined:
                # Check for similarity in suggestion text
                if self._are_suggestions_similar(llm_suggestion["suggestion"], 
                                               existing_suggestion["suggestion"]):
                    is_duplicate = True
                    # If LLM suggestion has more detail, replace the existing one
                    if len(llm_suggestion.get("implementation", "")) > len(existing_suggestion.get("implementation", "")):
                        combined.remove(existing_suggestion)
                        combined.append(llm_suggestion)
                    break
            
            if not is_duplicate:
                combined.append(llm_suggestion)
        
        # Sort by priority
        combined.sort(key=lambda x: x.get("priority", 3))
        
        return combined
    
    def _are_suggestions_similar(self, suggestion1: str, suggestion2: str) -> bool:
        """
        Check if two suggestions are similar.
        
        Args:
            suggestion1 (str): First suggestion
            suggestion2 (str): Second suggestion
            
        Returns:
            bool: True if suggestions are similar
        """
        # Simple similarity check based on common words
        words1 = set(suggestion1.lower().split())
        words2 = set(suggestion2.lower().split())
        
        # Remove common words
        common_words = {"the", "a", "an", "and", "or", "but", "in", "on", "at", "to", "for", "of", "with", "by"}
        words1 = words1 - common_words
        words2 = words2 - common_words
        
        # Calculate Jaccard similarity
        intersection = len(words1.intersection(words2))
        union = len(words1.union(words2))
        
        similarity = intersection / union if union > 0 else 0
        
        return similarity > 0.5  # Consider similar if more than 50% overlap
    
    def generate_comprehensive_suggestions(self, transcript: str, analytics: Dict[str, Any]) -> List[Dict[str, Any]]:
        """
        Generate comprehensive suggestions using both rule-based and LLM approaches.
        
        Args:
            transcript (str): Meeting transcript
            analytics (Dict[str, Any]): Meeting analytics
            
        Returns:
            List[Dict[str, Any]]: Comprehensive list of suggestions
        """
        # Generate rule-based suggestions
        rule_based_suggestions = self.generate_suggestions(transcript, analytics)
        
        # Generate LLM-based suggestions if enabled
        llm_suggestions = []
        if self.config.get("use_llm", True):
            llm_suggestions = self.generate_llm_suggestions(transcript, analytics)
        
        # Combine suggestions
        comprehensive_suggestions = self.combine_suggestions(rule_based_suggestions, llm_suggestions)
        
        return comprehensive_suggestions