"""
Test cases for ConfigManager with offline mode support.
"""

import os
import json
import tempfile
import unittest
from unittest.mock import patch, MagicMock

import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), '..', 'app'))

from core.main_app import ConfigManager
from utils.config_utils import NetworkChecker, ModeDetector, PrivacyManager, ConfigValidator


class TestConfigManagerOffline(unittest.TestCase):
    """Test cases for ConfigManager offline mode functionality."""
    
    def setUp(self):
        """Set up test fixtures."""
        self.temp_dir = tempfile.mkdtemp()
        self.config_path = os.path.join(self.temp_dir, 'test_config.json')
        self.config_manager = ConfigManager(self.config_path)
    
    def tearDown(self):
        """Clean up test fixtures."""
        import shutil
        shutil.rmtree(self.temp_dir, ignore_errors=True)
    
    def test_default_config_creation(self):
        """Test that default configuration is created with offline mode settings."""
        config = self.config_manager.config
        
        # Check offline mode settings exist
        self.assertIn('offline_mode', config)
        self.assertIn('auto_detect_mode', config)
        self.assertIn('offline_settings', config)
        self.assertIn('data_retention_days', config)
        self.assertIn('auto_delete_transcripts', config)
        self.assertIn('privacy_mode', config)
        
        # Check default values
        self.assertFalse(config['offline_mode'])
        self.assertTrue(config['auto_detect_mode'])
        self.assertEqual(config['data_retention_days'], 30)
        self.assertFalse(config['auto_delete_transcripts'])
        self.assertFalse(config['privacy_mode'])
    
    def test_offline_mode_toggle(self):
        """Test offline mode toggle functionality."""
        # Initially should be online
        self.assertFalse(self.config_manager.is_offline_mode())
        
        # Toggle to offline
        result = self.config_manager.toggle_offline_mode()
        self.assertTrue(result)
        self.assertTrue(self.config_manager.is_offline_mode())
        
        # Toggle back to online
        result = self.config_manager.toggle_offline_mode()
        self.assertFalse(result)
        self.assertFalse(self.config_manager.is_offline_mode())
    
    def test_set_offline_mode(self):
        """Test setting offline mode explicitly."""
        # Set to offline
        self.config_manager.set_offline_mode(True)
        self.assertTrue(self.config_manager.is_offline_mode())
        self.assertTrue(self.config_manager.config['offline_mode'])
        
        # Set to online
        self.config_manager.set_offline_mode(False)
        self.assertFalse(self.config_manager.is_offline_mode())
        self.assertFalse(self.config_manager.config['offline_mode'])
    
    def test_mode_indicators(self):
        """Test mode indicator functionality."""
        # Disable auto mode first
        self.config_manager.config['auto_detect_mode'] = False
        
        # Test online mode indicator
        self.config_manager.set_offline_mode(False)
        indicator = self.config_manager.get_mode_indicator()
        self.assertIn('Online', indicator)
        
        # Test offline mode indicator
        self.config_manager.set_offline_mode(True)
        indicator = self.config_manager.get_mode_indicator()
        self.assertIn('Offline', indicator)
        
        # Test auto mode indicator
        self.config_manager.config['auto_detect_mode'] = True
        indicator = self.config_manager.get_mode_indicator()
        self.assertIn('Auto', indicator)
    
    @patch('utils.config_utils.NetworkChecker.is_internet_available')
    @patch('utils.config_utils.NetworkChecker.is_ollama_server_available')
    def test_auto_detect_mode(self, mock_ollama, mock_internet):
        """Test automatic mode detection."""
        # Enable auto-detection
        self.config_manager.config['auto_detect_mode'] = True
        
        # Test online scenario
        mock_internet.return_value = True
        mock_ollama.return_value = True
        result = self.config_manager.auto_detect_mode()
        self.assertTrue(result)  # Should be online
        self.assertFalse(self.config_manager.is_offline_mode())
        
        # Test offline scenario (no internet)
        mock_internet.return_value = False
        mock_ollama.return_value = False
        result = self.config_manager.auto_detect_mode()
        self.assertFalse(result)  # Should be offline
        self.assertTrue(self.config_manager.is_offline_mode())
        
        # Test offline scenario (internet but no Ollama)
        mock_internet.return_value = True
        mock_ollama.return_value = False
        result = self.config_manager.auto_detect_mode()
        self.assertFalse(result)  # Should be offline
        self.assertTrue(self.config_manager.is_offline_mode())
    
    def test_offline_settings(self):
        """Test offline settings management."""
        # Get default offline settings
        settings = self.config_manager.get_offline_settings()
        self.assertIn('enable_local_llm', settings)
        self.assertIn('model_cache_dir', settings)
        self.assertIn('max_cache_size_gb', settings)
        
        # Update offline settings
        new_settings = {
            'enable_local_llm': False,
            'max_cache_size_gb': 5
        }
        self.config_manager.update_offline_settings(new_settings)
        
        updated_settings = self.config_manager.get_offline_settings()
        self.assertFalse(updated_settings['enable_local_llm'])
        self.assertEqual(updated_settings['max_cache_size_gb'], 5)
    
    def test_data_retention_settings(self):
        """Test data retention settings."""
        # Test default retention period
        self.assertEqual(self.config_manager.get_data_retention_days(), 30)
        
        # Test auto-delete setting
        self.assertFalse(self.config_manager.is_auto_delete_enabled())
        
        # Test privacy mode
        self.assertFalse(self.config_manager.is_privacy_mode_enabled())
        
        # Update settings
        self.config_manager.set('data_retention_days', 7)
        self.config_manager.set('auto_delete_transcripts', True)
        self.config_manager.set('privacy_mode', True)
        
        self.assertEqual(self.config_manager.get_data_retention_days(), 7)
        self.assertTrue(self.config_manager.is_auto_delete_enabled())
        self.assertTrue(self.config_manager.is_privacy_mode_enabled())
    
    def test_config_persistence(self):
        """Test that configuration changes are persisted."""
        # Make changes
        self.config_manager.set_offline_mode(True)
        self.config_manager.set('data_retention_days', 14)
        
        # Save configuration
        success = self.config_manager.save()
        self.assertTrue(success)
        
        # Create new config manager with same path
        new_config_manager = ConfigManager(self.config_path)
        
        # Verify changes were persisted
        self.assertTrue(new_config_manager.is_offline_mode())
        self.assertEqual(new_config_manager.get_data_retention_days(), 14)


class TestNetworkChecker(unittest.TestCase):
    """Test cases for NetworkChecker utility."""
    
    @patch('socket.create_connection')
    def test_internet_availability(self, mock_connection):
        """Test internet connectivity checking."""
        # Test successful connection
        mock_connection.return_value = MagicMock()
        self.assertTrue(NetworkChecker.is_internet_available())
        
        # Test failed connection
        mock_connection.side_effect = OSError("Connection failed")
        self.assertFalse(NetworkChecker.is_internet_available())
    
    @patch('requests.get')
    def test_ollama_server_availability(self, mock_get):
        """Test Ollama server availability checking."""
        # Test successful response
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_get.return_value = mock_response
        self.assertTrue(NetworkChecker.is_ollama_server_available())
        
        # Test failed response
        mock_response.status_code = 500
        mock_get.return_value = mock_response
        self.assertFalse(NetworkChecker.is_ollama_server_available())
        
        # Test connection error
        mock_get.side_effect = Exception("Connection error")
        self.assertFalse(NetworkChecker.is_ollama_server_available())
    
    @patch('utils.config_utils.NetworkChecker.is_internet_available')
    @patch('utils.config_utils.NetworkChecker.is_ollama_server_available')
    def test_connectivity_status(self, mock_ollama, mock_internet):
        """Test comprehensive connectivity status."""
        mock_internet.return_value = True
        mock_ollama.return_value = True
        
        status = NetworkChecker.get_connectivity_status()
        
        self.assertIn('internet', status)
        self.assertIn('ollama_server', status)
        self.assertIn('local_processing_available', status)
        self.assertTrue(status['internet'])
        self.assertTrue(status['ollama_server'])
        self.assertTrue(status['local_processing_available'])


class TestModeDetector(unittest.TestCase):
    """Test cases for ModeDetector utility."""
    
    def setUp(self):
        """Set up test fixtures."""
        self.config = {
            'auto_detect_mode': True,
            'offline_mode': False,
            'privacy_mode': False,
            'enable_collaboration': False,
            'offline_settings': {
                'enable_local_llm': True
            }
        }
        self.mode_detector = ModeDetector(self.config)
    
    @patch('utils.config_utils.NetworkChecker.get_connectivity_status')
    def test_detect_optimal_mode(self, mock_connectivity):
        """Test optimal mode detection."""
        # Test online scenario
        mock_connectivity.return_value = {
            'internet': True,
            'ollama_server': True,
            'local_processing_available': True
        }
        
        offline_mode, reason = self.mode_detector.detect_optimal_mode()
        self.assertFalse(offline_mode)
        self.assertIn('available', reason)
        
        # Test offline scenario (no internet)
        mock_connectivity.return_value = {
            'internet': False,
            'ollama_server': False,
            'local_processing_available': True
        }
        
        offline_mode, reason = self.mode_detector.detect_optimal_mode()
        self.assertTrue(offline_mode)
        self.assertIn('internet', reason)
    
    def test_mode_capabilities_online(self):
        """Test capabilities in online mode."""
        capabilities = self.mode_detector.get_mode_capabilities(offline_mode=False)
        
        self.assertTrue(capabilities['llm_processing'])
        self.assertTrue(capabilities['file_processing'])
        self.assertTrue(capabilities['external_integrations'])
        self.assertTrue(capabilities['cloud_storage'])
    
    def test_mode_capabilities_offline(self):
        """Test capabilities in offline mode."""
        capabilities = self.mode_detector.get_mode_capabilities(offline_mode=True)
        
        self.assertTrue(capabilities['simple_extraction'])
        self.assertTrue(capabilities['file_processing'])
        self.assertFalse(capabilities['collaboration'])
        self.assertFalse(capabilities['external_integrations'])
        self.assertFalse(capabilities['cloud_storage'])
    
    def test_privacy_mode_preference(self):
        """Test that privacy mode forces offline mode."""
        self.config['privacy_mode'] = True
        
        offline_mode, reason = self.mode_detector.detect_optimal_mode()
        self.assertTrue(offline_mode)
        self.assertIn('Privacy', reason)


class TestPrivacyManager(unittest.TestCase):
    """Test cases for PrivacyManager utility."""
    
    def setUp(self):
        """Set up test fixtures."""
        self.temp_dir = tempfile.mkdtemp()
        self.config = {
            'auto_delete_transcripts': True,
            'data_retention_days': 1,  # Short retention for testing
            'privacy_mode': False,
            'offline_mode': False
        }
        
        # Mock the data directory to use temp directory
        with patch('os.path.expanduser', return_value=self.temp_dir):
            self.privacy_manager = PrivacyManager(self.config)
    
    def tearDown(self):
        """Clean up test fixtures."""
        import shutil
        shutil.rmtree(self.temp_dir, ignore_errors=True)
    
    def test_retention_settings(self):
        """Test retention settings."""
        self.assertTrue(self.privacy_manager.should_auto_delete())
        self.assertEqual(self.privacy_manager.get_retention_period(), 1)
    
    def test_privacy_status(self):
        """Test privacy status reporting."""
        status = self.privacy_manager.get_privacy_status()
        
        self.assertIn('privacy_mode', status)
        self.assertIn('auto_delete_enabled', status)
        self.assertIn('retention_days', status)
        self.assertIn('data_directory', status)
        self.assertIn('offline_mode', status)
    
    def test_secure_file_deletion(self):
        """Test secure file deletion."""
        # Create a test file
        test_file = os.path.join(self.temp_dir, 'test_file.txt')
        with open(test_file, 'w') as f:
            f.write('sensitive data')
        
        # Verify file exists
        self.assertTrue(os.path.exists(test_file))
        
        # Securely delete file
        success = self.privacy_manager.secure_delete_file(test_file)
        self.assertTrue(success)
        self.assertFalse(os.path.exists(test_file))
    
    def test_cleanup_old_data_disabled(self):
        """Test cleanup when auto-delete is disabled."""
        self.config['auto_delete_transcripts'] = False
        privacy_manager = PrivacyManager(self.config)
        
        result = privacy_manager.cleanup_old_data()
        self.assertFalse(result['cleaned'])
        self.assertIn('disabled', result['reason'])


class TestConfigValidator(unittest.TestCase):
    """Test cases for ConfigValidator utility."""
    
    def test_valid_offline_config(self):
        """Test validation of valid offline configuration."""
        config = {
            'offline_settings': {
                'model_cache_dir': tempfile.mkdtemp(),
                'max_cache_size_gb': 10
            },
            'data_retention_days': 30
        }
        
        is_valid, errors = ConfigValidator.validate_offline_config(config)
        self.assertTrue(is_valid)
        self.assertEqual(len(errors), 0)
    
    def test_invalid_offline_config(self):
        """Test validation of invalid offline configuration."""
        config = {
            'offline_settings': {
                'max_cache_size_gb': -5  # Invalid negative value
            },
            'data_retention_days': 0  # Invalid zero value
        }
        
        is_valid, errors = ConfigValidator.validate_offline_config(config)
        self.assertFalse(is_valid)
        self.assertGreater(len(errors), 0)
    
    def test_valid_privacy_config(self):
        """Test validation of valid privacy configuration."""
        config = {
            'privacy_mode': True,
            'auto_delete_transcripts': False,
            'offline_mode': True
        }
        
        is_valid, errors = ConfigValidator.validate_privacy_config(config)
        self.assertTrue(is_valid)
        self.assertEqual(len(errors), 0)
    
    def test_invalid_privacy_config(self):
        """Test validation of invalid privacy configuration."""
        config = {
            'privacy_mode': 'yes',  # Should be boolean
            'auto_delete_transcripts': 1,  # Should be boolean
            'offline_mode': 'true'  # Should be boolean
        }
        
        is_valid, errors = ConfigValidator.validate_privacy_config(config)
        self.assertFalse(is_valid)
        self.assertGreater(len(errors), 0)


if __name__ == '__main__':
    unittest.main()