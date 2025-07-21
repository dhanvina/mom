"""
Test cases for MainApp offline support and graceful degradation.
"""

import os
import json
import tempfile
import unittest
from unittest.mock import patch, MagicMock

import sys
sys.path.append(os.path.join(os.path.dirname(__file__), '..', 'app'))

from core.main_app import MainApp


class TestMainAppOfflineSupport(unittest.TestCase):
    """Test cases for MainApp offline support."""
    
    def setUp(self):
        """Set up test fixtures."""
        self.temp_dir = tempfile.mkdtemp()
        self.config_path = os.path.join(self.temp_dir, 'test_config.json')
        
        # Create test configuration
        test_config = {
            'model_name': 'llama3:latest',
            'offline_mode': False,
            'auto_detect_mode': True,
            'privacy_mode': True,
            'data_retention_days': 30,
            'offline_settings': {
                'enable_local_llm': True,
                'fallback_to_simple_extraction': True
            }
        }
        
        with open(self.config_path, 'w') as f:
            json.dump(test_config, f)
        
        self.main_app = MainApp(self.config_path)
    
    def tearDown(self):
        """Clean up test fixtures."""
        import shutil
        shutil.rmtree(self.temp_dir, ignore_errors=True)
    
    def test_initialization_with_offline_support(self):
        """Test MainApp initialization with offline support."""
        self.assertIsNotNone(self.main_app.config_manager)
        self.assertIsNotNone(self.main_app.data_privacy_manager)
        self.assertIsNotNone(self.main_app.privacy_policy_generator)
        
        # Check that offline capabilities are available
        capabilities = self.main_app.get_offline_capabilities()
        self.assertIn('offline_processing_available', capabilities)
    
    @patch('utils.config_utils.NetworkChecker.get_connectivity_status')
    def test_detect_and_set_optimal_mode_online(self, mock_connectivity):
        """Test automatic mode detection when online."""
        # Mock online connectivity
        mock_connectivity.return_value = {
            'internet': True,
            'ollama_server': True,
            'local_processing_available': True
        }
        
        result = self.main_app.detect_and_set_optimal_mode()
        
        self.assertTrue(result['success'])
        self.assertEqual(result['current_mode'], 'online')
        self.assertIn('connectivity', result)
        self.assertIn('capabilities', result)
    
    @patch('utils.config_utils.NetworkChecker.get_connectivity_status')
    def test_detect_and_set_optimal_mode_offline(self, mock_connectivity):
        """Test automatic mode detection when offline."""
        # Mock offline connectivity
        mock_connectivity.return_value = {
            'internet': False,
            'ollama_server': False,
            'local_processing_available': True
        }
        
        result = self.main_app.detect_and_set_optimal_mode()
        
        self.assertTrue(result['success'])
        self.assertEqual(result['current_mode'], 'offline')
        self.assertIn('No internet', result['reason'])
    
    def test_get_feature_availability_online(self):
        """Test feature availability in online mode."""
        # Set to online mode
        self.main_app.config_manager.set_offline_mode(False)
        
        features = self.main_app.get_feature_availability()
        
        self.assertEqual(features['current_mode'], 'online')
        self.assertIn('basic_features', features)
        self.assertIn('advanced_features', features)
        self.assertIn('offline_features', features)
        self.assertIn('privacy_features', features)
        
        # Basic features should always be available
        self.assertTrue(features['basic_features']['transcript_processing'])
    
    def test_get_feature_availability_offline(self):
        """Test feature availability in offline mode."""
        # Set to offline mode
        self.main_app.config_manager.set_offline_mode(True)
        
        features = self.main_app.get_feature_availability()
        
        self.assertEqual(features['current_mode'], 'offline')
        
        # Check that offline-specific features are noted
        self.assertIn('offline_features', features)
        self.assertTrue(features['offline_features']['simple_extraction'])
        
        # Advanced features should be limited in offline mode
        advanced_features = features['advanced_features']
        self.assertFalse(advanced_features.get('collaboration', True))
        self.assertFalse(advanced_features.get('external_integrations', True))
    
    def test_health_check(self):
        """Test comprehensive health check."""
        health = self.main_app.health_check()
        
        self.assertIn('timestamp', health)
        self.assertIn('overall_status', health)
        self.assertIn('configuration', health)
        self.assertIn('offline_capabilities', health)
        self.assertIn('privacy', health)
        self.assertIn('features', health)
        
        # Should have some status (healthy, degraded, or unhealthy)
        self.assertIn(health['overall_status'], ['healthy', 'degraded', 'unhealthy', 'error'])
    
    @patch('core.main_app.MainApp.process_text')
    def test_graceful_degradation_success_first_try(self, mock_process):
        """Test graceful degradation when first attempt succeeds."""
        # Mock successful processing
        mock_process.return_value = {
            'mom_data': {'test': 'data'},
            'output': 'Test output',
            'processing_mode': 'online'
        }
        
        result = self.main_app.process_with_graceful_degradation(
            "Test transcript", 
            source_type='text'
        )
        
        self.assertIn('processing_mode', result)
        self.assertIn('processing_attempts', result)
        self.assertFalse(result.get('graceful_degradation', True))
        
        # Should have one successful attempt
        attempts = result['processing_attempts']
        self.assertEqual(len(attempts), 1)
        self.assertTrue(attempts[0]['success'])
    
    @patch('core.main_app.MainApp.process_text')
    def test_graceful_degradation_fallback_success(self, mock_process):
        """Test graceful degradation when fallback succeeds."""
        # Mock first attempt failure, second attempt success
        mock_process.side_effect = [
            Exception("Online processing failed"),
            {
                'mom_data': {'test': 'data'},
                'output': 'Test output (offline)',
                'processing_mode': 'offline'
            }
        ]
        
        result = self.main_app.process_with_graceful_degradation(
            "Test transcript", 
            source_type='text'
        )
        
        self.assertTrue(result.get('graceful_degradation', False))
        self.assertTrue(result.get('fallback_used', False))
        
        # Should have two attempts
        attempts = result['processing_attempts']
        self.assertEqual(len(attempts), 2)
        self.assertFalse(attempts[0]['success'])  # First failed
        self.assertTrue(attempts[1]['success'])   # Second succeeded
    
    def test_comprehensive_privacy_status(self):
        """Test comprehensive privacy status retrieval."""
        status = self.main_app.get_comprehensive_privacy_status()
        
        self.assertIn('config_privacy', status)
        self.assertIn('data_privacy', status)
        self.assertIn('combined_status', status)
        
        combined = status['combined_status']
        self.assertIn('privacy_mode', combined)
        self.assertIn('offline_mode', combined)
        self.assertIn('auto_delete_enabled', combined)
    
    def test_store_transcript_securely(self):
        """Test secure transcript storage."""
        transcript = "Test meeting transcript"
        metadata = {'meeting_id': 'test-123'}
        
        result = self.main_app.store_transcript_securely(transcript, metadata)
        
        self.assertTrue(result['success'])
        self.assertIn('file_path', result)
        self.assertTrue(os.path.exists(result['file_path']))
    
    def test_store_mom_output_securely(self):
        """Test secure MoM output storage."""
        mom_data = {
            'meeting_title': 'Test Meeting',
            'attendees': ['John', 'Sarah'],
            'discussion_points': ['Point 1', 'Point 2']
        }
        
        result = self.main_app.store_mom_output_securely(mom_data)
        
        self.assertTrue(result['success'])
        self.assertIn('file_path', result)
        self.assertTrue(os.path.exists(result['file_path']))
    
    def test_generate_privacy_policy(self):
        """Test privacy policy generation."""
        result = self.main_app.generate_privacy_policy()
        
        self.assertTrue(result['success'])
        self.assertIn('content', result)
        self.assertIn('Privacy Policy', result['content'])
    
    def test_generate_compliance_report(self):
        """Test compliance report generation."""
        result = self.main_app.generate_compliance_report()
        
        self.assertTrue(result['success'])
        self.assertIn('report', result)
        
        report = result['report']
        self.assertIn('privacy_report', report)
        self.assertIn('compliance_checklist', report)
        self.assertIn('system_status', report)
        self.assertIn('recommendations', report)
    
    def test_offline_model_management(self):
        """Test offline model management features."""
        # List available models
        models = self.main_app.list_offline_models()
        self.assertIsInstance(models, list)
        
        # Get offline capabilities
        capabilities = self.main_app.get_offline_capabilities()
        self.assertIn('offline_processing_available', capabilities)
        
        # Try to set up an offline model (will use mock/placeholder)
        setup_result = self.main_app.setup_offline_model('gemma-2b')
        # This should succeed with the mock implementation
        self.assertIn('success', setup_result)
    
    def test_data_cleanup_comprehensive(self):
        """Test comprehensive data cleanup."""
        # First store some data
        self.main_app.store_transcript_securely("Test transcript")
        self.main_app.store_mom_output_securely({'test': 'data'})
        
        # Then clean up
        result = self.main_app.cleanup_old_data_comprehensive()
        
        self.assertIn('config_cleanup', result)
        self.assertIn('data_cleanup', result)
        self.assertIn('total_deleted', result)
    
    def test_export_user_data(self):
        """Test user data export."""
        # Store some test data first
        self.main_app.store_transcript_securely("Test transcript")
        self.main_app.store_mom_output_securely({'test': 'data'})
        
        # Export data
        export_path = os.path.join(self.temp_dir, 'export')
        result = self.main_app.export_user_data(export_path)
        
        self.assertTrue(result['success'])
        self.assertTrue(os.path.exists(export_path))
    
    def test_delete_all_user_data(self):
        """Test deletion of all user data."""
        # Store some test data first
        self.main_app.store_transcript_securely("Test transcript")
        self.main_app.store_mom_output_securely({'test': 'data'})
        
        # Delete all data
        result = self.main_app.delete_all_user_data()
        
        self.assertTrue(result['success'])
        self.assertIn('deleted', result['message'])


class TestMainAppIntegration(unittest.TestCase):
    """Integration tests for MainApp with offline support."""
    
    def setUp(self):
        """Set up test fixtures."""
        self.temp_dir = tempfile.mkdtemp()
        self.config_path = os.path.join(self.temp_dir, 'test_config.json')
        
        # Create comprehensive test configuration
        test_config = {
            'model_name': 'llama3:latest',
            'offline_mode': False,
            'auto_detect_mode': True,
            'privacy_mode': True,
            'anonymize_data': True,
            'auto_delete_transcripts': True,
            'data_retention_days': 1,  # Short for testing
            'organization_name': 'Test Organization',
            'contact_email': 'test@example.com',
            'offline_settings': {
                'enable_local_llm': True,
                'fallback_to_simple_extraction': True,
                'model_cache_dir': os.path.join(self.temp_dir, 'models')
            }
        }
        
        with open(self.config_path, 'w') as f:
            json.dump(test_config, f)
        
        self.main_app = MainApp(self.config_path)
    
    def tearDown(self):
        """Clean up test fixtures."""
        import shutil
        shutil.rmtree(self.temp_dir, ignore_errors=True)
    
    def test_full_offline_workflow(self):
        """Test complete offline workflow."""
        # 1. Set to offline mode
        self.main_app.config_manager.set_offline_mode(True)
        
        # 2. Check feature availability
        features = self.main_app.get_feature_availability()
        self.assertEqual(features['current_mode'], 'offline')
        
        # 3. Process transcript with offline mode
        transcript = "John: Let's discuss the project. Sarah: I agree with the timeline."
        
        # This should work with simple extraction fallback
        result = self.main_app.process_text(transcript)
        self.assertIn('mom_data', result)
        self.assertEqual(result['processing_mode'], 'offline')
        
        # 4. Store results securely
        store_result = self.main_app.store_mom_output_securely(result['mom_data'])
        self.assertTrue(store_result['success'])
        
        # 5. Generate privacy report
        privacy_result = self.main_app.generate_compliance_report()
        self.assertTrue(privacy_result['success'])
        
        # 6. Perform health check
        health = self.main_app.health_check()
        self.assertIn(health['overall_status'], ['healthy', 'degraded'])
    
    @patch('utils.config_utils.NetworkChecker.get_connectivity_status')
    def test_mode_switching_workflow(self, mock_connectivity):
        """Test workflow with automatic mode switching."""
        # Start online
        mock_connectivity.return_value = {
            'internet': True,
            'ollama_server': True,
            'local_processing_available': True
        }
        
        # Detect mode (should be online)
        mode_result = self.main_app.detect_and_set_optimal_mode()
        self.assertEqual(mode_result['current_mode'], 'online')
        
        # Simulate network loss
        mock_connectivity.return_value = {
            'internet': False,
            'ollama_server': False,
            'local_processing_available': True
        }
        
        # Detect mode again (should switch to offline)
        mode_result = self.main_app.detect_and_set_optimal_mode()
        self.assertEqual(mode_result['current_mode'], 'offline')
        self.assertTrue(mode_result['mode_changed'])
    
    def test_graceful_degradation_workflow(self):
        """Test graceful degradation in realistic scenario."""
        transcript = "Meeting transcript for processing"
        
        # Try processing with graceful degradation
        result = self.main_app.process_with_graceful_degradation(
            transcript, 
            source_type='text'
        )
        
        # Should succeed with some mode
        self.assertIn('processing_mode', result)
        self.assertIn('processing_attempts', result)
        
        # Check that we have processing attempts logged
        attempts = result.get('processing_attempts', [])
        self.assertGreater(len(attempts), 0)
    
    def test_privacy_compliance_workflow(self):
        """Test complete privacy compliance workflow."""
        # 1. Store sensitive data
        sensitive_transcript = "John Smith: My email is john@company.com and phone is 555-1234"
        store_result = self.main_app.store_transcript_securely(sensitive_transcript)
        self.assertTrue(store_result['success'])
        
        # 2. Generate privacy policy
        policy_result = self.main_app.generate_privacy_policy()
        self.assertTrue(policy_result['success'])
        self.assertIn('john@company.com', policy_result['content'])  # Should be in contact info
        
        # 3. Create compliance report
        compliance_result = self.main_app.generate_compliance_report()
        self.assertTrue(compliance_result['success'])
        
        # 4. Export data (GDPR compliance)
        export_path = os.path.join(self.temp_dir, 'gdpr_export')
        export_result = self.main_app.export_user_data(export_path)
        self.assertTrue(export_result['success'])
        
        # 5. Delete all data (right to be forgotten)
        delete_result = self.main_app.delete_all_user_data()
        self.assertTrue(delete_result['success'])


if __name__ == '__main__':
    unittest.main()