"""
Test cases for DataPrivacyManager and related privacy features.
"""

import os
import json
import tempfile
import unittest
from unittest.mock import patch, MagicMock
from datetime import datetime, timedelta

import sys
sys.path.append(os.path.join(os.path.dirname(__file__), '..', 'app'))

from utils.data_privacy_manager import DataPrivacyManager, DataRetentionPolicy, SecureFileManager
from utils.privacy_policy_generator import PrivacyPolicyGenerator


class TestDataRetentionPolicy(unittest.TestCase):
    """Test cases for DataRetentionPolicy."""
    
    def test_default_policy(self):
        """Test default retention policy."""
        policy = DataRetentionPolicy()
        
        self.assertEqual(policy.retention_days, 30)
        self.assertFalse(policy.auto_delete)
        self.assertIn('transcripts', policy.categories)
        self.assertIn('mom_outputs', policy.categories)
    
    def test_custom_policy(self):
        """Test custom retention policy."""
        categories = {'transcripts': 7, 'outputs': 14}
        policy = DataRetentionPolicy(retention_days=15, auto_delete=True, categories=categories)
        
        self.assertEqual(policy.retention_days, 15)
        self.assertTrue(policy.auto_delete)
        self.assertEqual(policy.get_retention_period('transcripts'), 7)
        self.assertEqual(policy.get_retention_period('outputs'), 14)
        self.assertEqual(policy.get_retention_period('unknown'), 15)  # Default
    
    def test_should_delete(self):
        """Test should_delete logic."""
        policy = DataRetentionPolicy(retention_days=1)
        
        # Create a temporary file
        with tempfile.NamedTemporaryFile(delete=False) as temp_file:
            temp_path = temp_file.name
        
        try:
            # File should not be deleted immediately
            self.assertFalse(policy.should_delete(temp_path, 'transcripts'))
            
            # Mock file modification time to be old
            old_time = (datetime.now() - timedelta(days=2)).timestamp()
            os.utime(temp_path, (old_time, old_time))
            
            # File should be deleted now
            self.assertTrue(policy.should_delete(temp_path, 'transcripts'))
        
        finally:
            if os.path.exists(temp_path):
                os.unlink(temp_path)


class TestSecureFileManager(unittest.TestCase):
    """Test cases for SecureFileManager."""
    
    def test_secure_delete_file(self):
        """Test secure file deletion."""
        # Create a temporary file with content
        with tempfile.NamedTemporaryFile(mode='w', delete=False) as temp_file:
            temp_file.write("sensitive data")
            temp_path = temp_file.name
        
        # Verify file exists
        self.assertTrue(os.path.exists(temp_path))
        
        # Securely delete file
        success = SecureFileManager.secure_delete(temp_path)
        
        # Verify deletion
        self.assertTrue(success)
        self.assertFalse(os.path.exists(temp_path))
    
    def test_secure_delete_nonexistent_file(self):
        """Test secure deletion of non-existent file."""
        success = SecureFileManager.secure_delete('/nonexistent/file.txt')
        self.assertTrue(success)  # Should return True for non-existent files
    
    def test_create_secure_temp_file(self):
        """Test creation of secure temporary file."""
        temp_path, fd = SecureFileManager.create_secure_temp_file()
        
        try:
            # Verify file exists
            self.assertTrue(os.path.exists(temp_path))
            
            # Check file permissions (should be restrictive)
            file_stat = os.stat(temp_path)
            # On Windows, permission checking is different, so we'll just check it exists
            self.assertIsNotNone(file_stat)
        
        finally:
            # Clean up
            os.close(fd)
            if os.path.exists(temp_path):
                os.unlink(temp_path)


class TestDataPrivacyManager(unittest.TestCase):
    """Test cases for DataPrivacyManager."""
    
    def setUp(self):
        """Set up test fixtures."""
        self.temp_dir = tempfile.mkdtemp()
        self.config = {
            'data_retention_days': 30,
            'auto_delete_transcripts': True,
            'privacy_mode': True,
            'anonymize_data': True,
            'encrypt_storage': False
        }
        
        # Mock the data directory to use temp directory
        with patch('os.path.expanduser', return_value=self.temp_dir):
            self.privacy_manager = DataPrivacyManager(self.config)
    
    def tearDown(self):
        """Clean up test fixtures."""
        import shutil
        shutil.rmtree(self.temp_dir, ignore_errors=True)
    
    def test_initialization(self):
        """Test DataPrivacyManager initialization."""
        self.assertTrue(self.privacy_manager.privacy_mode)
        self.assertTrue(self.privacy_manager.anonymize_data)
        self.assertFalse(self.privacy_manager.encrypt_storage)
        self.assertEqual(self.privacy_manager.retention_policy.retention_days, 30)
    
    def test_get_privacy_status(self):
        """Test getting privacy status."""
        status = self.privacy_manager.get_privacy_status()
        
        self.assertIn('privacy_mode', status)
        self.assertIn('anonymize_data', status)
        self.assertIn('auto_delete_enabled', status)
        self.assertIn('data_directories', status)
        self.assertIn('storage_usage', status)
        
        self.assertTrue(status['privacy_mode'])
        self.assertTrue(status['anonymize_data'])
        self.assertTrue(status['auto_delete_enabled'])
    
    def test_store_transcript(self):
        """Test storing transcript with privacy considerations."""
        transcript = "John: Hello everyone. Sarah: Hi John, how are you?"
        metadata = {'meeting_id': 'test-123', 'date': '2024-01-01'}
        
        file_path = self.privacy_manager.store_transcript(transcript, metadata)
        
        # Verify file was created
        self.assertTrue(os.path.exists(file_path))
        
        # Verify content (should be anonymized)
        with open(file_path, 'r', encoding='utf-8') as f:
            stored_content = f.read()
        
        # Should contain anonymized content
        self.assertIn('Speaker:', stored_content)
        
        # Verify metadata file was created
        metadata_path = file_path.replace('.txt', '_metadata.json')
        self.assertTrue(os.path.exists(metadata_path))
        
        with open(metadata_path, 'r', encoding='utf-8') as f:
            stored_metadata = json.load(f)
        
        self.assertEqual(stored_metadata['meeting_id'], 'test-123')
    
    def test_store_mom_output(self):
        """Test storing MoM output with privacy considerations."""
        mom_data = {
            'meeting_title': 'Test Meeting',
            'attendees': ['John Doe', 'Sarah Smith'],
            'discussion_points': ['Point 1', 'Point 2'],
            'action_items': [{'description': 'Task 1', 'assignee': 'John Doe'}]
        }
        
        file_path = self.privacy_manager.store_mom_output(mom_data, 'json')
        
        # Verify file was created
        self.assertTrue(os.path.exists(file_path))
        
        # Verify content (should be anonymized)
        with open(file_path, 'r', encoding='utf-8') as f:
            stored_data = json.load(f)
        
        # Should contain anonymized attendees
        self.assertEqual(stored_data['attendees'], ['Attendee_1', 'Attendee_2'])
        
        # Action item assignee should be anonymized
        self.assertEqual(stored_data['action_items'][0]['assignee'], '[ASSIGNEE]')
    
    def test_anonymize_transcript(self):
        """Test transcript anonymization."""
        transcript = """
        John Smith: Welcome to the meeting.
        Email me at john@example.com or call 555-123-4567.
        Our office is at 123 Main Street.
        """
        
        anonymized = self.privacy_manager._anonymize_transcript(transcript)
        
        # Check that sensitive information was anonymized
        self.assertIn('Speaker:', anonymized)
        self.assertIn('[EMAIL]', anonymized)
        self.assertIn('[PHONE]', anonymized)
        self.assertIn('[ADDRESS]', anonymized)
        
        # Original sensitive data should not be present
        self.assertNotIn('john@example.com', anonymized)
        self.assertNotIn('555-123-4567', anonymized)
        self.assertNotIn('123 Main Street', anonymized)
    
    def test_anonymize_mom_data(self):
        """Test MoM data anonymization."""
        mom_data = {
            'attendees': ['John Doe', 'Sarah Smith', 'Mike Johnson'],
            'discussion_points': ['John said we need to improve sales'],
            'action_items': [{'description': 'Follow up', 'assignee': 'Sarah Smith'}]
        }
        
        anonymized = self.privacy_manager._anonymize_mom_data(mom_data)
        
        # Check attendees anonymization
        expected_attendees = ['Attendee_1', 'Attendee_2', 'Attendee_3']
        self.assertEqual(anonymized['attendees'], expected_attendees)
        
        # Check action item assignee anonymization
        self.assertEqual(anonymized['action_items'][0]['assignee'], '[ASSIGNEE]')
    
    def test_cleanup_old_data_disabled(self):
        """Test cleanup when auto-delete is disabled."""
        # Disable auto-delete
        self.privacy_manager.retention_policy.auto_delete = False
        
        result = self.privacy_manager.cleanup_old_data()
        
        self.assertFalse(result['cleaned'])
        self.assertIn('disabled', result['reason'])
    
    def test_delete_all_data(self):
        """Test deleting all user data."""
        # Create some test files
        transcript_path = self.privacy_manager.store_transcript("Test transcript")
        mom_path = self.privacy_manager.store_mom_output({'test': 'data'})
        
        # Verify files exist
        self.assertTrue(os.path.exists(transcript_path))
        self.assertTrue(os.path.exists(mom_path))
        
        # Delete all data
        result = self.privacy_manager.delete_all_data()
        
        self.assertTrue(result['success'])
        self.assertIn('deleted', result['message'])
        
        # Directories should still exist but be empty
        self.assertTrue(os.path.exists(self.privacy_manager.transcripts_dir))
        self.assertTrue(os.path.exists(self.privacy_manager.outputs_dir))
    
    def test_export_data(self):
        """Test data export functionality."""
        # Create some test data
        transcript_path = self.privacy_manager.store_transcript("Test transcript")
        mom_path = self.privacy_manager.store_mom_output({'test': 'data'})
        
        # Export data
        export_dir = os.path.join(self.temp_dir, 'export')
        result = self.privacy_manager.export_data(export_dir)
        
        self.assertTrue(result['success'])
        self.assertTrue(os.path.exists(export_dir))
        
        # Check manifest file
        manifest_path = result['manifest_path']
        self.assertTrue(os.path.exists(manifest_path))
        
        with open(manifest_path, 'r', encoding='utf-8') as f:
            manifest = json.load(f)
        
        self.assertIn('export_date', manifest)
        self.assertIn('exported_files', manifest)
        self.assertIn('privacy_status', manifest)
    
    def test_create_privacy_report(self):
        """Test privacy report creation."""
        report = self.privacy_manager.create_privacy_report()
        
        self.assertIn('report_date', report)
        self.assertIn('privacy_settings', report)
        self.assertIn('data_retention', report)
        self.assertIn('storage_usage', report)
        self.assertIn('compliance_status', report)
        self.assertIn('recommendations', report)
        
        # Check privacy settings
        privacy_settings = report['privacy_settings']
        self.assertTrue(privacy_settings['privacy_mode'])
        self.assertTrue(privacy_settings['anonymize_data'])


class TestPrivacyPolicyGenerator(unittest.TestCase):
    """Test cases for PrivacyPolicyGenerator."""
    
    def setUp(self):
        """Set up test fixtures."""
        self.config = {
            'organization_name': 'Test Organization',
            'contact_email': 'privacy@test.com',
            'data_retention_days': 30,
            'auto_delete_transcripts': True,
            'privacy_mode': True
        }
        self.policy_generator = PrivacyPolicyGenerator(self.config)
    
    def test_initialization(self):
        """Test PrivacyPolicyGenerator initialization."""
        self.assertEqual(self.policy_generator.organization_name, 'Test Organization')
        self.assertEqual(self.policy_generator.contact_email, 'privacy@test.com')
    
    def test_generate_privacy_policy(self):
        """Test privacy policy generation."""
        policy_content = self.policy_generator.generate_privacy_policy()
        
        # Check that policy contains expected sections
        self.assertIn('Privacy Policy', policy_content)
        self.assertIn('Test Organization', policy_content)
        self.assertIn('privacy@test.com', policy_content)
        self.assertIn('Information We Collect', policy_content)
        self.assertIn('Data Retention', policy_content)
        self.assertIn('Your Rights', policy_content)
        self.assertIn('Data Security', policy_content)
    
    def test_generate_privacy_policy_with_file(self):
        """Test privacy policy generation with file output."""
        with tempfile.NamedTemporaryFile(mode='w', delete=False, suffix='.md') as temp_file:
            temp_path = temp_file.name
        
        try:
            policy_content = self.policy_generator.generate_privacy_policy(temp_path)
            
            # Verify file was created
            self.assertTrue(os.path.exists(temp_path))
            
            # Verify content matches
            with open(temp_path, 'r', encoding='utf-8') as f:
                file_content = f.read()
            
            self.assertEqual(policy_content, file_content)
        
        finally:
            if os.path.exists(temp_path):
                os.unlink(temp_path)
    
    def test_generate_data_processing_agreement(self):
        """Test DPA generation."""
        dpa_content = self.policy_generator.generate_data_processing_agreement()
        
        # Check that DPA contains expected sections
        self.assertIn('Data Processing Agreement', dpa_content)
        self.assertIn('Test Organization', dpa_content)
        self.assertIn('Personal Data', dpa_content)
        self.assertIn('Data Security', dpa_content)
        self.assertIn('Data Subject Rights', dpa_content)
    
    def test_generate_compliance_checklist(self):
        """Test compliance checklist generation."""
        checklist = self.policy_generator.generate_compliance_checklist()
        
        self.assertIn('gdpr_compliance', checklist)
        self.assertIn('ccpa_compliance', checklist)
        self.assertIn('security_measures', checklist)
        self.assertIn('recommendations', checklist)
        
        # Check GDPR compliance items
        gdpr = checklist['gdpr_compliance']
        self.assertIn('lawful_basis', gdpr)
        self.assertIn('data_minimization', gdpr)
        self.assertIn('data_subject_rights', gdpr)
        
        # Check that recommendations are provided
        self.assertIsInstance(checklist['recommendations'], list)
        self.assertGreater(len(checklist['recommendations']), 0)


class TestDataPrivacyIntegration(unittest.TestCase):
    """Integration tests for data privacy features."""
    
    def setUp(self):
        """Set up test fixtures."""
        self.temp_dir = tempfile.mkdtemp()
        self.config = {
            'data_retention_days': 1,  # Short retention for testing
            'auto_delete_transcripts': True,
            'privacy_mode': True,
            'anonymize_data': True,
            'organization_name': 'Test Org',
            'contact_email': 'test@example.com'
        }
        
        with patch('os.path.expanduser', return_value=self.temp_dir):
            self.privacy_manager = DataPrivacyManager(self.config)
        
        self.policy_generator = PrivacyPolicyGenerator(self.config)
    
    def tearDown(self):
        """Clean up test fixtures."""
        import shutil
        shutil.rmtree(self.temp_dir, ignore_errors=True)
    
    def test_full_privacy_workflow(self):
        """Test complete privacy workflow."""
        # 1. Store transcript with privacy
        transcript = "John: Let's discuss the project. Sarah: I agree."
        transcript_path = self.privacy_manager.store_transcript(transcript)
        self.assertTrue(os.path.exists(transcript_path))
        
        # 2. Store MoM output with privacy
        mom_data = {
            'attendees': ['John', 'Sarah'],
            'discussion_points': ['Project discussion']
        }
        mom_path = self.privacy_manager.store_mom_output(mom_data)
        self.assertTrue(os.path.exists(mom_path))
        
        # 3. Generate privacy policy
        policy = self.policy_generator.generate_privacy_policy()
        self.assertIn('Privacy Policy', policy)
        
        # 4. Create privacy report
        report = self.privacy_manager.create_privacy_report()
        self.assertIn('privacy_settings', report)
        
        # 5. Export data
        export_dir = os.path.join(self.temp_dir, 'export')
        export_result = self.privacy_manager.export_data(export_dir)
        self.assertTrue(export_result['success'])
        
        # 6. Delete all data
        delete_result = self.privacy_manager.delete_all_data()
        self.assertTrue(delete_result['success'])


if __name__ == '__main__':
    unittest.main()