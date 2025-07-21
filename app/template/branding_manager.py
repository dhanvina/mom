"""
Branding manager module for AI-powered MoM generator.

This module provides functionality for managing branding elements.
"""

import os
import json
import logging
import base64
from typing import Dict, Any, Optional, List, Set, Union
from dataclasses import asdict
from .template_model import BrandingElement

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class BrandingManager:
    """
    Manages branding elements for templates.
    
    This class provides methods for loading, saving, and managing branding elements.
    
    Attributes:
        branding_dir (str): Directory for storing branding elements
        branding_sets (Dict[str, List[BrandingElement]]): Dictionary of branding sets
    """
    
    def __init__(self, branding_dir: Optional[str] = None):
        """
        Initialize the BrandingManager with optional branding directory.
        
        Args:
            branding_dir (str, optional): Directory for storing branding elements
        """
        self.branding_dir = branding_dir or os.path.join(os.path.dirname(__file__), 'branding')
        self.branding_sets: Dict[str, List[BrandingElement]] = {}
        self._load_branding_sets()
        logger.info("BrandingManager initialized")
    
    def _load_branding_sets(self) -> None:
        """Load branding sets from branding directory."""
        try:
            # Create branding directory if it doesn't exist
            os.makedirs(self.branding_dir, exist_ok=True)
            
            # Load branding sets from files
            for filename in os.listdir(self.branding_dir):
                if filename.endswith('.json'):
                    try:
                        path = os.path.join(self.branding_dir, filename)
                        with open(path, 'r', encoding='utf-8') as f:
                            data = json.load(f)
                            
                        # Extract branding set name and elements
                        set_name = data.get('name', os.path.splitext(filename)[0])
                        elements = [
                            BrandingElement(**element) for element in data.get('elements', [])
                        ]
                        
                        self.branding_sets[set_name] = elements
                        logger.info(f"Loaded branding set: {set_name}")
                    except Exception as e:
                        logger.warning(f"Error loading branding set {filename}: {e}")
        
        except Exception as e:
            logger.error(f"Error loading branding sets: {e}")
    
    def get_branding_set(self, name: str) -> Optional[List[BrandingElement]]:
        """
        Get a branding set by name.
        
        Args:
            name (str): Branding set name
            
        Returns:
            Optional[List[BrandingElement]]: List of branding elements, or None if not found
        """
        return self.branding_sets.get(name)
    
    def get_branding_sets(self) -> Dict[str, List[BrandingElement]]:
        """
        Get all branding sets.
        
        Returns:
            Dict[str, List[BrandingElement]]: Dictionary of branding sets
        """
        return self.branding_sets
    
    def add_branding_set(self, name: str, elements: List[BrandingElement]) -> None:
        """
        Add a branding set.
        
        Args:
            name (str): Branding set name
            elements (List[BrandingElement]): List of branding elements
        """
        self.branding_sets[name] = elements
        
        # Save branding set to file
        path = os.path.join(self.branding_dir, f"{name.lower().replace(' ', '_')}.json")
        with open(path, 'w', encoding='utf-8') as f:
            json.dump({
                'name': name,
                'elements': [asdict(element) for element in elements]
            }, f, indent=2)
        
        logger.info(f"Added branding set: {name}")
    
    def remove_branding_set(self, name: str) -> bool:
        """
        Remove a branding set.
        
        Args:
            name (str): Branding set name
            
        Returns:
            bool: True if branding set was removed, False otherwise
        """
        if name in self.branding_sets:
            # Remove branding set from memory
            self.branding_sets.pop(name)
            
            # Remove branding set file
            path = os.path.join(self.branding_dir, f"{name.lower().replace(' ', '_')}.json")
            if os.path.exists(path):
                os.remove(path)
            
            logger.info(f"Removed branding set: {name}")
            return True
        
        return False    

    def create_default_branding_sets(self) -> None:
        """Create default branding sets if they don't exist."""
        # Check if we already have branding sets
        if self.branding_sets:
            return
        
        # Create default branding set
        default_branding = [
            BrandingElement(
                name="logo",
                type="image",
                value="data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAGQAAABkCAYAAABw4pVUAAAABmJLR0QA/wD/AP+gvaeTAAAFJElEQVR4nO2dW2gdRRjHf01qNdW0SbxgxbvVqCCIWlREqFJ9qA/ixQdFfd6oD6JVUaE+KFZR8QIVQcSLFa0XRKu1XkCrVm2tWqPWJk2NJk1qbBqTPD7MHns8OWdnZnd2z5nz/WA/2N1v5pv/zOzszHwzUCgUCoVCoVAoFAqFQqFQKBQKhUKhUCgUCoVCIX+WAncCrwM/AweAv4FfgE+Bh4HFGdqXK5YDrwL/AK0Yx2/AXcCcDOzMBfOBZ4HDNBZC5/gOWJe6tTlgFfAz8UXROQZcnbLNmWYW8BRwlHhCHAe2AjcDFwJzgVOAi4EngJ0J6v0duCRF+zPLBuAg8UQ4CFyXoM6zgB0J6v4LWJmS/ZlkMfAbcYQ4ClydoO6ZwGMJ6v8dODMVL2SQJ4gjRgs4BKxOWP9twJEEbXg0FU9kjHOAPcQT43ng5IRtWAT8kKAdu4HTEvZFprgfvQgt4EfgvITXnwm8kqAte4AlCa+fKRYCu9EL0QIeT3j9WcBrCduxG1iQ8PqZ4m70QrSAX4GzE15/NvBWwnbsTdiOzDEf2I9ehBZwb8Lrz8FNyJO0Y1/CdmSOW9EL0cLNP+YnvP5c4N2E7TiUsB2ZYwawC70QLeCehNefC7yXsB1HErYjk6xBL0QLt/JKMkRNcgKftB25ZDN6IVq4FdLpCa8/D/ggYTuOJWxHJpkG7EAvRAt4MOH15wMfJWzH8YTtyCyXoBejBfyJm9QlYQHwScJ2/JewHZnlefRitHALwSQsBD5N2I7/ErYjs8zEbXrpxHgmYRsWAV8kbEcuT+CTcBl6MVrAX8CZCW1fDHyVsB25PIFPwpPoxWgBW4DTEti9BPg6YRtyeQKfhGnAj+jFaAGbgekxbV4KfJPw+rk8gU/KxcQT5ACwIYa9y4BvE147lyfwcdiEXowWbkV0XgQ7lwPfJbxuLk/g4zAV+Bq9IC3gS9ypeBSWA98nvGYuT+Djci5uJ08rSgt4IIJtK4AfEl4vlyfwSbgfvSAt3LnHmSFtWgn8mPBauTyBT8IU4Av0orRwR7ZhWIXbD0lyrVyewCdhJW4/QytKC7cPMiVg/auBnxJeJ5cn8Em5F70gLdxJe78V1BrgtwTXyOUJfFKmAJ+hF6WFm1/0OgJZC/ye4Pq5PIGPwxriCdLCHdmuT1DfOmBfgmvm8gQ+LvejF6WFm7j3OgJZD+xPcL1cnsDHZQrwKXpRWrgjW90RyAXAgQTXyuUJfBLWEk+QFu4IZF2Xei4EDia4Ti5P4JPyAHpRWrgj2zVd6rkIOJTgGrk8gU/KVGAH8QTZDFzSUcfFwOEE9efyBD4p64gnSAt3ZLu2rY5LgCMJ6s7lCXwaNqEXpYU7sl3TVsdlCevN5Ql8GqYB24knSAt3ZHs5cHnCOnN5Ap+WDcQTJI0jlyfwadmMXpQW+TuBT8104EvKCXxsLiSeILk8gU/LJvSi5PIEPi3TgS8oJ/CxuYh4guTyBD4tD6EXJZcn8GmZAXxOOYGPzTr0ouTyBD4tj6AXJZcn8GmZCXxGOYGPzXr0ouTyBD4tj6IXJZcn8GmZBXxKOYGPzQb0ouTyBD4tj6EXJZcn8GmZDXxCOYGPzUb0ouTyBD4tj6MXJZcn8GmZA3xMOYGPzSb0ouTyBD4tT6AXJZcn8GmZC3xEOYGPzW3oRcnlCXxankQvSi5P4NMyD9hGOYGPze3oRcnlCXxankIvSi5P4NMyH3gP+J9yAh+LO9CLkssT+LQ8jV6UXJ7Ap2UB8D7lBD4Wd6IXJZcn8Gl5Br0ouTyBLxQKhUKhUCgUCoVCoVAoFAqFQqFQKBQKhUKhkA/+BzXP96xP6M5KAAAAAElFTkSuQmCC",
                description="Default logo"
            ),
            BrandingElement(
                name="primary_color",
                type="color",
                value="#3498db",
                description="Primary color"
            ),
            BrandingElement(
                name="secondary_color",
                type="color",
                value="#2c3e50",
                description="Secondary color"
            ),
            BrandingElement(
                name="font",
                type="font",
                value="Arial, sans-serif",
                description="Default font"
            ),
            BrandingElement(
                name="header",
                type="text",
                value="Minutes of Meeting",
                description="Header text"
            ),
            BrandingElement(
                name="footer",
                type="text",
                value="Generated by AI-Powered MoM Generator",
                description="Footer text"
            )
        ]
        
        self.add_branding_set("Default", default_branding)
        
        # Create corporate branding set
        corporate_branding = [
            BrandingElement(
                name="logo",
                type="image",
                value="data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAGQAAABkCAYAAABw4pVUAAAABmJLR0QA/wD/AP+gvaeTAAAFJElEQVR4nO2dW2gdRRjHf01qNdW0SbxgxbvVqCCIWlREqFJ9qA/ixQdFfd6oD6JVUaE+KFZR8QIVQcSLFa0XRKu1XkCrVm2tWqPWJk2NJk2qbBqTPD7MHns8OWdnZnd2z5nz/WA/2N1v5pv/zOzszHwzUCgUCoVCoVAoFAqFQqFQKBQKhUKhUCgUCoVCIX+WAncCrwM/AweAv4FfgE+Bh4HFGdqXK5YDrwL/AK0Yx2/AXcCcDOzMBfOBZ4HDNBZC5/gOWJe6tTlgFfAz8UXROQZcnbLNmWYW8BRwlHhCHAe2AjcDFwJzgVOAi4EngJ0J6v0duCRF+zPLBuAg8UQ4CFyXoM6zgB0J6v4LWJmS/ZlkMfAbcYQ4ClydoO6ZwGMJ6v8dODMVL2SQJ4gjRgs4BKxOWP9twJEEbXg0FU9kjHOAPcQT43ng5IRtWAT8kKAdu4HTEvZFprgfvQgt4EfgvITXnwm8kqAte4AlCa+fKRYCu9EL0QIeT3j9WcBrCduxG1iQ8PqZ4m70QrSAX4GzE15/NvBWwnbsTdiOzDEf2I9ehBZwb8Lrz8FNyJO0Y1/CdmSOW9EL0cLNP+YnvP5c4N2E7TiUsB2ZYwawC70QLeCehNefC7yXsB1HErYjk6xBL0QLt/JKMkRNcgKftB25ZDN6IVq4FdLpCa8/D/ggYTuOJWxHJpkG7EAvRAt4MOH15wMfJWzH8YTtyCyXoBejBfyJm9QlYQHwScJ2/JewHZnlefRitHALwSQsBD5N2I7/ErYjs8zEbXrpxHgmYRsWAV8kbEcuT+CTcBl6MVrAX8CZCW1fDHyVsB25PIFPwpPoxWgBW4DTEti9BPg6YRtyeQKfhGnAj+jFaAGbgekxbV4KfJPw+rk8gU/KxcQT5ACwIYa9y4BvE147lyfwcdiEXowWbkV0XgQ7lwPfJbxuLk/g4zAV+Bq9IC3gS9ypeBSWA98nvGYuT+Djci5uJ08rSgt4IIJtK4AfEl4vlyfwSbgfvSAt3LnHmSFtWgn8mPBauTyBT8IU4Av0orRwR7ZhWIXbD0lyrVyewCdhJW4/QytKC7cPMiVg/auBnxJeJ5cn8Em5F70gLdxJe78V1BrgtwTXyOUJfFKmAJ+hF6WFm1/0OgJZC/ye4Pq5PIGPwxriCdLCHdmuT1DfOmBfgmvm8gQ+LvejF6WFm7j3OgJZD+xPcL1cnsDHZQrwKXpRWrgjW90RyAXAgQTXyuUJfBLWEk+QFu4IZF2Xei4EDia4Ti5P4JPyAHpRWrgj2zVd6rkIOJTgGrk8gU/KVGAH8QTZDFzSUcfFwOEE9efyBD4p64gnSAt3ZLu2rY5LgCMJ6s7lCXwaNqEXpYU7sl3TVsdlCevN5Ql8GqYB24knSAt3ZHs5cHnCOnN5Ap+WDcQTJI0jlyfwadmMXpQW+TuBT8104EvKCXxsLiSeILk8gU/LJvSi5PIEPi3TgS8oJ/CxuYh4guTyBD4tD6EXJZcn8GmZAXxOOYGPzTr0ouTyBD4tj6AXJZcn8GmZCXxGOYGPzXr0ouTyBD4tj6IXJZcn8GmZBXxKOYGPzQb0ouTyBD4tj6EXJZcn8GmZDXxCOYGPzUb0ouTyBD4tj6MXJZcn8GmZA3xMOYGPzSb0ouTyBD4tT6AXJZcn8GmZC3xEOYGPzW3oRcnlCXxankQvSi5P4NMyD9hGOYGPze3oRcnlCXxankIvSi5P4NMyH3gP+J9yAh+LO9CLkssT+LQ8jV6UXJ7Ap2UB8D7lBD4Wd6IXJZcn8Gl5Br0ouTyBLxQKhUKhUCgUCoVCoVAoFAqFQqFQKBQKhUKhkA/+BzXP96xP6M5KAAAAAElFTkSuQmCC",
                description="Corporate logo"
            ),
            BrandingElement(
                name="primary_color",
                type="color",
                value="#27ae60",
                description="Corporate primary color"
            ),
            BrandingElement(
                name="secondary_color",
                type="color",
                value="#2c3e50",
                description="Corporate secondary color"
            ),
            BrandingElement(
                name="font",
                type="font",
                value="Helvetica, Arial, sans-serif",
                description="Corporate font"
            ),
            BrandingElement(
                name="header",
                type="text",
                value="Corporate Meeting Minutes",
                description="Corporate header text"
            ),
            BrandingElement(
                name="footer",
                type="text",
                value="Confidential - Internal Use Only",
                description="Corporate footer text"
            )
        ]
        
        self.add_branding_set("Corporate", corporate_branding)
        
        logger.info("Created default branding sets")
    
    def get_branding_element(self, set_name: str, element_name: str) -> Optional[BrandingElement]:
        """
        Get a branding element from a branding set.
        
        Args:
            set_name (str): Branding set name
            element_name (str): Branding element name
            
        Returns:
            Optional[BrandingElement]: Branding element, or None if not found
        """
        branding_set = self.get_branding_set(set_name)
        if not branding_set:
            return None
            
        for element in branding_set:
            if element.name == element_name:
                return element
                
        return None
    
    def update_branding_element(self, set_name: str, element: BrandingElement) -> bool:
        """
        Update a branding element in a branding set.
        
        Args:
            set_name (str): Branding set name
            element (BrandingElement): Updated branding element
            
        Returns:
            bool: True if element was updated, False otherwise
        """
        branding_set = self.get_branding_set(set_name)
        if not branding_set:
            return False
            
        for i, e in enumerate(branding_set):
            if e.name == element.name:
                branding_set[i] = element
                
                # Save updated branding set
                self.add_branding_set(set_name, branding_set)
                return True
                
        return False