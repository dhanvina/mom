"""
Topic analyzer module for AI-powered MoM generator.

This module provides functionality for identifying topics in meeting transcripts.
"""

import logging
import re
from typing import Dict, Any, Optional, List, Tuple
from collections import Counter, defaultdict
import nltk
from nltk.tokenize import word_tokenize, sent_tokenize
from nltk.corpus import stopwords
from nltk.stem import WordNetLemmatizer
from nltk.collocations import BigramAssocMeasures, BigramCollocationFinder
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.cluster import KMeans

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class TopicAnalyzer:
    """
    Analyzes meeting transcripts to identify topics.
    
    This class provides methods for identifying topics in meeting transcripts
    using various NLP techniques.
    
    Attributes:
        config (Dict): Configuration options for the analyzer
    """
    
    def __init__(self, config: Optional[Dict[str, Any]] = None):
        """
        Initialize the TopicAnalyzer with optional configuration.
        
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
            
        try:
            nltk.data.find('corpora/wordnet')
        except LookupError:
            try:
                nltk.download('wordnet')
            except:
                pass
        
        # Initialize lemmatizer
        self.lemmatizer = WordNetLemmatizer()
        
        logger.info("TopicAnalyzer initialized")
    
    def identify_topics(self, transcript: str, num_topics: int = 5) -> List[Dict[str, Any]]:
        """
        Identify topics in a meeting transcript.
        
        Args:
            transcript (str): Meeting transcript
            num_topics (int, optional): Number of topics to identify. Defaults to 5.
            
        Returns:
            List[Dict[str, Any]]: List of identified topics with relevance scores
        """
        # Preprocess transcript
        preprocessed_text = self._preprocess_text(transcript)
        
        # Extract sentences
        try:
            sentences = sent_tokenize(transcript)
        except Exception as e:
            logger.warning(f"NLTK sentence tokenization failed, using simple fallback: {e}")
            # Simple sentence splitting fallback
            sentences = [s.strip() for s in transcript.split('.') if s.strip()]
        
        # Use multiple methods to identify topics
        keyword_topics = self._extract_keywords(preprocessed_text)
        bigram_topics = self._extract_bigrams(preprocessed_text)
        tfidf_topics = self._extract_tfidf_topics(sentences, num_topics)
        
        # Use LLM-based topic extraction if configured
        llm_topics = []
        if self.config.get("use_llm", True):
            llm_topics = self._extract_llm_topics(transcript, num_topics)
        
        # Combine topics from different methods
        combined_topics = self._combine_topics(keyword_topics, bigram_topics, tfidf_topics, llm_topics)
        
        # Limit to requested number of topics
        topics = combined_topics[:num_topics]
        
        # Add context for each topic
        topics = self._add_topic_context(topics, transcript)
        
        # Add time spent estimation
        topics = self._estimate_time_spent(topics, transcript)
        
        # Add key participants for each topic
        topics = self._identify_key_participants(topics, transcript)
        
        # Identify related topics
        topics = self._identify_related_topics(topics)
        
        return topics
    
    def _preprocess_text(self, text: str) -> List[str]:
        """
        Preprocess text for topic identification.
        
        Args:
            text (str): Text to preprocess
            
        Returns:
            List[str]: List of preprocessed tokens
        """
        try:
            # Convert to lowercase
            text = text.lower()
            
            # Tokenize
            tokens = word_tokenize(text)
            
            # Remove stopwords and punctuation
            stop_words = set(stopwords.words('english'))
            tokens = [token for token in tokens if token.isalnum() and token not in stop_words and len(token) > 2]
            
            # Lemmatize
            tokens = [self.lemmatizer.lemmatize(token) for token in tokens]
            
            return tokens
        
        except Exception as e:
            logger.warning(f"NLTK preprocessing failed, using simple fallback: {e}")
            return self._simple_preprocess_text(text)
    
    def _simple_preprocess_text(self, text: str) -> List[str]:
        """
        Simple text preprocessing fallback that doesn't use NLTK.
        
        Args:
            text (str): Text to preprocess
            
        Returns:
            List[str]: List of preprocessed tokens
        """
        import re
        
        # Convert to lowercase
        text = text.lower()
        
        # Simple tokenization using regex
        tokens = re.findall(r'\b[a-zA-Z]{3,}\b', text)
        
        # Simple stopwords list
        simple_stopwords = {
            'the', 'a', 'an', 'and', 'or', 'but', 'in', 'on', 'at', 'to', 'for', 'of', 'with', 'by',
            'is', 'are', 'was', 'were', 'be', 'been', 'being', 'have', 'has', 'had', 'do', 'does', 'did',
            'will', 'would', 'could', 'should', 'may', 'might', 'can', 'this', 'that', 'these', 'those',
            'i', 'you', 'he', 'she', 'it', 'we', 'they', 'me', 'him', 'her', 'us', 'them'
        }
        
        # Remove stopwords
        tokens = [token for token in tokens if token not in simple_stopwords]
        
        return tokens
    
    def _extract_keywords(self, tokens: List[str]) -> List[Dict[str, Any]]:
        """
        Extract keywords based on frequency.
        
        Args:
            tokens (List[str]): Preprocessed tokens
            
        Returns:
            List[Dict[str, Any]]: List of keywords with relevance scores
        """
        # Count word frequencies
        word_freq = Counter(tokens)
        
        # Get most common words as potential topics
        common_words = word_freq.most_common(20)
        
        # Create topics with relevance scores
        topics = [
            {
                "topic": word,
                "relevance": count / len(tokens) * 100,
                "mentions": count,
                "type": "keyword"
            }
            for word, count in common_words
        ]
        
        return topics
    
    def _extract_bigrams(self, tokens: List[str]) -> List[Dict[str, Any]]:
        """
        Extract bigrams (two-word phrases) as potential topics.
        
        Args:
            tokens (List[str]): Preprocessed tokens
            
        Returns:
            List[Dict[str, Any]]: List of bigrams with relevance scores
        """
        # Find bigram collocations
        bigram_measures = BigramAssocMeasures()
        finder = BigramCollocationFinder.from_words(tokens)
        
        # Apply frequency filter
        finder.apply_freq_filter(3)
        
        # Get top bigrams by PMI score
        bigrams = finder.nbest(bigram_measures.pmi, 15)
        
        # Create topics with relevance scores
        topics = [
            {
                "topic": f"{w1} {w2}",
                "relevance": finder.ngram_fd[(w1, w2)] / len(tokens) * 100,
                "mentions": finder.ngram_fd[(w1, w2)],
                "type": "bigram"
            }
            for w1, w2 in bigrams
        ]
        
        return topics
    
    def _extract_tfidf_topics(self, sentences: List[str], num_topics: int) -> List[Dict[str, Any]]:
        """
        Extract topics using TF-IDF and clustering.
        
        Args:
            sentences (List[str]): List of sentences from the transcript
            num_topics (int): Number of topics to extract
            
        Returns:
            List[Dict[str, Any]]: List of topics with relevance scores
        """
        # Check if we have enough sentences
        if len(sentences) < num_topics:
            return []
        
        try:
            # Create TF-IDF vectorizer
            vectorizer = TfidfVectorizer(
                max_features=100,
                stop_words='english',
                ngram_range=(1, 2)
            )
            
            # Fit and transform sentences
            tfidf_matrix = vectorizer.fit_transform(sentences)
            
            # Cluster sentences
            num_clusters = min(num_topics, len(sentences) // 2)
            kmeans = KMeans(n_clusters=num_clusters, random_state=42)
            kmeans.fit(tfidf_matrix)
            
            # Get cluster centers
            centers = kmeans.cluster_centers_
            
            # Get top terms for each cluster
            feature_names = vectorizer.get_feature_names_out()
            topics = []
            
            for i, center in enumerate(centers):
                # Get top terms for this cluster
                indices = center.argsort()[-5:][::-1]
                top_terms = [feature_names[j] for j in indices]
                
                # Join top terms to form topic
                topic_name = " / ".join(top_terms[:2])
                
                # Count sentences in this cluster
                cluster_size = sum(1 for label in kmeans.labels_ if label == i)
                
                topics.append({
                    "topic": topic_name,
                    "relevance": (cluster_size / len(sentences)) * 100,
                    "mentions": cluster_size,
                    "type": "cluster",
                    "related_terms": top_terms
                })
            
            return topics
            
        except Exception as e:
            logger.warning(f"Error in TF-IDF topic extraction: {e}")
            return []
    
    def _extract_llm_topics(self, transcript: str, num_topics: int = 5) -> List[Dict[str, Any]]:
        """
        Extract topics using LLM-based analysis.
        
        Args:
            transcript (str): Meeting transcript
            num_topics (int): Number of topics to extract
            
        Returns:
            List[Dict[str, Any]]: List of topics with relevance scores
        """
        try:
            # Import LLM client
            from app.llm.llm_client import LLMClient
            from app.prompt.prompt_manager import PromptManager
            
            # Initialize LLM client and prompt manager
            llm_client = LLMClient(self.config.get("llm", {}))
            prompt_manager = PromptManager(self.config.get("prompt", {}))
            
            # Get topic extraction prompt
            prompt_template = prompt_manager.get_prompt("topic_analysis")
            
            # Prepare variables for prompt
            prompt_vars = {
                "transcript": transcript,
                "num_topics": num_topics,
                "format": "json"
            }
            
            # Format prompt with variables
            prompt = prompt_manager.format_prompt(prompt_template, prompt_vars)
            
            # Extract topics using LLM
            response = llm_client.generate(prompt)
            
            # Parse response
            import json
            import re
            
            # Extract JSON from response
            json_match = re.search(r'\{[\s\S]*\}', response)
            if json_match:
                json_str = json_match.group(0)
                topics_data = json.loads(json_str)
                
                # Convert to our topic format
                topics = []
                if "topics" in topics_data:
                    for i, topic_data in enumerate(topics_data["topics"]):
                        # Handle different possible formats
                        if isinstance(topic_data, dict):
                            topic_name = topic_data.get("name", topic_data.get("topic", f"Topic {i+1}"))
                            relevance = topic_data.get("relevance", 100 - (i * 10))  # Decreasing relevance
                            mentions = topic_data.get("frequency", topic_data.get("mentions", 0))
                            time_spent = topic_data.get("time_spent", "")
                            
                            topic = {
                                "topic": topic_name,
                                "relevance": relevance,
                                "mentions": mentions,
                                "type": "llm",
                                "time_spent": time_spent
                            }
                            
                            # Add additional fields if present
                            for key, value in topic_data.items():
                                if key not in ["name", "topic", "relevance", "frequency", "mentions", "time_spent"]:
                                    topic[key] = value
                            
                            topics.append(topic)
                        elif isinstance(topic_data, str):
                            # Simple string format
                            topics.append({
                                "topic": topic_data,
                                "relevance": 100 - (i * 10),  # Decreasing relevance
                                "mentions": 0,
                                "type": "llm"
                            })
                
                return topics
            
            return []
            
        except Exception as e:
            logger.warning(f"Error in LLM topic extraction: {e}")
            return []
    
    def _estimate_time_spent(self, topics: List[Dict[str, Any]], transcript: str) -> List[Dict[str, Any]]:
        """
        Estimate time spent on each topic.
        
        Args:
            topics (List[Dict[str, Any]]): List of topics
            transcript (str): Meeting transcript
            
        Returns:
            List[Dict[str, Any]]: Topics with time spent estimation
        """
        # Split transcript into sentences
        sentences = sent_tokenize(transcript)
        total_sentences = len(sentences)
        
        # Estimate total meeting duration (if not already provided in topics)
        total_duration_minutes = self.config.get("meeting_duration_minutes", 60)
        
        # For each topic, count relevant sentences
        for topic in topics:
            # Skip if time_spent is already set by LLM
            if "time_spent" in topic and topic["time_spent"]:
                continue
                
            topic_terms = topic["topic"].lower().split()
            
            # Count sentences containing topic terms
            relevant_sentences = sum(
                1 for sentence in sentences
                if any(term in sentence.lower() for term in topic_terms)
            )
            
            # Calculate percentage of transcript
            percentage = (relevant_sentences / total_sentences) if total_sentences > 0 else 0
            
            # Estimate time in minutes
            time_minutes = round(percentage * total_duration_minutes)
            
            # Format time string
            if time_minutes < 1:
                time_str = "< 1 minute"
            elif time_minutes == 1:
                time_str = "1 minute"
            else:
                time_str = f"{time_minutes} minutes"
            
            # Add time spent to topic
            topic["time_spent"] = time_str
            topic["time_percentage"] = round(percentage * 100, 1)
        
        return topics
    
    def _identify_key_participants(self, topics: List[Dict[str, Any]], transcript: str) -> List[Dict[str, Any]]:
        """
        Identify key participants for each topic.
        
        Args:
            topics (List[Dict[str, Any]]): List of topics
            transcript (str): Meeting transcript
            
        Returns:
            List[Dict[str, Any]]: Topics with key participants
        """
        # Extract speaker patterns
        speaker_pattern = r'([A-Z][a-z]+ [A-Z][a-z]+):'
        
        # Split transcript into lines
        lines = transcript.split('\n')
        
        # For each topic, find speakers who discuss it
        for topic in topics:
            topic_terms = topic["topic"].lower().split()
            
            # Track speakers and their contribution to this topic
            speaker_contributions = defaultdict(int)
            current_speaker = "Unknown"
            
            for line in lines:
                # Check if line starts with a speaker name
                speaker_match = re.match(speaker_pattern, line)
                if speaker_match:
                    current_speaker = speaker_match.group(1)
                    # Remove speaker name from line
                    line = line[len(f"{current_speaker}:"):].strip()
                
                # Check if line contains topic terms
                line_lower = line.lower()
                if any(term in line_lower for term in topic_terms):
                    # Count words as contribution
                    words = len(line.split())
                    speaker_contributions[current_speaker] += words
            
            # Sort speakers by contribution
            sorted_speakers = sorted(
                speaker_contributions.items(),
                key=lambda x: x[1],
                reverse=True
            )
            
            # Get top 3 speakers
            key_participants = [speaker for speaker, _ in sorted_speakers[:3] if speaker != "Unknown"]
            
            # Add key participants to topic
            topic["key_participants"] = key_participants
        
        return topics
    
    def _identify_related_topics(self, topics: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """
        Identify related topics for each topic.
        
        Args:
            topics (List[Dict[str, Any]]): List of topics
            
        Returns:
            List[Dict[str, Any]]: Topics with related topics
        """
        # Create a similarity matrix between topics
        num_topics = len(topics)
        similarity_matrix = [[0.0 for _ in range(num_topics)] for _ in range(num_topics)]
        
        # Calculate similarity between each pair of topics
        for i in range(num_topics):
            for j in range(i + 1, num_topics):
                topic_i_terms = set(topics[i]["topic"].lower().split())
                topic_j_terms = set(topics[j]["topic"].lower().split())
                
                # Check for shared terms
                shared_terms = topic_i_terms.intersection(topic_j_terms)
                
                # Calculate Jaccard similarity
                union_terms = topic_i_terms.union(topic_j_terms)
                similarity = len(shared_terms) / len(union_terms) if union_terms else 0
                
                # Check for context similarity if available
                if "context" in topics[i] and "context" in topics[j]:
                    context_i = " ".join(topics[i]["context"]).lower()
                    context_j = " ".join(topics[j]["context"]).lower()
                    
                    # Check for shared terms in context
                    context_i_terms = set(context_i.split())
                    context_j_terms = set(context_j.split())
                    shared_context_terms = context_i_terms.intersection(context_j_terms)
                    
                    # Boost similarity based on context overlap
                    context_similarity = len(shared_context_terms) / (len(context_i_terms) + len(context_j_terms)) if (len(context_i_terms) + len(context_j_terms)) > 0 else 0
                    similarity = (similarity + context_similarity) / 2
                
                # Store similarity
                similarity_matrix[i][j] = similarity
                similarity_matrix[j][i] = similarity
        
        # For each topic, find related topics
        for i, topic in enumerate(topics):
            # Get indices of most similar topics
            similar_indices = sorted(
                range(num_topics),
                key=lambda j: similarity_matrix[i][j] if i != j else -1,
                reverse=True
            )[:3]  # Top 3 related topics
            
            # Get related topics
            related_topics = [topics[j]["topic"] for j in similar_indices if similarity_matrix[i][j] > 0.1]
            
            # Add related topics to topic
            topic["related_topics"] = related_topics
        
        return topics
    
    def _combine_topics(self, keyword_topics: List[Dict[str, Any]], 
                       bigram_topics: List[Dict[str, Any]],
                       tfidf_topics: List[Dict[str, Any]],
                       llm_topics: List[Dict[str, Any]] = None) -> List[Dict[str, Any]]:
        """
        Combine topics from different extraction methods.
        
        Args:
            keyword_topics (List[Dict[str, Any]]): Topics from keyword extraction
            bigram_topics (List[Dict[str, Any]]): Topics from bigram extraction
            tfidf_topics (List[Dict[str, Any]]): Topics from TF-IDF extraction
            llm_topics (List[Dict[str, Any]], optional): Topics from LLM extraction
            
        Returns:
            List[Dict[str, Any]]: Combined list of topics
        """
        # Combine all topics
        all_topics = []
        
        # Add LLM topics first (they're usually the best quality)
        if llm_topics:
            all_topics.extend(llm_topics)
        
        # Add TF-IDF topics next (they're usually better than keywords/bigrams)
        all_topics.extend(tfidf_topics)
        
        # Add bigram topics
        all_topics.extend(bigram_topics)
        
        # Add keyword topics
        all_topics.extend(keyword_topics)
        
        # Remove duplicates (based on topic name)
        seen_topics = set()
        unique_topics = []
        
        for topic in all_topics:
            # Normalize topic name for comparison
            normalized_topic = topic["topic"].lower().strip()
            
            if normalized_topic not in seen_topics:
                seen_topics.add(normalized_topic)
                unique_topics.append(topic)
            else:
                # If we have a duplicate topic but from a better source (LLM > TF-IDF > bigram > keyword),
                # replace the existing one
                topic_types = {"llm": 3, "cluster": 2, "bigram": 1, "keyword": 0}
                
                # Find the existing topic with the same name
                for i, existing_topic in enumerate(unique_topics):
                    if existing_topic["topic"].lower().strip() == normalized_topic:
                        # Compare topic types
                        existing_type = existing_topic.get("type", "keyword")
                        new_type = topic.get("type", "keyword")
                        
                        existing_score = topic_types.get(existing_type, 0)
                        new_score = topic_types.get(new_type, 0)
                        
                        # Replace if new topic has a better type
                        if new_score > existing_score:
                            unique_topics[i] = topic
                        # If same type but higher relevance, replace
                        elif new_score == existing_score and topic.get("relevance", 0) > existing_topic.get("relevance", 0):
                            unique_topics[i] = topic
                        
                        break
        
        # Sort by relevance
        unique_topics.sort(key=lambda x: x.get("relevance", 0), reverse=True)
        
        return unique_topics
    
    def _add_topic_context(self, topics: List[Dict[str, Any]], transcript: str) -> List[Dict[str, Any]]:
        """
        Add context for each topic.
        
        Args:
            topics (List[Dict[str, Any]]): List of topics
            transcript (str): Meeting transcript
            
        Returns:
            List[Dict[str, Any]]: Topics with added context
        """
        # Split transcript into sentences
        try:
            sentences = sent_tokenize(transcript)
        except Exception as e:
            logger.warning(f"NLTK sentence tokenization failed, using simple fallback: {e}")
            # Simple sentence splitting fallback
            sentences = [s.strip() for s in transcript.split('.') if s.strip()]
        
        # For each topic, find relevant sentences
        for topic in topics:
            topic_terms = topic["topic"].lower().split()
            
            # Find sentences containing topic terms
            relevant_sentences = []
            for sentence in sentences:
                sentence_lower = sentence.lower()
                if any(term in sentence_lower for term in topic_terms):
                    relevant_sentences.append(sentence)
            
            # Limit to 3 sentences
            relevant_sentences = relevant_sentences[:3]
            
            # Add context to topic
            topic["context"] = relevant_sentences
        
        return topics
    
    def generate_topic_distribution(self, topics: List[Dict[str, Any]]) -> Dict[str, float]:
        """
        Generate topic distribution data for visualization.
        
        Args:
            topics (List[Dict[str, Any]]): List of topics
            
        Returns:
            Dict[str, float]: Dictionary mapping topic names to their relevance scores
        """
        # Create distribution dictionary
        distribution = {}
        
        # Calculate total relevance
        total_relevance = sum(topic["relevance"] for topic in topics)
        
        # Normalize relevance scores
        if total_relevance > 0:
            for topic in topics:
                distribution[topic["topic"]] = topic["relevance"] / total_relevance * 100
        
        return distribution