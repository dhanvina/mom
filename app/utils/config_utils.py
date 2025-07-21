"""
Configuration utilities for offline mode and data privacy.

This module provides utility functions for managing configuration
related to offline mode, data privacy, and system status.
"""

import os
import socket
import logging
from typing import Dict, Any, Optional, Tuple
from datetime import datetime, timedelta

logger = logging.getLogger(__name__)


class NetworkChecker:
    """Utility class for checking network connectivity and service availability."""
    
    @staticmethod
    def is_internet_available(timeout: int = 3) -> bool:
        """
        Check if internet connectivity is available.
        
        Args:
            timeout (int): Connection timeout in seconds
            
        Returns:
            bool: True if internet is available
        """
        try:
            socket.create_connection(("8.8.8.8", 53), timeout=timeout)
            return True
        except (socket.error, OSError):
            return False
    
    @staticmethod
    def is_ollama_server_available(host: str = "localhost", port: int = 11434, timeout: int = 5) -> bool:
        """
        Check if Ollama server is available.
        
        Args:
            host (str): Ollama server host
            port (int): Ollama server port
            timeout (int): Connection timeout in seconds
            
        Returns:
            bool: True if Ollama server is available
        """
        try:
            import requests
            response = requests.get(f"http://{host}:{port}/api/version", timeout=timeout)
            return response.status_code == 200
        except Exception:
            return False
    
    @staticmethod
    def get_connectivity_status() -> Dict[str, bool]:
        """
        Get comprehensive connectivity status.
        
        Returns:
            Dict[str, bool]: Status of various connectivity checks
        """
        return {
            'internet': NetworkChecker.is_internet_available(),
            'ollama_server': NetworkChecker.is_ollama_server_available(),
            'local_processing_available': True  # Always available for offline mode
        }


class ModeDetector:
    """Utility class for detecting and managing application modes."""
    
    def __init__(self, config: Dict[str, Any]):
        """
        Initialize mode detector with configuration.
        
        Args:
            config (Dict[str, Any]): Application configuration
        """
        self.config = config
    
    def detect_optimal_mode(self) -> Tuple[bool, str]:
        """
        Detect the optimal mode (online/offline) based on current conditions.
        
        Returns:
            Tuple[bool, str]: (is_offline_mode, reason)
        """
        connectivity = NetworkChecker.get_connectivity_status()
        
        # If auto-detection is disabled, use configured mode
        if not self.config.get('auto_detect_mode', True):
            offline_mode = self.config.get('offline_mode', False)
            return offline_mode, "Manual configuration"
        
        # If privacy mode is enabled, prefer offline
        if self.config.get('privacy_mode', False):
            return True, "Privacy mode enabled"
        
        # If no internet, must use offline
        if not connectivity['internet']:
            return True, "No internet connectivity"
        
        # If internet available but no Ollama server, use offline
        if not connectivity['ollama_server']:
            return True, "Ollama server not available"
        
        # All services available, use online mode
        return False, "All services available"
    
    def get_mode_capabilities(self, offline_mode: bool) -> Dict[str, bool]:
        """
        Get capabilities available in the current mode.
        
        Args:
            offline_mode (bool): Whether in offline mode
            
        Returns:
            Dict[str, bool]: Available capabilities
        """
        if offline_mode:
            return {
                'llm_processing': self.config.get('offline_settings', {}).get('enable_local_llm', False),
                'simple_extraction': True,
                'file_processing': True,
                'basic_formatting': True,
                'collaboration': False,
                'external_integrations': False,
                'cloud_storage': False,
                'real_time_features': False
            }
        else:
            return {
                'llm_processing': True,
                'simple_extraction': True,
                'file_processing': True,
                'basic_formatting': True,
                'collaboration': self.config.get('enable_collaboration', False),
                'external_integrations': True,
                'cloud_storage': True,
                'real_time_features': True
            }


class PrivacyManager:
    """Utility class for managing data privacy and retention."""
    
    def __init__(self, config: Dict[str, Any]):
        """
        Initialize privacy manager with configuration.
        
        Args:
            config (Dict[str, Any]): Application configuration
        """
        self.config = config
        self.data_dir = os.path.join(os.path.expanduser("~"), ".mom_data")
        self.temp_dir = os.path.join(self.data_dir, "temp")
        
        # Ensure directories exist
        os.makedirs(self.data_dir, exist_ok=True)
        os.makedirs(self.temp_dir, exist_ok=True)
    
    def should_auto_delete(self) -> bool:
        """
        Check if automatic deletion is enabled.
        
        Returns:
            bool: True if auto-deletion is enabled
        """
        return self.config.get('auto_delete_transcripts', False)
    
    def get_retention_period(self) -> int:
        """
        Get data retention period in days.
        
        Returns:
            int: Retention period in days
        """
        return self.config.get('data_retention_days', 30)
    
    def cleanup_old_data(self) -> Dict[str, Any]:
        """
        Clean up old data based on retention policy.
        
        Returns:
            Dict[str, Any]: Cleanup results
        """
        if not self.should_auto_delete():
            return {'cleaned': False, 'reason': 'Auto-delete disabled'}
        
        retention_days = self.get_retention_period()
        cutoff_date = datetime.now() - timedelta(days=retention_days)
        
        cleaned_files = []
        errors = []
        
        try:
            for root, dirs, files in os.walk(self.data_dir):
                for file in files:
                    file_path = os.path.join(root, file)
                    try:
                        # Check file modification time
                        file_mtime = datetime.fromtimestamp(os.path.getmtime(file_path))
                        if file_mtime < cutoff_date:
                            os.remove(file_path)
                            cleaned_files.append(file_path)
                            logger.info(f"Deleted old file: {file_path}")
                    except Exception as e:
                        errors.append(f"Error deleting {file_path}: {e}")
                        logger.error(f"Error deleting {file_path}: {e}")
        
        except Exception as e:
            errors.append(f"Error during cleanup: {e}")
            logger.error(f"Error during cleanup: {e}")
        
        return {
            'cleaned': True,
            'files_deleted': len(cleaned_files),
            'files': cleaned_files,
            'errors': errors
        }
    
    def secure_delete_file(self, file_path: str) -> bool:
        """
        Securely delete a file by overwriting it before deletion.
        
        Args:
            file_path (str): Path to file to delete
            
        Returns:
            bool: True if successful
        """
        try:
            if not os.path.exists(file_path):
                return True
            
            # Get file size
            file_size = os.path.getsize(file_path)
            
            # Overwrite with random data
            with open(file_path, 'r+b') as f:
                f.write(os.urandom(file_size))
                f.flush()
                os.fsync(f.fileno())
            
            # Delete the file
            os.remove(file_path)
            logger.info(f"Securely deleted file: {file_path}")
            return True
        
        except Exception as e:
            logger.error(f"Error securely deleting {file_path}: {e}")
            return False
    
    def get_privacy_status(self) -> Dict[str, Any]:
        """
        Get current privacy settings and status.
        
        Returns:
            Dict[str, Any]: Privacy status information
        """
        return {
            'privacy_mode': self.config.get('privacy_mode', False),
            'auto_delete_enabled': self.should_auto_delete(),
            'retention_days': self.get_retention_period(),
            'data_directory': self.data_dir,
            'temp_directory': self.temp_dir,
            'offline_mode': self.config.get('offline_mode', False)
        }


class ConfigValidator:
    """Utility class for validating configuration settings."""
    
    @staticmethod
    def validate_offline_config(config: Dict[str, Any]) -> Tuple[bool, list]:
        """
        Validate offline mode configuration.
        
        Args:
            config (Dict[str, Any]): Configuration to validate
            
        Returns:
            Tuple[bool, list]: (is_valid, list_of_errors)
        """
        errors = []
        
        offline_settings = config.get('offline_settings', {})
        
        # Check model cache directory
        cache_dir = offline_settings.get('model_cache_dir')
        if cache_dir:
            try:
                os.makedirs(cache_dir, exist_ok=True)
                if not os.access(cache_dir, os.W_OK):
                    errors.append(f"Model cache directory not writable: {cache_dir}")
            except Exception as e:
                errors.append(f"Invalid model cache directory: {e}")
        
        # Check cache size limit
        max_cache_size = offline_settings.get('max_cache_size_gb', 10)
        if not isinstance(max_cache_size, (int, float)) or max_cache_size <= 0:
            errors.append("Invalid max_cache_size_gb: must be a positive number")
        
        # Check retention days
        retention_days = config.get('data_retention_days', 30)
        if not isinstance(retention_days, int) or retention_days < 1:
            errors.append("Invalid data_retention_days: must be a positive integer")
        
        return len(errors) == 0, errors
    
    @staticmethod
    def validate_privacy_config(config: Dict[str, Any]) -> Tuple[bool, list]:
        """
        Validate privacy configuration.
        
        Args:
            config (Dict[str, Any]): Configuration to validate
            
        Returns:
            Tuple[bool, list]: (is_valid, list_of_errors)
        """
        errors = []
        
        # Check boolean settings
        bool_settings = ['privacy_mode', 'auto_delete_transcripts', 'offline_mode']
        for setting in bool_settings:
            value = config.get(setting)
            if value is not None and not isinstance(value, bool):
                errors.append(f"Invalid {setting}: must be boolean")
        
        return len(errors) == 0, errors