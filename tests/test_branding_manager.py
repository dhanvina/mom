"""
Unit tests for the BrandingManager class.
"""

import pytest
import os
import json
import tempfile
import shutil
from unittest.mock import patch, MagicMock
from app.template.branding_manager import BrandingManager
from app.template.template_model import BrandingElement

class TestBrandingManager:
    """Test cases for BrandingManager class."""
    
    def setup_method(self):
        """Set up test fixtures."""
        # Create a temporary directory for branding sets
        self.temp_dir = tempfile.mkdtemp()
        self.branding_manager = BrandingManager(self.temp_dir)
        
        # Create test branding elements
        self.test_branding = [
            BrandingElement(name="logo", type="image", value="test-logo.png", description="Test logo"),
            BrandingElement(name="color", type="color", value="#ff0000", description="Test color")
        ]
    
    def teardown_method(self):
        """Tear down test fixtures."""
        # Remove temporary directory
        shutil.rmtree(self.temp_dir)
    
    def test_init(self):
        """Test initialization."""
        # Verify branding directory
        assert self.branding_manager.branding_dir == self.temp_dir
        
        # Verify branding sets dictionary
        assert isinstance(self.branding_manager.branding_sets, dict)
        assert len(self.branding_manager.branding_sets) == 0
    
    def test_add_branding_set(self):
        """Test adding a branding set."""
        # Add branding set
        self.branding_manager.add_branding_set("Test", self.test_branding)
        
        # Verify branding set was added to memory
        assert "Test" in self.branding_manager.branding_sets
        assert len(self.branding_manager.branding_sets["Test"]) == 2
        assert self.branding_manager.branding_sets["Test"][0].name == "logo"
        assert self.branding_manager.branding_sets["Test"][1].name == "color"
        
        # Verify branding set was saved to file
        file_path = os.path.join(self.temp_dir, "test.json")
        assert os.path.exists(file_path)
        
        # Verify file content
        with open(file_path, 'r', encoding='utf-8') as f:
            data = json.load(f)
            assert data["name"] == "Test"
            assert len(data["elements"]) == 2
            assert data["elements"][0]["name"] == "logo"
            assert data["elements"][1]["name"] == "color"
    
    def test_get_branding_set(self):
        """Test getting a branding set."""
        # Add branding set
        self.branding_manager.add_branding_set("Test", self.test_branding)
        
        # Get branding set
        branding_set = self.branding_manager.get_branding_set("Test")
        
        # Verify branding set
        assert branding_set is not None
        assert len(branding_set) == 2
        assert branding_set[0].name == "logo"
        assert branding_set[1].name == "color"
        
        # Get nonexistent branding set
        branding_set = self.branding_manager.get_branding_set("Nonexistent")
        
        # Verify result is None
        assert branding_set is None
    
    def test_get_branding_sets(self):
        """Test getting all branding sets."""
        # Add branding sets
        self.branding_manager.add_branding_set("Test1", self.test_branding)
        self.branding_manager.add_branding_set("Test2", self.test_branding)
        
        # Get all branding sets
        branding_sets = self.branding_manager.get_branding_sets()
        
        # Verify branding sets
        assert len(branding_sets) == 2
        assert "Test1" in branding_sets
        assert "Test2" in branding_sets
    
    def test_remove_branding_set(self):
        """Test removing a branding set."""
        # Add branding set
        self.branding_manager.add_branding_set("Test", self.test_branding)
        
        # Verify branding set was added
        assert "Test" in self.branding_manager.branding_sets
        
        # Remove branding set
        result = self.branding_manager.remove_branding_set("Test")
        
        # Verify result
        assert result == True
        
        # Verify branding set was removed from memory
        assert "Test" not in self.branding_manager.branding_sets
        
        # Verify branding set file was removed
        file_path = os.path.join(self.temp_dir, "test.json")
        assert not os.path.exists(file_path)
        
        # Remove nonexistent branding set
        result = self.branding_manager.remove_branding_set("Nonexistent")
        
        # Verify result
        assert result == False
    
    def test_create_default_branding_sets(self):
        """Test creating default branding sets."""
        # Create default branding sets
        self.branding_manager.create_default_branding_sets()
        
        # Verify default branding sets were created
        assert "Default" in self.branding_manager.branding_sets
        assert "Corporate" in self.branding_manager.branding_sets
        
        # Verify default branding set
        default_branding = self.branding_manager.get_branding_set("Default")
        assert default_branding is not None
        assert len(default_branding) == 6
        
        # Verify corporate branding set
        corporate_branding = self.branding_manager.get_branding_set("Corporate")
        assert corporate_branding is not None
        assert len(corporate_branding) == 6
    
    def test_get_branding_element(self):
        """Test getting a branding element."""
        # Add branding set
        self.branding_manager.add_branding_set("Test", self.test_branding)
        
        # Get branding element
        element = self.branding_manager.get_branding_element("Test", "logo")
        
        # Verify branding element
        assert element is not None
        assert element.name == "logo"
        assert element.type == "image"
        assert element.value == "test-logo.png"
        
        # Get nonexistent branding element
        element = self.branding_manager.get_branding_element("Test", "nonexistent")
        
        # Verify result is None
        assert element is None
        
        # Get element from nonexistent branding set
        element = self.branding_manager.get_branding_element("Nonexistent", "logo")
        
        # Verify result is None
        assert element is None
    
    def test_update_branding_element(self):
        """Test updating a branding element."""
        # Add branding set
        self.branding_manager.add_branding_set("Test", self.test_branding)
        
        # Create updated branding element
        updated_element = BrandingElement(
            name="logo",
            type="image",
            value="updated-logo.png",
            description="Updated logo"
        )
        
        # Update branding element
        result = self.branding_manager.update_branding_element("Test", updated_element)
        
        # Verify result
        assert result == True
        
        # Verify branding element was updated
        element = self.branding_manager.get_branding_element("Test", "logo")
        assert element is not None
        assert element.value == "updated-logo.png"
        assert element.description == "Updated logo"
        
        # Update nonexistent branding element
        nonexistent_element = BrandingElement(
            name="nonexistent",
            type="text",
            value="nonexistent",
            description="Nonexistent"
        )
        
        result = self.branding_manager.update_branding_element("Test", nonexistent_element)
        
        # Verify result
        assert result == False
        
        # Update element in nonexistent branding set
        result = self.branding_manager.update_branding_element("Nonexistent", updated_element)
        
        # Verify result
        assert result == False