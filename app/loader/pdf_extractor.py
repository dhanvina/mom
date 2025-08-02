"""
PDF extractor module for AI-powered MoM generator.

This module provides functionality for extracting text from PDF files.
"""

import io
import logging
from typing import Any, Dict, Optional, Union
import PyPDF2
from .base_extractor import BaseExtractor

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class PDFExtractor(BaseExtractor):
    """
    Extracts text from PDF files.
    
    This class provides methods for loading and extracting text from PDF files.
    
    Attributes:
        config (Dict): Configuration options for the extractor
    """
    
    def __init__(self, config: Optional[Dict[str, Any]] = None):
        """
        Initialize the PDFExtractor with optional configuration.
        
        Args:
            config (Dict, optional): Configuration options for the extractor
        """
        super().__init__(config)
        logger.info("PDFExtractor initialized")
    
    def extract(self, source: Union[str, bytes, io.BytesIO]) -> str:
        """
        Extract text from a PDF file.
        
        Args:
            source (Union[str, bytes, io.BytesIO]): Path to the PDF file,
                bytes content, or BytesIO object
            
        Returns:
            str: The extracted text
            
        Raises:
            IOError: If the PDF file cannot be read or processed
            ValueError: If the source type is not supported
        """
        try:
            logger.info("Extracting text from PDF file")
            
            # Handle different source types
            if isinstance(source, str):
                # Source is a file path
                with open(source, 'rb') as file:
                    reader = PyPDF2.PdfReader(file)
                    return self._extract_from_reader(reader)
            elif isinstance(source, bytes):
                # Source is bytes
                reader = PyPDF2.PdfReader(io.BytesIO(source))
                return self._extract_from_reader(reader)
            elif isinstance(source, io.BytesIO):
                # Source is BytesIO
                reader = PyPDF2.PdfReader(source)
                return self._extract_from_reader(reader)
            else:
                raise ValueError(f"Unsupported source type: {type(source)}")
        
        except Exception as e:
            error_msg = f"Error extracting text from PDF: {e}"
            logger.error(error_msg)
            raise IOError(error_msg)
    
    def _extract_from_reader(self, reader: PyPDF2.PdfReader) -> str:
        """
        Extract text from a PDF reader.
        
        Args:
            reader (PyPDF2.PdfReader): PDF reader object
            
        Returns:
            str: The extracted text
        """
        logger.info(f"Extracting text from PDF with {len(reader.pages)} pages")
        
        # Extract text from each page
        text_parts = []
        for i, page in enumerate(reader.pages):
            try:
                page_text = page.extract_text()
                if page_text:
                    text_parts.append(page_text)
                else:
                    logger.warning(f"No text extracted from page {i+1}")
            except Exception as e:
                logger.warning(f"Error extracting text from page {i+1}: {e}")
        
        # Combine all text parts
        full_text = "\n\n".join(text_parts)
        
        # Preprocess the text
        return self.preprocess(full_text)
    
    def extract_page(self, source: Union[str, bytes, io.BytesIO], page_num: int) -> str:
        """
        Extract text from a specific page of a PDF file.
        
        Args:
            source (Union[str, bytes, io.BytesIO]): Path to the PDF file,
                bytes content, or BytesIO object
            page_num (int): Page number (0-based index)
            
        Returns:
            str: The extracted text from the specified page
            
        Raises:
            IOError: If the PDF file cannot be read or processed
            ValueError: If the source type is not supported or page number is invalid
        """
        try:
            logger.info(f"Extracting text from PDF page {page_num+1}")
            
            # Handle different source types
            if isinstance(source, str):
                # Source is a file path
                with open(source, 'rb') as file:
                    reader = PyPDF2.PdfReader(file)
                    return self._extract_from_page(reader, page_num)
            elif isinstance(source, bytes):
                # Source is bytes
                reader = PyPDF2.PdfReader(io.BytesIO(source))
                return self._extract_from_page(reader, page_num)
            elif isinstance(source, io.BytesIO):
                # Source is BytesIO
                reader = PyPDF2.PdfReader(source)
                return self._extract_from_page(reader, page_num)
            else:
                raise ValueError(f"Unsupported source type: {type(source)}")
        
        except Exception as e:
            error_msg = f"Error extracting text from PDF page {page_num+1}: {e}"
            logger.error(error_msg)
            raise IOError(error_msg)
    
    def _extract_from_page(self, reader: PyPDF2.PdfReader, page_num: int) -> str:
        """
        Extract text from a specific page of a PDF reader.
        
        Args:
            reader (PyPDF2.PdfReader): PDF reader object
            page_num (int): Page number (0-based index)
            
        Returns:
            str: The extracted text from the specified page
            
        Raises:
            ValueError: If the page number is invalid
        """
        if page_num < 0 or page_num >= len(reader.pages):
            raise ValueError(f"Invalid page number: {page_num+1}. PDF has {len(reader.pages)} pages.")
        
        try:
            page = reader.pages[page_num]
            page_text = page.extract_text()
            
            if not page_text:
                logger.warning(f"No text extracted from page {page_num+1}")
                return ""
            
            # Preprocess the text
            return self.preprocess(page_text)
        
        except Exception as e:
            logger.warning(f"Error extracting text from page {page_num+1}: {e}")
            return ""
    
    def extract_page_range(self, source: Union[str, bytes, io.BytesIO], start_page: int, end_page: int) -> str:
        """
        Extract text from a range of pages in a PDF file.
        
        Args:
            source (Union[str, bytes, io.BytesIO]): Path to the PDF file,
                bytes content, or BytesIO object
            start_page (int): Start page number (0-based index, inclusive)
            end_page (int): End page number (0-based index, inclusive)
            
        Returns:
            str: The extracted text from the specified page range
            
        Raises:
            IOError: If the PDF file cannot be read or processed
            ValueError: If the source type is not supported or page numbers are invalid
        """
        try:
            logger.info(f"Extracting text from PDF pages {start_page+1} to {end_page+1}")
            
            if start_page < 0:
                raise ValueError("Start page cannot be negative")
            if end_page < start_page:
                raise ValueError("End page must be greater than or equal to start page")
            
            # Handle different source types
            if isinstance(source, str):
                # Source is a file path
                with open(source, 'rb') as file:
                    reader = PyPDF2.PdfReader(file)
                    return self._extract_from_page_range(reader, start_page, end_page)
            elif isinstance(source, bytes):
                # Source is bytes
                reader = PyPDF2.PdfReader(io.BytesIO(source))
                return self._extract_from_page_range(reader, start_page, end_page)
            elif isinstance(source, io.BytesIO):
                # Source is BytesIO
                reader = PyPDF2.PdfReader(source)
                return self._extract_from_page_range(reader, start_page, end_page)
            else:
                raise ValueError(f"Unsupported source type: {type(source)}")
        
        except Exception as e:
            error_msg = f"Error extracting text from PDF pages {start_page+1} to {end_page+1}: {e}"
            logger.error(error_msg)
            raise IOError(error_msg)
    
    def _extract_from_page_range(self, reader: PyPDF2.PdfReader, start_page: int, end_page: int) -> str:
        """
        Extract text from a range of pages in a PDF reader.
        
        Args:
            reader (PyPDF2.PdfReader): PDF reader object
            start_page (int): Start page number (0-based index, inclusive)
            end_page (int): End page number (0-based index, inclusive)
            
        Returns:
            str: The extracted text from the specified page range
            
        Raises:
            ValueError: If the page numbers are invalid
        """
        if start_page < 0:
            raise ValueError("Start page cannot be negative")
        
        # Adjust end_page if it's beyond the document
        num_pages = len(reader.pages)
        if end_page >= num_pages:
            logger.warning(f"End page {end_page+1} exceeds document length ({num_pages} pages)")
            end_page = num_pages - 1
        
        if end_page < start_page:
            raise ValueError("End page must be greater than or equal to start page")
        
        # Extract text from each page in the range
        text_parts = []
        for i in range(start_page, end_page + 1):
            try:
                page = reader.pages[i]
                page_text = page.extract_text()
                if page_text:
                    text_parts.append(page_text)
                else:
                    logger.warning(f"No text extracted from page {i+1}")
            except Exception as e:
                logger.warning(f"Error extracting text from page {i+1}: {e}")
        
        # Combine all text parts
        full_text = "\n\n".join(text_parts)
        
        # Preprocess the text
        return self.preprocess(full_text)