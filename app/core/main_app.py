"""
Main application module for AI-powered MoM generator.

This module provides the main application class that orchestrates the workflow
between different components of the MoM generator system.
"""

import os
import json
import logging
from typing import Dict, Any, Optional, Tuple, List
from datetime import datetime

from loader.transcript_loader import TranscriptLoader
from extractor.mom_extractor import MoMExtractor
from formatter.mom_formatter import MoMFormatter
from utils.config_utils import NetworkChecker, ModeDetector, PrivacyManager, ConfigValidator
from utils.data_privacy_manager import DataPrivacyManager
from utils.privacy_policy_generator import PrivacyPolicyGenerator

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class ConfigManager:
    """
    Manages application configuration with offline mode support.
    
    This class handles loading, saving, and accessing configuration settings
    for the MoM generator application, including offline mode configuration
    and visual indicators for current mode.
    
    Attributes:
        config_path (str): Path to the configuration file
        config (Dict): Configuration settings
        _offline_mode (bool): Current offline mode status
        _mode_indicators (Dict): Visual indicators for different modes
    """
    
    def __init__(self, config_path: Optional[str] = None):
        """
        Initialize the ConfigManager with an optional config path.
        
        Args:
            config_path (str, optional): Path to the configuration file
        """
        self.config_path = config_path or os.path.join(os.path.dirname(__file__), '..', 'config', 'config.json')
        self.config = self._load_config()
        self._offline_mode = self.config.get('offline_mode', False)
        self._mode_indicators = {
            'online': '🌐 Online Mode',
            'offline': '🔒 Offline Mode',
            'auto': '🔄 Auto Mode'
        }
        
        # Initialize utility classes
        self.mode_detector = ModeDetector(self.config)
        self.privacy_manager = PrivacyManager(self.config)
        self.data_privacy_manager = DataPrivacyManager(self.config)
        self.privacy_policy_generator = PrivacyPolicyGenerator(self.config)
        
        # Validate configuration
        self._validate_config()
        
    def _load_config(self) -> Dict[str, Any]:
        """
        Load configuration from file with offline mode support.
        
        Returns:
            Dict[str, Any]: Configuration settings
        """
        default_config = {
            "model_name": "llama3:latest",
            "default_format": "text",
            "offline_mode": False,
            "auto_detect_mode": True,
            "offline_model_path": None,
            "local_model_name": "llama3:latest",
            "enable_collaboration": False,
            "data_retention_days": 30,
            "auto_delete_transcripts": False,
            "privacy_mode": False,
            "loader": {},
            "extractor": {
                "offline_fallback": True,
                "local_processing": False
            },
            "formatter": {},
            "offline_settings": {
                "enable_local_llm": True,
                "model_cache_dir": os.path.join(os.path.expanduser("~"), ".mom_cache", "models"),
                "max_cache_size_gb": 10,
                "fallback_to_simple_extraction": True
            }
        }
        
        try:
            if os.path.exists(self.config_path):
                with open(self.config_path, 'r') as f:
                    config = json.load(f)
                # Merge with default config to ensure all keys exist
                for key, value in default_config.items():
                    if key not in config:
                        config[key] = value
                return config
            else:
                # Create config directory if it doesn't exist
                os.makedirs(os.path.dirname(self.config_path), exist_ok=True)
                # Save default config
                with open(self.config_path, 'w') as f:
                    json.dump(default_config, f, indent=2)
                return default_config
        except Exception as e:
            logger.error(f"Error loading configuration: {e}")
            return default_config
    
    def save(self) -> bool:
        """
        Save configuration to file.
        
        Returns:
            bool: True if successful, False otherwise
        """
        try:
            with open(self.config_path, 'w') as f:
                json.dump(self.config, f, indent=2)
            return True
        except Exception as e:
            logger.error(f"Error saving configuration: {e}")
            return False
    
    def get(self, key: str, default: Any = None) -> Any:
        """
        Get a configuration value.
        
        Args:
            key (str): Configuration key
            default (Any, optional): Default value if key doesn't exist
            
        Returns:
            Any: Configuration value
        """
        return self.config.get(key, default)
    
    def set(self, key: str, value: Any) -> None:
        """
        Set a configuration value.
        
        Args:
            key (str): Configuration key
            value (Any): Configuration value
        """
        self.config[key] = value
    
    def is_offline_mode(self) -> bool:
        """
        Check if the application is in offline mode.
        
        Returns:
            bool: True if in offline mode, False otherwise
        """
        return self._offline_mode
    
    def set_offline_mode(self, offline: bool) -> None:
        """
        Set offline mode status.
        
        Args:
            offline (bool): True to enable offline mode, False to disable
        """
        self._offline_mode = offline
        self.config['offline_mode'] = offline
        logger.info(f"Offline mode {'enabled' if offline else 'disabled'}")
    
    def toggle_offline_mode(self) -> bool:
        """
        Toggle offline mode on/off.
        
        Returns:
            bool: New offline mode status
        """
        new_status = not self._offline_mode
        self.set_offline_mode(new_status)
        return new_status
    
    def get_mode_indicator(self) -> str:
        """
        Get visual indicator for current mode.
        
        Returns:
            str: Visual indicator string
        """
        if self.config.get('auto_detect_mode', False):
            return self._mode_indicators['auto']
        elif self._offline_mode:
            return self._mode_indicators['offline']
        else:
            return self._mode_indicators['online']
    
    def auto_detect_mode(self) -> bool:
        """
        Automatically detect and set appropriate mode based on network connectivity.
        
        Returns:
            bool: True if online mode is available, False if offline mode is set
        """
        if not self.config.get('auto_detect_mode', False):
            return not self._offline_mode
        
        try:
            # Try to check network connectivity
            import socket
            socket.create_connection(("8.8.8.8", 53), timeout=3)
            
            # Check if Ollama server is accessible
            try:
                import requests
                response = requests.get("http://localhost:11434/api/version", timeout=5)
                if response.status_code == 200:
                    if self._offline_mode:
                        logger.info("Network and Ollama server available, switching to online mode")
                        self.set_offline_mode(False)
                    return True
            except:
                pass
            
            # Network available but Ollama not accessible
            if not self._offline_mode:
                logger.info("Network available but Ollama server not accessible, switching to offline mode")
                self.set_offline_mode(True)
            return False
            
        except (socket.error, OSError):
            # No network connectivity
            if not self._offline_mode:
                logger.info("No network connectivity detected, switching to offline mode")
                self.set_offline_mode(True)
            return False
    
    def get_offline_settings(self) -> Dict[str, Any]:
        """
        Get offline mode specific settings.
        
        Returns:
            Dict[str, Any]: Offline settings
        """
        return self.config.get('offline_settings', {})
    
    def update_offline_settings(self, settings: Dict[str, Any]) -> None:
        """
        Update offline mode specific settings.
        
        Args:
            settings (Dict[str, Any]): New offline settings
        """
        if 'offline_settings' not in self.config:
            self.config['offline_settings'] = {}
        
        self.config['offline_settings'].update(settings)
        logger.info("Offline settings updated")
    
    def get_data_retention_days(self) -> int:
        """
        Get data retention period in days.
        
        Returns:
            int: Number of days to retain data
        """
        return self.config.get('data_retention_days', 30)
    
    def is_auto_delete_enabled(self) -> bool:
        """
        Check if automatic transcript deletion is enabled.
        
        Returns:
            bool: True if auto-delete is enabled
        """
        return self.config.get('auto_delete_transcripts', False)
    
    def is_privacy_mode_enabled(self) -> bool:
        """
        Check if privacy mode is enabled.
        
        Returns:
            bool: True if privacy mode is enabled
        """
        return self.config.get('privacy_mode', False)
    
    def _validate_config(self) -> None:
        """Validate configuration settings."""
        try:
            # Validate offline configuration
            offline_valid, offline_errors = ConfigValidator.validate_offline_config(self.config)
            if not offline_valid:
                for error in offline_errors:
                    logger.warning(f"Offline config validation: {error}")
            
            # Validate privacy configuration
            privacy_valid, privacy_errors = ConfigValidator.validate_privacy_config(self.config)
            if not privacy_valid:
                for error in privacy_errors:
                    logger.warning(f"Privacy config validation: {error}")
        
        except Exception as e:
            logger.error(f"Error validating configuration: {e}")
    
    def get_system_status(self) -> Dict[str, Any]:
        """
        Get comprehensive system status including connectivity and mode information.
        
        Returns:
            Dict[str, Any]: System status information
        """
        connectivity = NetworkChecker.get_connectivity_status()
        optimal_mode, mode_reason = self.mode_detector.detect_optimal_mode()
        capabilities = self.mode_detector.get_mode_capabilities(self._offline_mode)
        privacy_status = self.privacy_manager.get_privacy_status()
        
        return {
            'current_mode': 'offline' if self._offline_mode else 'online',
            'mode_indicator': self.get_mode_indicator(),
            'optimal_mode': 'offline' if optimal_mode else 'online',
            'mode_reason': mode_reason,
            'connectivity': connectivity,
            'capabilities': capabilities,
            'privacy': privacy_status,
            'config_valid': True  # Would be set based on validation results
        }
    
    def cleanup_data(self) -> Dict[str, Any]:
        """
        Clean up old data based on privacy settings.
        
        Returns:
            Dict[str, Any]: Cleanup results
        """
        return self.privacy_manager.cleanup_old_data()


class MainApp:
    """
    Main application class for the MoM generator.
    
    This class orchestrates the workflow between different components of the
    MoM generator system, including transcript loading, MoM extraction, and
    output formatting.
    
    Attributes:
        config_manager (ConfigManager): Configuration manager
        transcript_loader (TranscriptLoader): Transcript loader
        mom_extractor (MoMExtractor): MoM extractor
        mom_formatter (MoMFormatter): MoM formatter
    """
    
    def __init__(self, config_path: Optional[str] = None):
        """
        Initialize the MainApp with optional configuration path.
        
        Args:
            config_path (str, optional): Path to the configuration file
        """
        # Initialize configuration
        self.config_manager = ConfigManager(config_path)
        
        # Auto-detect mode if enabled
        if self.config_manager.get('auto_detect_mode', True):
            self.config_manager.auto_detect_mode()
        
        # Initialize data privacy manager
        self.data_privacy_manager = DataPrivacyManager(self.config_manager.config)
        self.privacy_policy_generator = PrivacyPolicyGenerator(self.config_manager.config)
        
        # Initialize components
        self.transcript_loader = TranscriptLoader(
            config=self.config_manager.get('loader', {})
        )
        
        self.mom_extractor = MoMExtractor(
            model_name=self.config_manager.get('model_name', 'llama3:latest'),
            config=self.config_manager.get('extractor', {})
        )
        
        self.mom_formatter = MoMFormatter(
            config=self.config_manager.get('formatter', {})
        )
        
        logger.info(f"MainApp initialized - {self.config_manager.get_mode_indicator()}")
    
    def setup(self) -> Tuple[bool, str]:
        """
        Set up the application and check dependencies with offline mode support.
        
        Returns:
            Tuple[bool, str]: (success, message)
        """
        try:
            # Get system status
            status = self.config_manager.get_system_status()
            
            # If in offline mode, skip online dependency checks
            if self.config_manager.is_offline_mode():
                logger.info("Running in offline mode - skipping online dependency checks")
                
                # Check if local LLM is available for offline processing
                offline_settings = self.config_manager.get_offline_settings()
                if offline_settings.get('enable_local_llm', False):
                    # TODO: Check local LLM availability (will be implemented in task 10.2)
                    logger.info("Local LLM support enabled")
                
                return True, f"Application setup successful - {self.config_manager.get_mode_indicator()}"
            
            # Online mode - check dependencies
            if not status['connectivity']['ollama_server']:
                # Auto-switch to offline mode if configured
                if self.config_manager.get('auto_detect_mode', True):
                    self.config_manager.set_offline_mode(True)
                    logger.info("Ollama server not available, switched to offline mode")
                    return True, f"Application setup successful - {self.config_manager.get_mode_indicator()}"
                else:
                    return False, "Ollama server is not running"
            
            # Check if model is available
            if not self.mom_extractor.ollama_manager.is_model_available():
                success = self.mom_extractor.ollama_manager.pull_model()
                if not success:
                    # Try offline mode as fallback
                    if self.config_manager.get('auto_detect_mode', True):
                        self.config_manager.set_offline_mode(True)
                        logger.info("Failed to pull model, switched to offline mode")
                        return True, f"Application setup successful - {self.config_manager.get_mode_indicator()}"
                    else:
                        return False, f"Failed to pull model: {self.mom_extractor.model_name}"
            
            return True, f"Application setup successful - {self.config_manager.get_mode_indicator()}"
        
        except Exception as e:
            error_msg = f"Error setting up application: {e}"
            logger.error(error_msg)
            
            # Try fallback to offline mode
            if not self.config_manager.is_offline_mode() and self.config_manager.get('auto_detect_mode', True):
                self.config_manager.set_offline_mode(True)
                logger.info("Setup failed, falling back to offline mode")
                return True, f"Application setup successful (fallback) - {self.config_manager.get_mode_indicator()}"
            
            return False, error_msg
    
    def process_file(self, file_path: str, output_format: str = "text") -> Dict[str, Any]:
        """
        Process a transcript file and generate MoM with offline mode support.
        
        Args:
            file_path (str): Path to the transcript file
            output_format (str, optional): Output format. Defaults to "text".
            
        Returns:
            Dict[str, Any]: Result containing MoM data and formatted output
            
        Raises:
            FileNotFoundError: If the file does not exist
            ValueError: If the file format is not supported
            RuntimeError: If processing fails
        """
        try:
            # Load transcript
            transcript = self.transcript_loader.load_from_file(file_path)
            
            # Extract MoM data with offline mode consideration
            offline_mode = self.config_manager.is_offline_mode()
            mom_data = self.mom_extractor.extract(transcript, offline_mode=offline_mode)
            
            # Format output
            output = self.mom_formatter.format(mom_data, output_format)
            
            return {
                'mom_data': mom_data,
                'output': output,
                'processing_mode': 'offline' if offline_mode else 'online'
            }
        
        except Exception as e:
            error_msg = f"Error processing file {file_path}: {e}"
            logger.error(error_msg)
            raise RuntimeError(error_msg)
    
    def process_text(self, text: str, output_format: str = "text") -> Dict[str, Any]:
        """
        Process a transcript text and generate MoM with offline mode support.
        
        Args:
            text (str): Transcript text
            output_format (str, optional): Output format. Defaults to "text".
            
        Returns:
            Dict[str, Any]: Result containing MoM data and formatted output
            
        Raises:
            RuntimeError: If processing fails
        """
        try:
            # Preprocess text
            transcript = self.transcript_loader.load_from_text(text)
            
            # Extract MoM data with offline mode consideration
            offline_mode = self.config_manager.is_offline_mode()
            mom_data = self.mom_extractor.extract(transcript, offline_mode=offline_mode)
            
            # Format output
            output = self.mom_formatter.format(mom_data, output_format)
            
            return {
                'mom_data': mom_data,
                'output': output,
                'processing_mode': 'offline' if offline_mode else 'online'
            }
        
        except Exception as e:
            error_msg = f"Error processing text: {e}"
            logger.error(error_msg)
            raise RuntimeError(error_msg)
    
    def save_output(self, output: str, output_path: str) -> bool:
        """
        Save output to a file.
        
        Args:
            output (str): Output content
            output_path (str): Path to save the output
            
        Returns:
            bool: True if successful, False otherwise
        """
        try:
            # Create directory if it doesn't exist
            os.makedirs(os.path.dirname(os.path.abspath(output_path)), exist_ok=True)
            
            # Write output to file
            with open(output_path, 'w', encoding='utf-8') as f:
                f.write(output)
            
            logger.info(f"Output saved to {output_path}")
            return True
        
        except Exception as e:
            error_msg = f"Error saving output to {output_path}: {e}"
            logger.error(error_msg)
            return False
    
    def get_system_status(self) -> Dict[str, Any]:
        """
        Get comprehensive system status.
        
        Returns:
            Dict[str, Any]: System status information
        """
        return self.config_manager.get_system_status()
    
    def toggle_offline_mode(self) -> Dict[str, Any]:
        """
        Toggle offline mode and return new status.
        
        Returns:
            Dict[str, Any]: New mode status and capabilities
        """
        new_offline_status = self.config_manager.toggle_offline_mode()
        
        # Save configuration
        self.config_manager.save()
        
        # Get updated capabilities
        capabilities = self.config_manager.mode_detector.get_mode_capabilities(new_offline_status)
        
        return {
            'offline_mode': new_offline_status,
            'mode_indicator': self.config_manager.get_mode_indicator(),
            'capabilities': capabilities,
            'message': f"Switched to {'offline' if new_offline_status else 'online'} mode"
        }
    
    def cleanup_old_data(self) -> Dict[str, Any]:
        """
        Clean up old data based on privacy settings.
        
        Returns:
            Dict[str, Any]: Cleanup results
        """
        return self.config_manager.cleanup_data()
    
    def get_privacy_status(self) -> Dict[str, Any]:
        """
        Get privacy settings and status.
        
        Returns:
            Dict[str, Any]: Privacy status information
        """
        return self.config_manager.privacy_manager.get_privacy_status()
    
    def update_privacy_settings(self, settings: Dict[str, Any]) -> bool:
        """
        Update privacy settings.
        
        Args:
            settings (Dict[str, Any]): New privacy settings
            
        Returns:
            bool: True if successful
        """
        try:
            # Update relevant config values
            for key, value in settings.items():
                if key in ['privacy_mode', 'auto_delete_transcripts', 'data_retention_days']:
                    self.config_manager.set(key, value)
            
            # Save configuration
            success = self.config_manager.save()
            
            if success:
                logger.info("Privacy settings updated")
            
            return success
        
        except Exception as e:
            logger.error(f"Error updating privacy settings: {e}")
            return False
    
    def get_offline_capabilities(self) -> Dict[str, Any]:
        """
        Get offline processing capabilities.
        
        Returns:
            Dict[str, Any]: Offline capabilities information
        """
        return self.mom_extractor.get_offline_capabilities()
    
    def setup_offline_model(self, model_name: Optional[str] = None) -> Dict[str, Any]:
        """
        Set up a local model for offline processing.
        
        Args:
            model_name (str, optional): Specific model to download
            
        Returns:
            Dict[str, Any]: Setup result
        """
        try:
            success, message = self.mom_extractor.setup_offline_model(model_name)
            
            return {
                'success': success,
                'message': message,
                'offline_capabilities': self.get_offline_capabilities() if success else None
            }
        
        except Exception as e:
            error_msg = f"Error setting up offline model: {e}"
            logger.error(error_msg)
            return {
                'success': False,
                'message': error_msg
            }
    
    def list_offline_models(self) -> List[Dict[str, Any]]:
        """
        List available offline models.
        
        Returns:
            List[Dict[str, Any]]: Available models information
        """
        try:
            return self.mom_extractor.local_llm_manager.list_available_models()
        except Exception as e:
            logger.error(f"Error listing offline models: {e}")
            return []
    
    def remove_offline_model(self, model_name: str) -> Dict[str, Any]:
        """
        Remove a cached offline model.
        
        Args:
            model_name (str): Name of the model to remove
            
        Returns:
            Dict[str, Any]: Removal result
        """
        try:
            success, message = self.mom_extractor.local_llm_manager.remove_model(model_name)
            
            return {
                'success': success,
                'message': message,
                'cache_usage': self.mom_extractor.local_llm_manager.get_cache_usage() if success else None
            }
        
        except Exception as e:
            error_msg = f"Error removing offline model: {e}"
            logger.error(error_msg)
            return {
                'success': False,
                'message': error_msg
            }
    
    def get_comprehensive_privacy_status(self) -> Dict[str, Any]:
        """
        Get comprehensive privacy status including data privacy features.
        
        Returns:
            Dict[str, Any]: Comprehensive privacy status
        """
        try:
            config_privacy = self.config_manager.privacy_manager.get_privacy_status()
            data_privacy = self.data_privacy_manager.get_privacy_status()
            
            return {
                'config_privacy': config_privacy,
                'data_privacy': data_privacy,
                'combined_status': {
                    'privacy_mode': config_privacy.get('privacy_mode', False) or data_privacy.get('privacy_mode', False),
                    'offline_mode': config_privacy.get('offline_mode', False),
                    'auto_delete_enabled': data_privacy.get('auto_delete_enabled', False),
                    'anonymize_data': data_privacy.get('anonymize_data', False),
                    'encrypt_storage': data_privacy.get('encrypt_storage', False)
                }
            }
        except Exception as e:
            logger.error(f"Error getting comprehensive privacy status: {e}")
            return {'error': str(e)}
    
    def store_transcript_securely(self, transcript: str, metadata: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """
        Store a transcript with privacy considerations.
        
        Args:
            transcript (str): Transcript content
            metadata (Dict[str, Any], optional): Transcript metadata
            
        Returns:
            Dict[str, Any]: Storage result
        """
        try:
            file_path = self.data_privacy_manager.store_transcript(transcript, metadata)
            
            return {
                'success': True,
                'file_path': file_path,
                'message': 'Transcript stored securely'
            }
        except Exception as e:
            error_msg = f"Error storing transcript securely: {e}"
            logger.error(error_msg)
            return {
                'success': False,
                'error': error_msg
            }
    
    def store_mom_output_securely(self, mom_data: Dict[str, Any], output_format: str = 'json') -> Dict[str, Any]:
        """
        Store MoM output with privacy considerations.
        
        Args:
            mom_data (Dict[str, Any]): MoM data
            output_format (str): Output format
            
        Returns:
            Dict[str, Any]: Storage result
        """
        try:
            file_path = self.data_privacy_manager.store_mom_output(mom_data, output_format)
            
            return {
                'success': True,
                'file_path': file_path,
                'message': 'MoM output stored securely'
            }
        except Exception as e:
            error_msg = f"Error storing MoM output securely: {e}"
            logger.error(error_msg)
            return {
                'success': False,
                'error': error_msg
            }
    
    def cleanup_old_data_comprehensive(self) -> Dict[str, Any]:
        """
        Comprehensive cleanup of old data using both privacy managers.
        
        Returns:
            Dict[str, Any]: Cleanup results
        """
        try:
            # Cleanup using config privacy manager
            config_cleanup = self.config_manager.cleanup_data()
            
            # Cleanup using data privacy manager
            data_cleanup = self.data_privacy_manager.cleanup_old_data()
            
            return {
                'config_cleanup': config_cleanup,
                'data_cleanup': data_cleanup,
                'total_deleted': (config_cleanup.get('files_deleted', 0) + 
                                data_cleanup.get('deleted_count', 0))
            }
        except Exception as e:
            error_msg = f"Error in comprehensive cleanup: {e}"
            logger.error(error_msg)
            return {
                'success': False,
                'error': error_msg
            }
    
    def delete_all_user_data(self) -> Dict[str, Any]:
        """
        Delete all user data for privacy compliance.
        
        Returns:
            Dict[str, Any]: Deletion results
        """
        try:
            result = self.data_privacy_manager.delete_all_data()
            
            if result.get('success', False):
                logger.info("All user data deleted successfully")
            
            return result
        except Exception as e:
            error_msg = f"Error deleting all user data: {e}"
            logger.error(error_msg)
            return {
                'success': False,
                'error': error_msg
            }
    
    def export_user_data(self, export_path: str) -> Dict[str, Any]:
        """
        Export all user data for portability (GDPR compliance).
        
        Args:
            export_path (str): Path to export data to
            
        Returns:
            Dict[str, Any]: Export results
        """
        try:
            result = self.data_privacy_manager.export_data(export_path)
            
            if result.get('success', False):
                logger.info(f"User data exported to: {export_path}")
            
            return result
        except Exception as e:
            error_msg = f"Error exporting user data: {e}"
            logger.error(error_msg)
            return {
                'success': False,
                'error': error_msg
            }
    
    def generate_privacy_policy(self, output_path: Optional[str] = None) -> Dict[str, Any]:
        """
        Generate privacy policy documentation.
        
        Args:
            output_path (str, optional): Path to save the policy
            
        Returns:
            Dict[str, Any]: Generation result
        """
        try:
            policy_content = self.privacy_policy_generator.generate_privacy_policy(output_path)
            
            return {
                'success': True,
                'content': policy_content,
                'output_path': output_path,
                'message': 'Privacy policy generated successfully'
            }
        except Exception as e:
            error_msg = f"Error generating privacy policy: {e}"
            logger.error(error_msg)
            return {
                'success': False,
                'error': error_msg
            }
    
    def generate_compliance_report(self) -> Dict[str, Any]:
        """
        Generate comprehensive privacy compliance report.
        
        Returns:
            Dict[str, Any]: Compliance report
        """
        try:
            # Get privacy report from data privacy manager
            privacy_report = self.data_privacy_manager.create_privacy_report()
            
            # Get compliance checklist from policy generator
            compliance_checklist = self.privacy_policy_generator.generate_compliance_checklist()
            
            # Combine reports
            comprehensive_report = {
                'report_date': datetime.now().isoformat(),
                'privacy_report': privacy_report,
                'compliance_checklist': compliance_checklist,
                'system_status': self.get_comprehensive_privacy_status(),
                'recommendations': self._generate_combined_recommendations(privacy_report, compliance_checklist)
            }
            
            return {
                'success': True,
                'report': comprehensive_report
            }
        except Exception as e:
            error_msg = f"Error generating compliance report: {e}"
            logger.error(error_msg)
            return {
                'success': False,
                'error': error_msg
            }
    
    def _generate_combined_recommendations(self, privacy_report: Dict[str, Any], 
                                         compliance_checklist: Dict[str, Any]) -> List[str]:
        """
        Generate combined recommendations from privacy report and compliance checklist.
        
        Args:
            privacy_report (Dict[str, Any]): Privacy report
            compliance_checklist (Dict[str, Any]): Compliance checklist
            
        Returns:
            List[str]: Combined recommendations
        """
        recommendations = []
        
        # Add recommendations from privacy report
        if 'recommendations' in privacy_report:
            recommendations.extend(privacy_report['recommendations'])
        
        # Add recommendations from compliance checklist
        if 'recommendations' in compliance_checklist:
            recommendations.extend(compliance_checklist['recommendations'])
        
        # Remove duplicates while preserving order
        seen = set()
        unique_recommendations = []
        for rec in recommendations:
            if rec not in seen:
                seen.add(rec)
                unique_recommendations.append(rec)
        
        return unique_recommendations
    
    def detect_and_set_optimal_mode(self) -> Dict[str, Any]:
        """
        Automatically detect and set the optimal processing mode.
        
        Returns:
            Dict[str, Any]: Mode detection results
        """
        try:
            # Get current connectivity status
            connectivity = NetworkChecker.get_connectivity_status()
            
            # Detect optimal mode
            optimal_offline, reason = self.config_manager.mode_detector.detect_optimal_mode()
            
            # Get current mode
            current_offline = self.config_manager.is_offline_mode()
            
            # Update mode if different from optimal
            mode_changed = False
            if current_offline != optimal_offline:
                self.config_manager.set_offline_mode(optimal_offline)
                self.config_manager.save()
                mode_changed = True
                logger.info(f"Mode changed to {'offline' if optimal_offline else 'online'}: {reason}")
            
            # Get capabilities for the current mode
            capabilities = self.config_manager.mode_detector.get_mode_capabilities(optimal_offline)
            
            return {
                'success': True,
                'current_mode': 'offline' if optimal_offline else 'online',
                'mode_changed': mode_changed,
                'reason': reason,
                'connectivity': connectivity,
                'capabilities': capabilities,
                'mode_indicator': self.config_manager.get_mode_indicator()
            }
        
        except Exception as e:
            error_msg = f"Error detecting optimal mode: {e}"
            logger.error(error_msg)
            return {
                'success': False,
                'error': error_msg
            }
    
    def process_with_graceful_degradation(self, source: str, source_type: Optional[str] = None, 
                                        output_format: str = "text", 
                                        options: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """
        Process input with graceful degradation between online and offline modes.
        
        Args:
            source (str): Input source (file path or text)
            source_type (str, optional): Type of source ('file' or 'text')
            output_format (str): Output format
            options (Dict[str, Any], optional): Processing options
            
        Returns:
            Dict[str, Any]: Processing results with mode information
        """
        options = options or {}
        processing_attempts = []
        
        try:
            # First, try to detect optimal mode
            mode_detection = self.detect_and_set_optimal_mode()
            current_mode = 'offline' if self.config_manager.is_offline_mode() else 'online'
            
            # Determine processing function based on source type
            if source_type == 'file' or (source_type is None and os.path.exists(source)):
                process_func = self.process_file
                process_args = (source, output_format)
            else:
                process_func = self.process_text
                process_args = (source, output_format)
            
            # Try processing with current mode
            try:
                logger.info(f"Attempting processing in {current_mode} mode")
                result = process_func(*process_args)
                
                processing_attempts.append({
                    'mode': current_mode,
                    'success': True,
                    'message': f'Successfully processed in {current_mode} mode'
                })
                
                # Add mode information to result
                result['processing_mode'] = current_mode
                result['mode_detection'] = mode_detection
                result['processing_attempts'] = processing_attempts
                result['graceful_degradation'] = False
                
                return result
            
            except Exception as e:
                processing_attempts.append({
                    'mode': current_mode,
                    'success': False,
                    'error': str(e)
                })
                
                logger.warning(f"Processing failed in {current_mode} mode: {e}")
                
                # Try fallback mode
                fallback_mode = 'offline' if current_mode == 'online' else 'online'
                
                # Check if fallback mode is viable
                if fallback_mode == 'offline':
                    # Check if offline capabilities are available
                    offline_capabilities = self.get_offline_capabilities()
                    if not offline_capabilities.get('offline_processing_available', False):
                        raise RuntimeError("Offline processing not available and online processing failed")
                
                logger.info(f"Attempting fallback to {fallback_mode} mode")
                
                # Temporarily switch mode
                original_mode = self.config_manager.is_offline_mode()
                self.config_manager.set_offline_mode(fallback_mode == 'offline')
                
                try:
                    result = process_func(*process_args)
                    
                    processing_attempts.append({
                        'mode': fallback_mode,
                        'success': True,
                        'message': f'Successfully processed in {fallback_mode} mode (fallback)'
                    })
                    
                    # Add mode information to result
                    result['processing_mode'] = fallback_mode
                    result['mode_detection'] = mode_detection
                    result['processing_attempts'] = processing_attempts
                    result['graceful_degradation'] = True
                    result['fallback_used'] = True
                    
                    logger.info(f"Graceful degradation successful: {current_mode} -> {fallback_mode}")
                    
                    return result
                
                finally:
                    # Restore original mode
                    self.config_manager.set_offline_mode(original_mode)
        
        except Exception as e:
            processing_attempts.append({
                'mode': 'fallback',
                'success': False,
                'error': str(e)
            })
            
            error_msg = f"Processing failed in all modes: {e}"
            logger.error(error_msg)
            
            return {
                'success': False,
                'error': error_msg,
                'processing_attempts': processing_attempts,
                'graceful_degradation': True,
                'fallback_failed': True
            }
    
    def get_feature_availability(self) -> Dict[str, Any]:
        """
        Get availability of features based on current mode and capabilities.
        
        Returns:
            Dict[str, Any]: Feature availability information
        """
        try:
            current_mode = 'offline' if self.config_manager.is_offline_mode() else 'online'
            capabilities = self.config_manager.mode_detector.get_mode_capabilities(
                self.config_manager.is_offline_mode()
            )
            
            # Get offline-specific capabilities
            offline_capabilities = self.get_offline_capabilities()
            
            # Get privacy features availability
            privacy_status = self.get_comprehensive_privacy_status()
            
            return {
                'current_mode': current_mode,
                'mode_indicator': self.config_manager.get_mode_indicator(),
                'basic_features': {
                    'transcript_processing': True,  # Always available
                    'mom_generation': capabilities.get('llm_processing', False) or capabilities.get('simple_extraction', False),
                    'file_processing': capabilities.get('file_processing', True),
                    'basic_formatting': capabilities.get('basic_formatting', True)
                },
                'advanced_features': {
                    'llm_processing': capabilities.get('llm_processing', False),
                    'sentiment_analysis': capabilities.get('llm_processing', False),
                    'multi_language': capabilities.get('llm_processing', False),
                    'collaboration': capabilities.get('collaboration', False),
                    'external_integrations': capabilities.get('external_integrations', False),
                    'real_time_features': capabilities.get('real_time_features', False)
                },
                'offline_features': {
                    'local_processing': offline_capabilities.get('offline_processing_available', False),
                    'cached_models': offline_capabilities.get('cached_model_count', 0) > 0,
                    'simple_extraction': True  # Always available as fallback
                },
                'privacy_features': {
                    'data_anonymization': privacy_status.get('combined_status', {}).get('anonymize_data', False),
                    'secure_deletion': True,
                    'data_export': True,
                    'privacy_reports': True,
                    'offline_processing': current_mode == 'offline'
                },
                'degradation_available': True  # Graceful degradation is always available
            }
        
        except Exception as e:
            logger.error(f"Error getting feature availability: {e}")
            return {
                'error': str(e),
                'basic_features': {'transcript_processing': True},  # Minimal fallback
                'degradation_available': False
            }
    
    def health_check(self) -> Dict[str, Any]:
        """
        Perform comprehensive health check of the application.
        
        Returns:
            Dict[str, Any]: Health check results
        """
        try:
            health_status = {
                'timestamp': datetime.now().isoformat(),
                'overall_status': 'healthy',
                'issues': [],
                'warnings': []
            }
            
            # Check configuration
            try:
                config_status = self.config_manager.get_system_status()
                health_status['configuration'] = {
                    'status': 'healthy',
                    'mode': config_status.get('current_mode', 'unknown'),
                    'connectivity': config_status.get('connectivity', {})
                }
            except Exception as e:
                health_status['configuration'] = {'status': 'error', 'error': str(e)}
                health_status['issues'].append(f"Configuration error: {e}")
            
            # Check offline capabilities
            try:
                offline_status = self.get_offline_capabilities()
                health_status['offline_capabilities'] = {
                    'status': 'healthy' if offline_status.get('offline_processing_available', False) else 'limited',
                    'cached_models': offline_status.get('cached_model_count', 0),
                    'cache_usage': offline_status.get('cache_usage', {})
                }
                
                if offline_status.get('cached_model_count', 0) == 0:
                    health_status['warnings'].append("No offline models cached - limited offline functionality")
            
            except Exception as e:
                health_status['offline_capabilities'] = {'status': 'error', 'error': str(e)}
                health_status['issues'].append(f"Offline capabilities error: {e}")
            
            # Check privacy features
            try:
                privacy_status = self.get_comprehensive_privacy_status()
                health_status['privacy'] = {
                    'status': 'healthy',
                    'privacy_mode': privacy_status.get('combined_status', {}).get('privacy_mode', False),
                    'auto_delete': privacy_status.get('combined_status', {}).get('auto_delete_enabled', False)
                }
            except Exception as e:
                health_status['privacy'] = {'status': 'error', 'error': str(e)}
                health_status['issues'].append(f"Privacy features error: {e}")
            
            # Check feature availability
            try:
                features = self.get_feature_availability()
                health_status['features'] = {
                    'status': 'healthy',
                    'basic_available': features.get('basic_features', {}).get('mom_generation', False),
                    'advanced_available': any(features.get('advanced_features', {}).values()),
                    'degradation_available': features.get('degradation_available', False)
                }
                
                if not features.get('basic_features', {}).get('mom_generation', False):
                    health_status['issues'].append("Basic MoM generation not available")
            
            except Exception as e:
                health_status['features'] = {'status': 'error', 'error': str(e)}
                health_status['issues'].append(f"Feature availability error: {e}")
            
            # Determine overall status
            if health_status['issues']:
                health_status['overall_status'] = 'unhealthy'
            elif health_status['warnings']:
                health_status['overall_status'] = 'degraded'
            
            return health_status
        
        except Exception as e:
            logger.error(f"Error performing health check: {e}")
            return {
                'timestamp': datetime.now().isoformat(),
                'overall_status': 'error',
                'error': str(e)
            }