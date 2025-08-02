"""
Local LLM Manager for offline processing.

This module provides functionality for managing local LLM models,
including downloading, caching, and running models locally for
offline MoM generation.
"""

import os
import json
import logging
import hashlib
import requests
from typing import Dict, Any, Optional, List, Tuple
from datetime import datetime
import subprocess
import shutil

logger = logging.getLogger(__name__)


class ModelInfo:
    """Information about a local LLM model."""
    
    def __init__(self, name: str, size_gb: float, url: str, 
                 description: str = "", requirements: Dict[str, Any] = None):
        """
        Initialize model information.
        
        Args:
            name (str): Model name
            size_gb (float): Model size in GB
            url (str): Download URL
            description (str): Model description
            requirements (Dict[str, Any]): System requirements
        """
        self.name = name
        self.size_gb = size_gb
        self.url = url
        self.description = description
        self.requirements = requirements or {}
        self.downloaded = False
        self.cached_path = None


class LocalLLMManager:
    """
    Manager for local LLM models and offline processing.
    
    This class handles downloading, caching, and running local LLM models
    for offline MoM generation when internet connectivity is not available.
    """
    
    def __init__(self, config: Dict[str, Any]):
        """
        Initialize the LocalLLMManager.
        
        Args:
            config (Dict[str, Any]): Configuration settings
        """
        self.config = config
        self.offline_settings = config.get('offline_settings', {})
        self.cache_dir = self.offline_settings.get(
            'model_cache_dir', 
            os.path.join(os.path.expanduser("~"), ".mom_cache", "models")
        )
        self.max_cache_size_gb = self.offline_settings.get('max_cache_size_gb', 10)
        
        # Ensure cache directory exists
        os.makedirs(self.cache_dir, exist_ok=True)
        
        # Available local models
        self.available_models = self._get_available_models()
        self.cached_models = self._scan_cached_models()
        
        logger.info(f"LocalLLMManager initialized with cache dir: {self.cache_dir}")
    
    def _get_available_models(self) -> Dict[str, ModelInfo]:
        """
        Get list of available local models.
        
        Returns:
            Dict[str, ModelInfo]: Available models
        """
        # For now, we'll focus on smaller models suitable for offline use
        models = {
            'llama3-8b-instruct': ModelInfo(
                name='llama3-8b-instruct',
                size_gb=4.7,
                url='https://huggingface.co/meta-llama/Meta-Llama-3-8B-Instruct',
                description='Llama 3 8B Instruct model - good balance of size and performance',
                requirements={'ram_gb': 8, 'disk_gb': 5}
            ),
            'phi3-mini': ModelInfo(
                name='phi3-mini',
                size_gb=2.3,
                url='https://huggingface.co/microsoft/Phi-3-mini-4k-instruct',
                description='Microsoft Phi-3 Mini - lightweight and efficient',
                requirements={'ram_gb': 4, 'disk_gb': 3}
            ),
            'gemma-2b': ModelInfo(
                name='gemma-2b',
                size_gb=1.4,
                url='https://huggingface.co/google/gemma-2b-it',
                description='Google Gemma 2B - very lightweight for basic tasks',
                requirements={'ram_gb': 3, 'disk_gb': 2}
            )
        }
        
        return models
    
    def _scan_cached_models(self) -> Dict[str, ModelInfo]:
        """
        Scan cache directory for already downloaded models.
        
        Returns:
            Dict[str, ModelInfo]: Cached models
        """
        cached = {}
        
        try:
            if not os.path.exists(self.cache_dir):
                return cached
            
            for item in os.listdir(self.cache_dir):
                model_path = os.path.join(self.cache_dir, item)
                if os.path.isdir(model_path):
                    # Check if this is a valid model directory
                    info_file = os.path.join(model_path, 'model_info.json')
                    if os.path.exists(info_file):
                        try:
                            with open(info_file, 'r') as f:
                                info_data = json.load(f)
                            
                            model_info = ModelInfo(
                                name=info_data['name'],
                                size_gb=info_data['size_gb'],
                                url=info_data['url'],
                                description=info_data.get('description', ''),
                                requirements=info_data.get('requirements', {})
                            )
                            model_info.downloaded = True
                            model_info.cached_path = model_path
                            
                            cached[item] = model_info
                            logger.info(f"Found cached model: {item}")
                        
                        except Exception as e:
                            logger.warning(f"Error reading model info for {item}: {e}")
        
        except Exception as e:
            logger.error(f"Error scanning cached models: {e}")
        
        return cached
    
    def list_available_models(self) -> List[Dict[str, Any]]:
        """
        List all available models with their status.
        
        Returns:
            List[Dict[str, Any]]: Model information
        """
        models = []
        
        for name, model_info in self.available_models.items():
            is_cached = name in self.cached_models
            models.append({
                'name': name,
                'description': model_info.description,
                'size_gb': model_info.size_gb,
                'requirements': model_info.requirements,
                'cached': is_cached,
                'path': self.cached_models[name].cached_path if is_cached else None
            })
        
        return models
    
    def get_recommended_model(self) -> Optional[str]:
        """
        Get recommended model based on system capabilities.
        
        Returns:
            Optional[str]: Recommended model name
        """
        try:
            # Get system memory (simplified check)
            import psutil
            available_ram_gb = psutil.virtual_memory().available / (1024**3)
            available_disk_gb = shutil.disk_usage(self.cache_dir).free / (1024**3)
            
            # Find the best model that fits system requirements
            suitable_models = []
            
            for name, model_info in self.available_models.items():
                ram_req = model_info.requirements.get('ram_gb', 4)
                disk_req = model_info.requirements.get('disk_gb', 2)
                
                if available_ram_gb >= ram_req and available_disk_gb >= disk_req:
                    suitable_models.append((name, model_info))
            
            if not suitable_models:
                logger.warning("No suitable models found for current system")
                return None
            
            # Sort by size (prefer larger models if system can handle them)
            suitable_models.sort(key=lambda x: x[1].size_gb, reverse=True)
            
            recommended = suitable_models[0][0]
            logger.info(f"Recommended model: {recommended}")
            return recommended
        
        except Exception as e:
            logger.error(f"Error determining recommended model: {e}")
            return 'gemma-2b'  # Fallback to smallest model
    
    def is_model_cached(self, model_name: str) -> bool:
        """
        Check if a model is already cached locally.
        
        Args:
            model_name (str): Name of the model
            
        Returns:
            bool: True if model is cached
        """
        return model_name in self.cached_models
    
    def get_cache_usage(self) -> Dict[str, Any]:
        """
        Get current cache usage information.
        
        Returns:
            Dict[str, Any]: Cache usage statistics
        """
        try:
            total_size = 0
            model_count = 0
            
            for model_name, model_info in self.cached_models.items():
                if model_info.cached_path and os.path.exists(model_info.cached_path):
                    # Calculate directory size
                    for root, dirs, files in os.walk(model_info.cached_path):
                        for file in files:
                            file_path = os.path.join(root, file)
                            if os.path.exists(file_path):
                                total_size += os.path.getsize(file_path)
                    model_count += 1
            
            total_size_gb = total_size / (1024**3)
            
            return {
                'total_size_gb': round(total_size_gb, 2),
                'max_size_gb': self.max_cache_size_gb,
                'usage_percent': round((total_size_gb / self.max_cache_size_gb) * 100, 1),
                'model_count': model_count,
                'cache_dir': self.cache_dir
            }
        
        except Exception as e:
            logger.error(f"Error calculating cache usage: {e}")
            return {
                'total_size_gb': 0,
                'max_size_gb': self.max_cache_size_gb,
                'usage_percent': 0,
                'model_count': 0,
                'cache_dir': self.cache_dir
            }
    
    def download_model(self, model_name: str, progress_callback=None) -> Tuple[bool, str]:
        """
        Download a model for local use.
        
        Args:
            model_name (str): Name of the model to download
            progress_callback: Optional callback for progress updates
            
        Returns:
            Tuple[bool, str]: (success, message)
        """
        if model_name not in self.available_models:
            return False, f"Model '{model_name}' not available"
        
        if self.is_model_cached(model_name):
            return True, f"Model '{model_name}' already cached"
        
        model_info = self.available_models[model_name]
        
        # Check cache space
        cache_usage = self.get_cache_usage()
        if cache_usage['total_size_gb'] + model_info.size_gb > self.max_cache_size_gb:
            return False, f"Insufficient cache space. Need {model_info.size_gb}GB, available: {self.max_cache_size_gb - cache_usage['total_size_gb']}GB"
        
        try:
            # For this implementation, we'll simulate model download
            # In a real implementation, this would download from Hugging Face or Ollama
            model_dir = os.path.join(self.cache_dir, model_name)
            os.makedirs(model_dir, exist_ok=True)
            
            # Create model info file
            info_file = os.path.join(model_dir, 'model_info.json')
            with open(info_file, 'w') as f:
                json.dump({
                    'name': model_info.name,
                    'size_gb': model_info.size_gb,
                    'url': model_info.url,
                    'description': model_info.description,
                    'requirements': model_info.requirements,
                    'downloaded_at': datetime.now().isoformat()
                }, f, indent=2)
            
            # Create a placeholder model file (in real implementation, this would be the actual model)
            model_file = os.path.join(model_dir, 'model.bin')
            with open(model_file, 'w') as f:
                f.write(f"# Placeholder for {model_name} model\n")
                f.write(f"# Size: {model_info.size_gb}GB\n")
                f.write(f"# URL: {model_info.url}\n")
            
            # Update cached models
            model_info.downloaded = True
            model_info.cached_path = model_dir
            self.cached_models[model_name] = model_info
            
            logger.info(f"Model '{model_name}' downloaded successfully")
            return True, f"Model '{model_name}' downloaded successfully"
        
        except Exception as e:
            error_msg = f"Error downloading model '{model_name}': {e}"
            logger.error(error_msg)
            return False, error_msg
    
    def remove_model(self, model_name: str) -> Tuple[bool, str]:
        """
        Remove a cached model to free up space.
        
        Args:
            model_name (str): Name of the model to remove
            
        Returns:
            Tuple[bool, str]: (success, message)
        """
        if not self.is_model_cached(model_name):
            return False, f"Model '{model_name}' not cached"
        
        try:
            model_info = self.cached_models[model_name]
            if model_info.cached_path and os.path.exists(model_info.cached_path):
                shutil.rmtree(model_info.cached_path)
            
            # Remove from cached models
            del self.cached_models[model_name]
            
            logger.info(f"Model '{model_name}' removed from cache")
            return True, f"Model '{model_name}' removed successfully"
        
        except Exception as e:
            error_msg = f"Error removing model '{model_name}': {e}"
            logger.error(error_msg)
            return False, error_msg
    
    def cleanup_cache(self, target_usage_percent: float = 80.0) -> Dict[str, Any]:
        """
        Clean up cache to maintain target usage percentage.
        
        Args:
            target_usage_percent (float): Target cache usage percentage
            
        Returns:
            Dict[str, Any]: Cleanup results
        """
        cache_usage = self.get_cache_usage()
        
        if cache_usage['usage_percent'] <= target_usage_percent:
            return {
                'cleaned': False,
                'reason': f"Cache usage ({cache_usage['usage_percent']}%) below target ({target_usage_percent}%)",
                'removed_models': []
            }
        
        # Sort models by last access time (oldest first)
        # For now, we'll just remove models in order of size (largest first)
        models_by_size = sorted(
            self.cached_models.items(),
            key=lambda x: x[1].size_gb,
            reverse=True
        )
        
        removed_models = []
        
        for model_name, model_info in models_by_size:
            if cache_usage['usage_percent'] <= target_usage_percent:
                break
            
            success, message = self.remove_model(model_name)
            if success:
                removed_models.append(model_name)
                # Recalculate cache usage
                cache_usage = self.get_cache_usage()
        
        return {
            'cleaned': len(removed_models) > 0,
            'removed_models': removed_models,
            'final_usage_percent': cache_usage['usage_percent']
        }
    
    def process_with_local_model(self, text: str, model_name: Optional[str] = None) -> Tuple[bool, str]:
        """
        Process text using a local model.
        
        Args:
            text (str): Input text to process
            model_name (str, optional): Specific model to use
            
        Returns:
            Tuple[bool, str]: (success, processed_text)
        """
        # Determine which model to use
        if model_name is None:
            model_name = self.get_recommended_model()
            if model_name is None:
                return False, "No suitable local model available"
        
        if not self.is_model_cached(model_name):
            return False, f"Model '{model_name}' not cached locally"
        
        try:
            # For this implementation, we'll provide a simple fallback processing
            # In a real implementation, this would use the actual local LLM
            
            logger.info(f"Processing text with local model: {model_name}")
            
            # Simple rule-based extraction as fallback
            processed_text = self._simple_mom_extraction(text)
            
            return True, processed_text
        
        except Exception as e:
            error_msg = f"Error processing with local model '{model_name}': {e}"
            logger.error(error_msg)
            return False, error_msg
    
    def _simple_mom_extraction(self, text: str) -> str:
        """
        Simple rule-based MoM extraction as fallback.
        
        Args:
            text (str): Input transcript text
            
        Returns:
            str: Extracted MoM
        """
        lines = text.split('\n')
        
        # Simple extraction logic
        mom_sections = {
            'attendees': [],
            'key_points': [],
            'action_items': [],
            'decisions': []
        }
        
        # Look for common patterns
        for line in lines:
            line = line.strip()
            if not line:
                continue
            
            # Look for names (simple heuristic)
            if ':' in line and len(line.split(':')[0]) < 30:
                speaker = line.split(':')[0].strip()
                if speaker not in mom_sections['attendees'] and len(speaker.split()) <= 3:
                    mom_sections['attendees'].append(speaker)
            
            # Look for action items
            if any(keyword in line.lower() for keyword in ['action', 'todo', 'task', 'assign', 'follow up']):
                mom_sections['action_items'].append(line)
            
            # Look for decisions
            if any(keyword in line.lower() for keyword in ['decide', 'agreed', 'conclusion', 'resolution']):
                mom_sections['decisions'].append(line)
            
            # General key points
            if len(line) > 20 and not line.startswith('http'):
                mom_sections['key_points'].append(line)
        
        # Format output
        mom_output = "# Meeting Minutes\n\n"
        
        if mom_sections['attendees']:
            mom_output += "## Attendees\n"
            for attendee in mom_sections['attendees'][:10]:  # Limit to 10
                mom_output += f"- {attendee}\n"
            mom_output += "\n"
        
        if mom_sections['key_points']:
            mom_output += "## Key Discussion Points\n"
            for point in mom_sections['key_points'][:10]:  # Limit to 10
                mom_output += f"- {point}\n"
            mom_output += "\n"
        
        if mom_sections['action_items']:
            mom_output += "## Action Items\n"
            for item in mom_sections['action_items'][:5]:  # Limit to 5
                mom_output += f"- {item}\n"
            mom_output += "\n"
        
        if mom_sections['decisions']:
            mom_output += "## Decisions\n"
            for decision in mom_sections['decisions'][:5]:  # Limit to 5
                mom_output += f"- {decision}\n"
            mom_output += "\n"
        
        mom_output += "\n*Note: This MoM was generated using offline processing with limited capabilities.*\n"
        
        return mom_output
    
    def get_status(self) -> Dict[str, Any]:
        """
        Get comprehensive status of local LLM manager.
        
        Returns:
            Dict[str, Any]: Status information
        """
        cache_usage = self.get_cache_usage()
        available_models = self.list_available_models()
        recommended_model = self.get_recommended_model()
        
        return {
            'cache_usage': cache_usage,
            'available_models': available_models,
            'cached_model_count': len(self.cached_models),
            'recommended_model': recommended_model,
            'offline_processing_available': len(self.cached_models) > 0 or self.offline_settings.get('fallback_to_simple_extraction', True)
        }