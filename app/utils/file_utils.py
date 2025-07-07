"""
File handling utilities for streamlit
This module provides utilities for handling file uploads and text input
in the streamlit interface, supporting .txt and .docx file formats
"""

import streamlit as st
import docx
from typing import Optional
import io
import logging

#configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class FileHandler:
    """
    Handles the file uploads and text processing for streamlit interface.

    This class provides methods for uploading transcript files(.txt, .docx)
    and handling manual text input from user. It includes proper error
    handling and validation for different file types.

    Attributes:
        supported_types (list): List of supported file extensions
        supported_mime_types (dict) : mapping of MIME types to file extensions
    """
    
    def __init__(self):
        """
        Initialize File handler with supported file types
        """
        self.supported_file_types = ['txt', 'docx']
        self.supported_mime_types = {
            "text/plain",
            "application/vnd.openxmlformats-officedocument.wordprocessingml.document"
        }
    
    def upload_file(self) -> Optional[str]:
        """
        Display a file uploader and return the content of uploaded file.

        Creates a streamlit file uploader widget that accepts .txt and .docx
        files. If a file is uploaded it reads and gives the content

        Returns:
            Optional[str]: The content of the uploaded file as a string, or None id the file is not uploaded.
        """
        try:
            uploaded_file = st.file_uploader(
                "Upload a transcript file",
                type = self.supported_file_types,
                help = "Upload a .txt or .docx file containing meeting transcript"
            )

            if uploaded_file is not None:
                logger.info(f"File uploaded: {uploaded_file.name} and {uploaded_file.type}")
                return self.read_file_content(uploaded_file)
            else:
                logger.debug("No file uploaded")
                return None
            
        except Exception as e:
            logger.error(f"Error in the file uploaded: {e}")
            st.error(f"Error handling file upload : {e}")
            return None

    def read_file_content(self, uploaded_file) -> str:
        """
        Read and parse the content from an uploaded file

        Supports both .txt files and .docx files
        Args:
            uploaded_file: StreamlitUploadedFile object containing the file data
            
        Returns:
            str: The file content as a string
            
        Raises:
            Exception: If file reading fails or unsupported file type
        """
        try:
            #Handle .txt files 
            if uploaded_file.type == "text/plain":
                logger.debug("Processing text file")
                return uploaded_file.getvalue().decode("utf-8")
            elif uploaded_file.type == "application/vnd.openxmlformats-officedocument.wordprocessingml.document":
                logger.debug("Processing word document")
                doc = docx.Document(io.BytesIO(uploaded_file.getvalue()))
                return "\n".join([paragraph.text for paragraph in doc.paragraphs])
            else:
                error_msg = f"Unsupported file type: {uploaded_file.type}"
                st.error("Unsupported file type")
                logger.warning(error_msg)
                return ""
        except UnicodeDecodeError as e:
            error_msg = f"Error decoding file content: {e}"
            logger.error(error_msg)
            st.error(error_msg)
            return ""
        
        except Exception as e:
            error_msg = f"Error reading file content: {e}"
            logger.error(error_msg)
            st.error(error_msg)
            return ""
        
    def text_input_area(self)-> str:
        """
        Display a text area for manual transcript input

        Creates a Streamlit text area widget where users can paste or type
        their meeting transcript directly into the interface.
        
        Returns:
            str: The text entered by the user
        """
        try:
            return st.text_area(
                "or paste your transcript here:",
                height=300,
                placeholder="Paste your meeting transcript here ....",
                help = "Enter or paste meeting transcript text directly"
            )
        except Exception as e:
            logger.error(f"Error in text input area: {e}")
            st.error("Error with text input: {e}")
            return ""
        
    def get_file_info(self, uploaded_file) -> dict:
        """
        Get information about an uploaded file

         Args:
            uploaded_file: StreamlitUploadedFile object
            
        Returns:
            dict: Dictionary containing file information
        """
        if uploaded_file is None:
            return {}
        return {"name": uploaded_file.name,
                "type": uploaded_file.type,
                "size": uploaded_file.size,
                "size_mb": round(uploaded_file.size /(1024*1024),2)
                }







