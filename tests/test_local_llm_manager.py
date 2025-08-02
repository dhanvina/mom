"""
Test cases for LocalLLMManager.
"""

import os
import json
import tempfile
import unittest
from unittest.mock import patch, MagicMock

import sys
sys.path.append(os.path.join(os.path.dirname(__file__), '..', 'app'))

from utils.local_llm_manager import LocalLLMManager, ModelInfo


class TestModelInfo(unittest.TestCase):
    """Test cases for ModelInfo class."""
    
    def test_model_info_creation(self):
        """Test ModelInfo creation."""
        model = ModelInfo(
            name="test-model",
            size_gb=2.5,
            url="https://example.com/model",
            description="Test model",
            requirements={"ram_gb": 4}
        )
        
        self.assertEqual(model.name, "test-model")
        self.assertEqual(model.size_gb, 2.5)
        self.assertEqual(model.url, "https://example.com/model")
        self.assertEqual(model.description, "Test model")
        self.assertEqual(model.requirements["ram_gb"], 4)
        self.assertFalse(model.downloaded)
        self.assertIsNone(model.cached_path)


class TestLocalLLMManager(unittest.TestCase):
    """Test cases for LocalLLMManager."""
    
    def setUp(self):
        """Set up test fixtures."""
        self.temp_dir = tempfile.mkdtemp()
        self.config = {
            'offline_settings': {
                'model_cache_dir': self.temp_dir,
                'max_cache_size_gb': 10,
                'enable_local_llm': True,
                'fallback_to_simple_extraction': True
            }
        }
        self.llm_manager = LocalLLMManager(self.config)
    
    def tearDown(self):
        """Clean up test fixtures."""
        import shutil
        shutil.rmtree(self.temp_dir, ignore_errors=True)
    
    def test_initialization(self):
        """Test LocalLLMManager initialization."""
        self.assertEqual(self.llm_manager.cache_dir, self.temp_dir)
        self.assertEqual(self.llm_manager.max_cache_size_gb, 10)
        self.assertIsInstance(self.llm_manager.available_models, dict)
        self.assertGreater(len(self.llm_manager.available_models), 0)
    
    def test_available_models(self):
        """Test getting available models."""
        models = self.llm_manager.list_available_models()
        
        self.assertIsInstance(models, list)
        self.assertGreater(len(models), 0)
        
        # Check model structure
        for model in models:
            self.assertIn('name', model)
            self.assertIn('description', model)
            self.assertIn('size_gb', model)
            self.assertIn('requirements', model)
            self.assertIn('cached', model)
    
    @patch('psutil.virtual_memory')
    @patch('shutil.disk_usage')
    def test_get_recommended_model(self, mock_disk_usage, mock_virtual_memory):
        """Test getting recommended model based on system capabilities."""
        # Mock system resources
        mock_virtual_memory.return_value = MagicMock(available=8 * 1024**3)  # 8GB RAM
        mock_disk_usage.return_value = MagicMock(free=20 * 1024**3)  # 20GB disk
        
        recommended = self.llm_manager.get_recommended_model()
        
        self.assertIsNotNone(recommended)
        self.assertIn(recommended, self.llm_manager.available_models)
    
    @patch('psutil.virtual_memory')
    @patch('shutil.disk_usage')
    def test_get_recommended_model_limited_resources(self, mock_disk_usage, mock_virtual_memory):
        """Test getting recommended model with limited system resources."""
        # Mock limited system resources
        mock_virtual_memory.return_value = MagicMock(available=2 * 1024**3)  # 2GB RAM
        mock_disk_usage.return_value = MagicMock(free=1 * 1024**3)  # 1GB disk
        
        recommended = self.llm_manager.get_recommended_model()
        
        # Should recommend the smallest model or None
        if recommended:
            model_info = self.llm_manager.available_models[recommended]
            self.assertLessEqual(model_info.requirements.get('ram_gb', 0), 2)
    
    def test_is_model_cached(self):
        """Test checking if model is cached."""
        # Initially no models should be cached
        self.assertFalse(self.llm_manager.is_model_cached('test-model'))
    
    def test_cache_usage(self):
        """Test getting cache usage information."""
        usage = self.llm_manager.get_cache_usage()
        
        self.assertIn('total_size_gb', usage)
        self.assertIn('max_size_gb', usage)
        self.assertIn('usage_percent', usage)
        self.assertIn('model_count', usage)
        self.assertIn('cache_dir', usage)
        
        self.assertEqual(usage['max_size_gb'], 10)
        self.assertEqual(usage['cache_dir'], self.temp_dir)
        self.assertEqual(usage['model_count'], 0)  # No models cached initially
    
    def test_download_model_success(self):
        """Test successful model download."""
        model_name = 'gemma-2b'  # Use the smallest available model
        
        success, message = self.llm_manager.download_model(model_name)
        
        self.assertTrue(success)
        self.assertIn('successfully', message)
        self.assertTrue(self.llm_manager.is_model_cached(model_name))
        
        # Check that model directory was created
        model_dir = os.path.join(self.temp_dir, model_name)
        self.assertTrue(os.path.exists(model_dir))
        
        # Check that model info file was created
        info_file = os.path.join(model_dir, 'model_info.json')
        self.assertTrue(os.path.exists(info_file))
        
        # Verify model info content
        with open(info_file, 'r') as f:
            info_data = json.load(f)
        
        self.assertEqual(info_data['name'], model_name)
        self.assertIn('size_gb', info_data)
        self.assertIn('downloaded_at', info_data)
    
    def test_download_model_already_cached(self):
        """Test downloading a model that's already cached."""
        model_name = 'gemma-2b'
        
        # Download model first
        self.llm_manager.download_model(model_name)
        
        # Try to download again
        success, message = self.llm_manager.download_model(model_name)
        
        self.assertTrue(success)
        self.assertIn('already cached', message)
    
    def test_download_model_invalid(self):
        """Test downloading an invalid model."""
        success, message = self.llm_manager.download_model('invalid-model')
        
        self.assertFalse(success)
        self.assertIn('not available', message)
    
    def test_remove_model_success(self):
        """Test successful model removal."""
        model_name = 'gemma-2b'
        
        # Download model first
        self.llm_manager.download_model(model_name)
        self.assertTrue(self.llm_manager.is_model_cached(model_name))
        
        # Remove model
        success, message = self.llm_manager.remove_model(model_name)
        
        self.assertTrue(success)
        self.assertIn('successfully', message)
        self.assertFalse(self.llm_manager.is_model_cached(model_name))
    
    def test_remove_model_not_cached(self):
        """Test removing a model that's not cached."""
        success, message = self.llm_manager.remove_model('non-existent-model')
        
        self.assertFalse(success)
        self.assertIn('not cached', message)
    
    def test_process_with_local_model_no_model(self):
        """Test processing with local model when no model is available."""
        success, result = self.llm_manager.process_with_local_model("Test transcript")
        
        # Should use simple extraction fallback
        self.assertTrue(success)
        self.assertIn('Meeting Minutes', result)
        self.assertIn('offline processing', result.lower())
    
    def test_simple_mom_extraction(self):
        """Test simple MoM extraction functionality."""
        transcript = """
        John: Welcome everyone to today's meeting.
        Sarah: Thanks John. Let's discuss the project timeline.
        John: We need to decide on the launch date.
        Sarah: I think we should target next month.
        Action: John will prepare the launch plan by Friday.
        Decision: Launch date set for next month.
        """
        
        result = self.llm_manager._simple_mom_extraction(transcript)
        
        self.assertIn('Meeting Minutes', result)
        self.assertIn('Attendees', result)
        self.assertIn('John', result)
        self.assertIn('Sarah', result)
        self.assertIn('Action Items', result)
        self.assertIn('Decisions', result)
    
    def test_cleanup_cache(self):
        """Test cache cleanup functionality."""
        # Download a model to have something to clean up
        model_name = 'gemma-2b'
        self.llm_manager.download_model(model_name)
        
        # Test cleanup with high target (should not clean anything)
        result = self.llm_manager.cleanup_cache(target_usage_percent=90.0)
        
        self.assertIn('cleaned', result)
        self.assertIn('removed_models', result)
        
        # Since we only have one small model, it likely won't trigger cleanup
        # unless the target is very low
    
    def test_get_status(self):
        """Test getting comprehensive status."""
        status = self.llm_manager.get_status()
        
        self.assertIn('cache_usage', status)
        self.assertIn('available_models', status)
        self.assertIn('cached_model_count', status)
        self.assertIn('recommended_model', status)
        self.assertIn('offline_processing_available', status)
        
        # Should be available due to fallback extraction
        self.assertTrue(status['offline_processing_available'])


class TestLocalLLMManagerIntegration(unittest.TestCase):
    """Integration tests for LocalLLMManager."""
    
    def setUp(self):
        """Set up test fixtures."""
        self.temp_dir = tempfile.mkdtemp()
        self.config = {
            'offline_settings': {
                'model_cache_dir': self.temp_dir,
                'max_cache_size_gb': 5,
                'enable_local_llm': True,
                'fallback_to_simple_extraction': True
            }
        }
        self.llm_manager = LocalLLMManager(self.config)
    
    def tearDown(self):
        """Clean up test fixtures."""
        import shutil
        shutil.rmtree(self.temp_dir, ignore_errors=True)
    
    def test_full_workflow(self):
        """Test complete workflow from model download to processing."""
        model_name = 'gemma-2b'
        
        # 1. Check initial state
        self.assertFalse(self.llm_manager.is_model_cached(model_name))
        
        # 2. Download model
        success, message = self.llm_manager.download_model(model_name)
        self.assertTrue(success)
        self.assertTrue(self.llm_manager.is_model_cached(model_name))
        
        # 3. Process text
        transcript = "John: Let's discuss the project. Sarah: I agree, we need to finalize the timeline."
        success, result = self.llm_manager.process_with_local_model(transcript, model_name)
        self.assertTrue(success)
        self.assertIsInstance(result, str)
        self.assertGreater(len(result), 0)
        
        # 4. Check cache usage
        usage = self.llm_manager.get_cache_usage()
        self.assertGreater(usage['model_count'], 0)
        
        # 5. Remove model
        success, message = self.llm_manager.remove_model(model_name)
        self.assertTrue(success)
        self.assertFalse(self.llm_manager.is_model_cached(model_name))


if __name__ == '__main__':
    unittest.main()