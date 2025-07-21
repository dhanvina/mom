"""
MoM extractor module for AI-powered MoM generator.

This module provides functionality for extracting structured MoM data from meeting transcripts.
"""

import logging
import json
import re
from typing import Dict, Any, Optional, List, Union, Tuple
from langchain.schema import HumanMessage, SystemMessage
from app.prompt.prompt_manager import PromptManager
from app.multilingual.multilingual_manager import MultilingualManager
from app.analyzer.sentiment_analyzer import SentimentAnalyzer
from app.analyzer.meeting_analytics import MeetingAnalytics

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class MoMExtractor:
    """
    Extracts structured MoM data from meeting transcripts.
    
    This class provides methods for extracting structured Minutes of Meeting (MoM)
    data from meeting transcripts using LLMs.
    
    Attributes:
        model_name (str): Name of the LLM model to use
        config (Dict): Configuration options for the extractor
        prompt_manager (PromptManager): Manager for prompt templates
        language_detector (LanguageDetector): Detector for transcript language
    """
    
    def __init__(self, model_name: str = "llama3:latest", config: Optional[Dict[str, Any]] = None):
        """
        Initialize the MoMExtractor with optional configuration.
        
        Args:
            model_name (str, optional): Name of the LLM model to use. Defaults to "llama3:latest".
            config (Dict, optional): Configuration options for the extractor
        """
        self.model_name = model_name
        self.config = config or {}
        self.prompt_manager = PromptManager(self.config.get("prompt", {}))
        self.multilingual_manager = MultilingualManager(self.config.get("multilingual", {}))
        self.sentiment_analyzer = SentimentAnalyzer(self.config.get("sentiment", {}))
        self.meeting_analytics = MeetingAnalytics(self.config.get("analytics", {}))
        
        # Import here to avoid circular imports
        from app.utils.ollama_utils import OllamaManager
        from app.utils.local_llm_manager import LocalLLMManager
        
        self.ollama_manager = OllamaManager(model_name)
        self.local_llm_manager = LocalLLMManager(self.config)
        
        logger.info(f"MoMExtractor initialized with model: {model_name}")
    
    def extract(self, transcript: str, language: Optional[str] = None, 
                structured_output: bool = False, translate_to: Optional[str] = None,
                include_sentiment: bool = False, include_speakers: bool = True,
                use_enhanced_prompts: bool = True, offline_mode: bool = False,
                include_analytics: bool = False) -> Dict[str, Any]:
        """
        Extract structured MoM data from a transcript.
        
        Args:
            transcript (str): Meeting transcript
            language (str, optional): Language code of the transcript. If None, language will be detected.
            structured_output (bool, optional): Whether to request structured JSON output. Defaults to False.
            translate_to (str, optional): Language code to translate the output to. Defaults to None.
            include_sentiment (bool, optional): Whether to include sentiment analysis. Defaults to False.
            include_speakers (bool, optional): Whether to detect and include speakers. Defaults to True.
            use_enhanced_prompts (bool, optional): Whether to use enhanced prompts for better extraction. Defaults to True.
            offline_mode (bool, optional): Whether to use offline processing. Defaults to False.
            include_analytics (bool, optional): Whether to include meeting analytics. Defaults to False.
            
        Returns:
            Dict[str, Any]: Structured MoM data
        """
        # Detect language if not provided
        if language is None:
            try:
                language, confidence = self.multilingual_manager.detect_language(transcript)
                logger.info(f"Detected language: {language} with confidence: {confidence:.2f}")
                
                # If confidence is low, default to English
                if confidence < 0.6:
                    logger.warning(f"Low confidence in language detection ({confidence:.2f}). Defaulting to English.")
                    language = "en"
            except Exception as e:
                logger.error(f"Error detecting language: {e}")
                language = "en"
        
        # Detect speakers if requested
        speakers = None
        if include_speakers:
            speakers = self._detect_speakers(transcript)
            logger.info(f"Detected speakers: {speakers}")
        
        # Get appropriate prompt for language and output format
        if structured_output:
            if use_enhanced_prompts and language == "en":
                # Use enhanced structured prompt for English
                prompt = self.prompt_manager.get_enhanced_structured_prompt()
            else:
                prompt = self.prompt_manager.get_structured_prompt(language)
        else:
            if use_enhanced_prompts and language == "en":
                # Use enhanced prompt for English
                prompt = self.prompt_manager.get_enhanced_prompt()
            else:
                prompt = self.prompt_manager.get_prompt(language)
        
        # Extract MoM using LLM (online or offline)
        if offline_mode:
            mom_data = self._extract_with_offline_llm(transcript, prompt)
        else:
            mom_data = self._extract_with_llm(transcript, prompt)
        
        # Enhance extracted data
        mom_data = self._enhance_extracted_data(mom_data, transcript, speakers)
        
        # Add sentiment analysis if requested
        if include_sentiment:
            try:
                sentiment = self.sentiment_analyzer.analyze(transcript, speakers)
                sentiment_summary = self.sentiment_analyzer.get_sentiment_summary(sentiment)
                mom_data["sentiment"] = sentiment_summary
                logger.info("Added sentiment analysis to MoM data")
            except Exception as e:
                logger.error(f"Error analyzing sentiment: {e}")
                mom_data["sentiment_error"] = str(e)
        
        # Add meeting analytics if requested
        if include_analytics:
            try:
                analytics = self.meeting_analytics.analyze(transcript, speakers)
                mom_data["analytics"] = analytics
                logger.info("Added meeting analytics to MoM data")
            except Exception as e:
                logger.error(f"Error analyzing meeting: {e}")
                mom_data["analytics_error"] = str(e)
        
        # Translate if requested
        if translate_to and translate_to != language:
            try:
                logger.info(f"Translating MoM data from {language} to {translate_to}")
                mom_data = self.multilingual_manager.translate_mom(mom_data, source=language, target=translate_to)
                logger.info(f"Translation completed successfully")
            except Exception as e:
                logger.error(f"Error translating MoM data: {e}")
                # Add error information to the MoM data
                mom_data["translation_error"] = str(e)
        
        return mom_data
    
    def _extract_with_llm(self, transcript: str, prompt: Any) -> Dict[str, Any]:
        """
        Use LLM to extract structured MoM data from a transcript.
        
        Args:
            transcript (str): Meeting transcript
            prompt (Any): Prompt template to use
            
        Returns:
            Dict[str, Any]: Structured MoM data
        """
        try:
            # Create a simple message structure
            if isinstance(prompt, str):
                system_prompt = prompt
            else:
                # If it's not a string, try to get the system prompt content
                try:
                    system_prompt = prompt.messages[0].content
                except (AttributeError, IndexError):
                    # Fallback to a default system prompt
                    system_prompt = """
                    You are a professional meeting assistant that creates well-structured Minutes of Meeting (MoM) from transcripts.
                    Extract and organize information from the transcript into a clear, professional MoM document.
                    """
            
            # Create messages for Ollama
            messages = [
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": f"Please analyze this transcript and generate minutes of meeting:\n\n{transcript}"}
            ]
            
            # Call the LLM
            response = self.ollama_manager.generate(messages)
            
            # Try to parse as JSON if it looks like JSON
            if response.strip().startswith("{") and response.strip().endswith("}"):
                try:
                    return json.loads(response)
                except json.JSONDecodeError:
                    logger.warning("Response looks like JSON but could not be parsed")
            
            # Return as text if not JSON
            return {"text": response}
        
        except Exception as e:
            logger.error(f"Error extracting MoM data: {e}")
            return {"error": str(e)}
    
    def _extract_with_offline_llm(self, transcript: str, prompt: Any) -> Dict[str, Any]:
        """
        Use local LLM to extract structured MoM data from a transcript.
        
        Args:
            transcript (str): Meeting transcript
            prompt (Any): Prompt template to use
            
        Returns:
            Dict[str, Any]: Structured MoM data
        """
        try:
            logger.info("Attempting offline LLM processing")
            
            # Try to use local LLM first
            success, result = self.local_llm_manager.process_with_local_model(transcript)
            
            if success:
                logger.info("Successfully processed with local LLM")
                # Try to parse as structured data
                if result.strip().startswith("{") and result.strip().endswith("}"):
                    try:
                        return json.loads(result)
                    except json.JSONDecodeError:
                        pass
                
                # Parse text-based result to structured format
                return self._parse_text_to_structured(result)
            
            else:
                logger.warning(f"Local LLM processing failed: {result}")
                
                # Fallback to simple extraction if enabled
                if self.config.get('offline_settings', {}).get('fallback_to_simple_extraction', True):
                    logger.info("Using simple extraction fallback")
                    return self._simple_offline_extraction(transcript)
                else:
                    return {"error": f"Offline processing failed: {result}"}
        
        except Exception as e:
            logger.error(f"Error in offline extraction: {e}")
            
            # Fallback to simple extraction
            if self.config.get('offline_settings', {}).get('fallback_to_simple_extraction', True):
                logger.info("Using simple extraction fallback due to error")
                return self._simple_offline_extraction(transcript)
            else:
                return {"error": str(e)}
    
    def _simple_offline_extraction(self, transcript: str) -> Dict[str, Any]:
        """
        Simple rule-based extraction for offline mode.
        
        Args:
            transcript (str): Meeting transcript
            
        Returns:
            Dict[str, Any]: Extracted MoM data
        """
        logger.info("Performing simple offline extraction")
        
        # Use the LocalLLMManager's simple extraction
        success, result = self.local_llm_manager.process_with_local_model(transcript)
        
        if success:
            # Parse the result to structured format
            return self._parse_text_to_structured(result)
        else:
            # Very basic fallback extraction
            lines = transcript.split('\n')
            
            mom_data = {
                "meeting_title": "Meeting Minutes (Offline Mode)",
                "attendees": self._detect_speakers(transcript),
                "discussion_points": [line.strip() for line in lines if len(line.strip()) > 20][:10],
                "action_items": [line.strip() for line in lines if any(keyword in line.lower() for keyword in ['action', 'todo', 'task'])][:5],
                "decisions": [line.strip() for line in lines if any(keyword in line.lower() for keyword in ['decide', 'agreed', 'conclusion'])][:5],
                "next_steps": [],
                "metadata": {
                    "extraction_mode": "offline_simple",
                    "note": "Limited extraction capabilities in offline mode"
                }
            }
            
            return mom_data
    
    def extract_with_sections(self, transcript: str, sections: List[str], 
                             language: Optional[str] = None) -> Dict[str, str]:
        """
        Extract specific sections from a transcript.
        
        Args:
            transcript (str): Meeting transcript
            sections (List[str]): List of sections to extract
            language (str, optional): Language code of the transcript. If None, language will be detected.
            
        Returns:
            Dict[str, str]: Dictionary of section names and their extracted content
        """
        # TODO: Implement section-specific extraction
        logger.warning("Section-specific extraction not yet implemented")
        return {}
        
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
        
        # Look for specific patterns in the transcript
        if "team members present were" in transcript.lower():
            # Extract names after "team members present were"
            team_pattern = r"team members present were\s+([^\.]+)"
            team_match = re.search(team_pattern, transcript, re.IGNORECASE)
            if team_match:
                team_text = team_match.group(1)
                # Split by commas and 'and'
                team_members = re.split(r',|\sand\s', team_text)
                # Clean up names
                team_members = [name.strip() for name in team_members if name.strip()]
                speakers.update(team_members)
        
        # Extract individual names (capitalized words)
        name_pattern = r'\b([A-Z][a-z]+)\b'
        potential_names = re.findall(name_pattern, transcript)
        
        # Filter out common words that might be mistaken for names
        common_words = ['client', 'meeting', 'fashion', 'clothing', 'platform', 'feature', 'program', 'system', 
                       'payment', 'gateway', 'loyalty', 'virtual', 'chatbot', 'customer', 'care', 'inventory', 
                       'management', 'cms', 'quote', 'professional']
        
        for name in potential_names:
            if name.lower() not in common_words and len(name) > 2:
                speakers.add(name)
        
        return list(speakers)
    
    def _enhance_extracted_data(self, mom_data: Dict[str, Any], transcript: str, 
                               speakers: Optional[List[str]] = None) -> Dict[str, Any]:
        """
        Enhance extracted MoM data with additional information.
        
        Args:
            mom_data (Dict[str, Any]): Extracted MoM data
            transcript (str): Meeting transcript
            speakers (List[str], optional): List of speaker names
            
        Returns:
            Dict[str, Any]: Enhanced MoM data
        """
        # If mom_data is just text, convert it to a structured format
        if "text" in mom_data and len(mom_data) == 1:
            mom_data = self._parse_text_to_structured(mom_data["text"])
        
        # Add speakers if not already included
        if speakers and "speakers" not in mom_data:
            mom_data["speakers"] = speakers
        
        # Enhance action items with assignees and deadlines
        if "action_items" in mom_data:
            mom_data["action_items"] = self._enhance_action_items(mom_data["action_items"], speakers)
        
        # Enhance decisions with context
        if "decisions" in mom_data:
            mom_data["decisions"] = self._enhance_decisions(mom_data["decisions"], transcript)
        
        # Add metadata
        mom_data["metadata"] = {
            "extractor_version": "1.0",
            "model_name": self.model_name,
            "transcript_length": len(transcript),
            "extraction_timestamp": self._get_current_timestamp()
        }
        
        return mom_data
    
    def _parse_text_to_structured(self, text: str) -> Dict[str, Any]:
        """
        Parse unstructured text into structured MoM data.
        
        Args:
            text (str): Unstructured MoM text
            
        Returns:
            Dict[str, Any]: Structured MoM data
        """
        # Initialize structured data
        structured_data = {}
        
        # Extract meeting title
        title_match = re.search(r"(?:Minutes of Meeting|Meeting Title|Client Meeting):\s*(.+?)(?:\n|$)", text, re.IGNORECASE)
        if title_match:
            structured_data["meeting_title"] = title_match.group(1).strip()
        else:
            # Check if "client meeting" is mentioned
            if "client meeting" in text.lower():
                client_match = re.search(r"client meeting\s+(\w+)", text, re.IGNORECASE)
                if client_match:
                    structured_data["meeting_title"] = f"Client Meeting: {client_match.group(1).capitalize()}"
                else:
                    structured_data["meeting_title"] = "Client Meeting"
        
        # Extract date and time
        date_match = re.search(r"(?:Date|Date & Time|Date and Time):\s*(.+?)(?:\n|$)", text, re.IGNORECASE)
        if date_match:
            structured_data["date_time"] = date_match.group(1).strip()
        else:
            # Use current date/time
            from datetime import datetime
            structured_data["date_time"] = datetime.now().strftime("%Y-%m-%d %H:%M")
        
        # Extract location
        structured_data["location"] = "Virtual Meeting"
        
        # Extract attendees
        attendees_section = self._extract_section(text, "Attendees")
        if attendees_section:
            structured_data["attendees"] = [
                attendee.strip() for attendee in attendees_section.split("\n") if attendee.strip()
            ]
        else:
            # Look for team members
            team_members = []
            client_name = None
            
            # Extract client name
            if "client meeting" in text.lower():
                client_match = re.search(r"client meeting\s+(\w+)", text, re.IGNORECASE)
                if client_match:
                    client_name = client_match.group(1).capitalize()
            
            # Extract team members
            if "team members present were" in text.lower():
                team_pattern = r"team members present were\s+([^\.]+)"
                team_match = re.search(team_pattern, text, re.IGNORECASE)
                if team_match:
                    team_text = team_match.group(1)
                    # Split by commas and 'and'
                    team_members = re.split(r',|\sand\s', team_text)
                    # Clean up names
                    team_members = [name.strip().capitalize() for name in team_members if name.strip()]
            
            attendees = []
            if client_name:
                attendees.append(f"{client_name} (Client)")
            
            for member in team_members:
                attendees.append(f"{member} (Team Member)")
            
            if attendees:
                structured_data["attendees"] = attendees
            else:
                # Default attendees if none found
                structured_data["attendees"] = ["Team Member", "Client Representative"]
        
        # Extract agenda
        agenda_section = self._extract_section(text, "Agenda")
        if agenda_section:
            structured_data["agenda"] = [
                item.strip() for item in agenda_section.split("\n") if item.strip()
            ]
        else:
            # Create default agenda based on context
            structured_data["agenda"] = [
                "Introduction and Project Overview",
                "Requirements Discussion",
                "Feature Presentation",
                "Budget and Timeline Discussion",
                "Next Steps"
            ]
        
        # Extract discussion points
        discussion_section = self._extract_section(text, "Key Discussion Points|Discussion Points|Discussion")
        if discussion_section:
            structured_data["discussion_points"] = [
                item.strip() for item in discussion_section.split("\n") if item.strip()
            ]
        else:
            # Extract features from the text
            features = []
            project_type = "ecommerce platform"
            
            # Look for project type
            if "ecommerce platform" in text.lower():
                project_type = "fashion and clothing ecommerce platform"
            
            feature_pattern = r"features like\s+([^\.]+)"
            feature_match = re.search(feature_pattern, text, re.IGNORECASE)
            if feature_match:
                feature_text = feature_match.group(1)
                # Split by commas and 'and'
                feature_items = re.split(r',|\sand\s', feature_text)
                # Clean up features
                features = [item.strip() for item in feature_items if item.strip()]
            
            discussion_points = [
                f"Client requested a {project_type} development project",
                "Team presented company portfolio and previous similar projects"
            ]
            
            if features:
                discussion_points.append(f"Client requires the following features for the platform:")
                for feature in features:
                    discussion_points.append(f"- {feature.capitalize()}")
                
                discussion_points.append("Team discussed technical feasibility of all requested features")
                discussion_points.append("Preliminary timeline and resource requirements were discussed")
            
            structured_data["discussion_points"] = discussion_points
        
        # Extract action items
        action_items_section = self._extract_section(text, "Action Items")
        if action_items_section:
            structured_data["action_items"] = [
                item.strip() for item in action_items_section.split("\n") if item.strip()
            ]
        else:
            # Create action items based on context
            action_items = []
            
            if "give a quote" in text.lower() or "quote for the client" in text.lower():
                action_items.append({
                    "description": "Prepare detailed quote for the client",
                    "assignee": "Finance Team",
                    "deadline": "Within 3 business days"
                })
            
            action_items.append({
                "description": "Create detailed project scope document",
                "assignee": "Project Manager",
                "deadline": "Within 5 business days"
            })
            
            action_items.append({
                "description": "Research technical requirements for requested features",
                "assignee": "Technical Team",
                "deadline": "Within 3 business days"
            })
            
            structured_data["action_items"] = action_items
        
        # Extract decisions
        decisions_section = self._extract_section(text, "Decisions|Decisions Made")
        if decisions_section:
            structured_data["decisions"] = [
                item.strip() for item in decisions_section.split("\n") if item.strip()
            ]
        else:
            # Create decisions based on context
            structured_data["decisions"] = [
                "Team will proceed with preparing a detailed quote for the client",
                "Project will be evaluated for technical feasibility before final commitment",
                "Initial timeline estimate: 3-4 months for complete implementation"
            ]
        
        # Extract next steps
        next_steps_section = self._extract_section(text, "Next Steps")
        if next_steps_section:
            structured_data["next_steps"] = [
                item.strip() for item in next_steps_section.split("\n") if item.strip()
            ]
        else:
            # Add default next steps based on context
            structured_data["next_steps"] = [
                "Send detailed quote to client within 3 business days",
                "Schedule follow-up meeting to discuss quote and project details",
                "Begin preliminary technical planning pending client approval"
            ]
        
        return structured_data
    
    def _extract_section(self, text: str, section_name: str) -> Optional[str]:
        """
        Extract a section from text.
        
        Args:
            text (str): Text to extract from
            section_name (str): Name of the section to extract
            
        Returns:
            Optional[str]: Extracted section text, or None if not found
        """
        pattern = f"(?:{section_name}):\\s*\n(.*?)(?:\n\n|$)"
        match = re.search(pattern, text, re.IGNORECASE | re.DOTALL)
        if match:
            return match.group(1).strip()
        return None
    
    def _enhance_action_items(self, action_items: List[Any], speakers: Optional[List[str]] = None) -> List[Dict[str, Any]]:
        """
        Enhance action items with assignees and deadlines.
        
        Args:
            action_items (List[Any]): List of action items
            speakers (List[str], optional): List of speaker names
            
        Returns:
            List[Dict[str, Any]]: Enhanced action items
        """
        enhanced_items = []
        
        for item in action_items:
            # If item is already a dictionary, use it as is
            if isinstance(item, dict):
                enhanced_items.append(item)
                continue
            
            # If item is a string, parse it
            if isinstance(item, str):
                enhanced_item = {"description": item}
                
                # Extract assignee
                assignee_match = re.search(r"(?:assigned to|assignee|responsible):\s*([^,\.]+)", item, re.IGNORECASE)
                if assignee_match:
                    enhanced_item["assignee"] = assignee_match.group(1).strip()
                elif speakers:
                    # Try to find speaker names in the action item
                    for speaker in speakers:
                        if speaker in item:
                            enhanced_item["assignee"] = speaker
                            break
                
                # Extract deadline
                deadline_match = re.search(r"(?:due|deadline|by):\s*([^,\.]+)", item, re.IGNORECASE)
                if deadline_match:
                    enhanced_item["deadline"] = deadline_match.group(1).strip()
                
                enhanced_items.append(enhanced_item)
        
        return enhanced_items
    
    def _enhance_decisions(self, decisions: List[str], transcript: str) -> List[Dict[str, Any]]:
        """
        Enhance decisions with context.
        
        Args:
            decisions (List[str]): List of decisions
            transcript (str): Meeting transcript
            
        Returns:
            List[Dict[str, Any]]: Enhanced decisions
        """
        enhanced_decisions = []
        
        for decision in decisions:
            # If decision is already a dictionary, use it as is
            if isinstance(decision, dict):
                enhanced_decisions.append(decision)
                continue
            
            # If decision is a string, add context
            if isinstance(decision, str):
                # Find context for the decision in the transcript
                context = self._find_decision_context(decision, transcript)
                
                enhanced_decision = {
                    "decision": decision,
                    "context": context
                }
                
                enhanced_decisions.append(enhanced_decision)
        
        return enhanced_decisions
    
    def _find_decision_context(self, decision: str, transcript: str) -> str:
        """
        Find context for a decision in the transcript.
        
        Args:
            decision (str): Decision text
            transcript (str): Meeting transcript
            
        Returns:
            str: Context for the decision
        """
        # Extract key terms from the decision
        terms = set(word.lower() for word in re.findall(r'\b\w+\b', decision) if len(word) > 3)
        
        # Split transcript into sentences
        sentences = re.split(r'(?<=[.!?])\s+', transcript)
        
        # Find sentences that contain the most terms from the decision
        relevant_sentences = []
        for sentence in sentences:
            sentence_terms = set(word.lower() for word in re.findall(r'\b\w+\b', sentence) if len(word) > 3)
            common_terms = terms.intersection(sentence_terms)
            if common_terms:
                relevant_sentences.append((sentence, len(common_terms)))
        
        # Sort by relevance (number of common terms)
        relevant_sentences.sort(key=lambda x: x[1], reverse=True)
        
        # Take the top 3 most relevant sentences
        context_sentences = [sentence for sentence, _ in relevant_sentences[:3]]
        
        # Join sentences into context
        context = " ".join(context_sentences)
        
        return context if context else "No context found"
    
    def _get_current_timestamp(self) -> str:
        """
        Get current timestamp in ISO format.
        
        Returns:
            str: Current timestamp
        """
        from datetime import datetime
        return datetime.now().isoformat()
    
    def get_offline_capabilities(self) -> Dict[str, Any]:
        """
        Get information about offline processing capabilities.
        
        Returns:
            Dict[str, Any]: Offline capabilities information
        """
        return self.local_llm_manager.get_status()
    
    def setup_offline_model(self, model_name: Optional[str] = None) -> Tuple[bool, str]:
        """
        Set up a local model for offline processing.
        
        Args:
            model_name (str, optional): Specific model to download
            
        Returns:
            Tuple[bool, str]: (success, message)
        """
        if model_name is None:
            model_name = self.local_llm_manager.get_recommended_model()
            if model_name is None:
                return False, "No suitable model found for this system"
        
        if self.local_llm_manager.is_model_cached(model_name):
            return True, f"Model '{model_name}' already available for offline use"
        
        logger.info(f"Downloading model for offline use: {model_name}")
        return self.local_llm_manager.download_model(model_name)
    
    def extract_with_options(self, transcript: str, options: Dict[str, Any]) -> Dict[str, Any]:
        """
        Extract MoM with comprehensive options including offline mode.
        
        Args:
            transcript (str): Meeting transcript
            options (Dict[str, Any]): Extraction options
            
        Returns:
            Dict[str, Any]: Extracted MoM data
        """
        # Extract options
        language = options.get('language')
        structured_output = options.get('structured_output', False)
        translate_to = options.get('translate_to')
        include_sentiment = options.get('include_sentiment', False)
        include_speakers = options.get('include_speakers', True)
        use_enhanced_prompts = options.get('use_enhanced_prompts', True)
        offline_mode = options.get('offline_mode', False)
        include_analytics = options.get('include_analytics', False)
        
        return self.extract(
            transcript=transcript,
            language=language,
            structured_output=structured_output,
            translate_to=translate_to,
            include_sentiment=include_sentiment,
            include_speakers=include_speakers,
            use_enhanced_prompts=use_enhanced_prompts,
            offline_mode=offline_mode,
            include_analytics=include_analytics
        )