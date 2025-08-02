"""
Data Privacy Manager for MoM Generator.

This module provides comprehensive data privacy features including
data retention policies, secure deletion, and privacy compliance.
"""

import os
import json
import logging
import hashlib
import shutil
from typing import Dict, Any, Optional, List, Tuple
from datetime import datetime, timedelta
from pathlib import Path
import tempfile

logger = logging.getLogger(__name__)


class DataRetentionPolicy:
    """Data retention policy configuration."""
    
    def __init__(self, retention_days: int = 30, auto_delete: bool = False, 
                 categories: Optional[Dict[str, int]] = None):
        """
        Initialize data retention policy.
        
        Args:
            retention_days (int): Default retention period in days
            auto_delete (bool): Whether to automatically delete old data
            categories (Dict[str, int], optional): Category-specific retention periods
        """
        self.retention_days = retention_days
        self.auto_delete = auto_delete
        self.categories = categories or {
            'transcripts': retention_days,
            'mom_outputs': retention_days * 2,  # Keep outputs longer
            'temp_files': 1,  # Delete temp files after 1 day
            'logs': 7,  # Keep logs for 7 days
            'cache': 30  # Keep cache for 30 days
        }
    
    def get_retention_period(self, category: str) -> int:
        """
        Get retention period for a specific data category.
        
        Args:
            category (str): Data category
            
        Returns:
            int: Retention period in days
        """
        return self.categories.get(category, self.retention_days)
    
    def should_delete(self, file_path: str, category: str) -> bool:
        """
        Check if a file should be deleted based on retention policy.
        
        Args:
            file_path (str): Path to the file
            category (str): Data category
            
        Returns:
            bool: True if file should be deleted
        """
        if not os.path.exists(file_path):
            return False
        
        retention_days = self.get_retention_period(category)
        file_age = datetime.now() - datetime.fromtimestamp(os.path.getmtime(file_path))
        
        return file_age.days > retention_days


class SecureFileManager:
    """Manager for secure file operations."""
    
    @staticmethod
    def secure_delete(file_path: str, passes: int = 3) -> bool:
        """
        Securely delete a file by overwriting it multiple times.
        
        Args:
            file_path (str): Path to file to delete
            passes (int): Number of overwrite passes
            
        Returns:
            bool: True if successful
        """
        try:
            if not os.path.exists(file_path):
                return True
            
            file_size = os.path.getsize(file_path)
            
            # Overwrite file multiple times
            with open(file_path, 'r+b') as f:
                for _ in range(passes):
                    f.seek(0)
                    f.write(os.urandom(file_size))
                    f.flush()
                    os.fsync(f.fileno())
            
            # Finally delete the file
            os.remove(file_path)
            logger.info(f"Securely deleted file: {file_path}")
            return True
        
        except Exception as e:
            logger.error(f"Error securely deleting {file_path}: {e}")
            return False
    
    @staticmethod
    def secure_delete_directory(dir_path: str) -> bool:
        """
        Securely delete a directory and all its contents.
        
        Args:
            dir_path (str): Path to directory to delete
            
        Returns:
            bool: True if successful
        """
        try:
            if not os.path.exists(dir_path):
                return True
            
            # Securely delete all files in directory
            for root, dirs, files in os.walk(dir_path, topdown=False):
                for file in files:
                    file_path = os.path.join(root, file)
                    SecureFileManager.secure_delete(file_path)
                
                # Remove empty directories
                for dir_name in dirs:
                    dir_full_path = os.path.join(root, dir_name)
                    try:
                        os.rmdir(dir_full_path)
                    except OSError:
                        pass  # Directory not empty, will be handled in next iteration
            
            # Remove the main directory
            os.rmdir(dir_path)
            logger.info(f"Securely deleted directory: {dir_path}")
            return True
        
        except Exception as e:
            logger.error(f"Error securely deleting directory {dir_path}: {e}")
            return False
    
    @staticmethod
    def create_secure_temp_file(suffix: str = '.tmp', prefix: str = 'mom_') -> Tuple[str, Any]:
        """
        Create a secure temporary file.
        
        Args:
            suffix (str): File suffix
            prefix (str): File prefix
            
        Returns:
            Tuple[str, Any]: (file_path, file_handle)
        """
        try:
            fd, temp_path = tempfile.mkstemp(suffix=suffix, prefix=prefix)
            
            # Set restrictive permissions (owner read/write only)
            os.chmod(temp_path, 0o600)
            
            return temp_path, fd
        
        except Exception as e:
            logger.error(f"Error creating secure temp file: {e}")
            raise


class DataPrivacyManager:
    """
    Comprehensive data privacy manager.
    
    This class handles data retention policies, secure deletion,
    privacy compliance, and data anonymization.
    """
    
    def __init__(self, config: Dict[str, Any]):
        """
        Initialize the DataPrivacyManager.
        
        Args:
            config (Dict[str, Any]): Configuration settings
        """
        self.config = config
        self.data_dir = os.path.join(os.path.expanduser("~"), ".mom_data")
        self.temp_dir = os.path.join(self.data_dir, "temp")
        self.logs_dir = os.path.join(self.data_dir, "logs")
        self.transcripts_dir = os.path.join(self.data_dir, "transcripts")
        self.outputs_dir = os.path.join(self.data_dir, "outputs")
        
        # Ensure directories exist
        for directory in [self.data_dir, self.temp_dir, self.logs_dir, 
                         self.transcripts_dir, self.outputs_dir]:
            os.makedirs(directory, exist_ok=True)
            # Set restrictive permissions
            os.chmod(directory, 0o700)
        
        # Initialize retention policy
        self.retention_policy = DataRetentionPolicy(
            retention_days=config.get('data_retention_days', 30),
            auto_delete=config.get('auto_delete_transcripts', False),
            categories=config.get('retention_categories', {})
        )
        
        # Initialize secure file manager
        self.secure_file_manager = SecureFileManager()
        
        # Privacy settings
        self.privacy_mode = config.get('privacy_mode', False)
        self.anonymize_data = config.get('anonymize_data', False)
        self.encrypt_storage = config.get('encrypt_storage', False)
        
        logger.info("DataPrivacyManager initialized")
    
    def get_privacy_status(self) -> Dict[str, Any]:
        """
        Get comprehensive privacy status.
        
        Returns:
            Dict[str, Any]: Privacy status information
        """
        return {
            'privacy_mode': self.privacy_mode,
            'anonymize_data': self.anonymize_data,
            'encrypt_storage': self.encrypt_storage,
            'auto_delete_enabled': self.retention_policy.auto_delete,
            'retention_days': self.retention_policy.retention_days,
            'data_directories': {
                'data_dir': self.data_dir,
                'temp_dir': self.temp_dir,
                'logs_dir': self.logs_dir,
                'transcripts_dir': self.transcripts_dir,
                'outputs_dir': self.outputs_dir
            },
            'retention_categories': self.retention_policy.categories,
            'storage_usage': self._get_storage_usage()
        }
    
    def _get_storage_usage(self) -> Dict[str, Any]:
        """
        Get storage usage information.
        
        Returns:
            Dict[str, Any]: Storage usage statistics
        """
        usage = {}
        
        for category, directory in [
            ('transcripts', self.transcripts_dir),
            ('outputs', self.outputs_dir),
            ('temp', self.temp_dir),
            ('logs', self.logs_dir)
        ]:
            try:
                total_size = 0
                file_count = 0
                
                if os.path.exists(directory):
                    for root, dirs, files in os.walk(directory):
                        for file in files:
                            file_path = os.path.join(root, file)
                            if os.path.exists(file_path):
                                total_size += os.path.getsize(file_path)
                                file_count += 1
                
                usage[category] = {
                    'size_mb': round(total_size / (1024 * 1024), 2),
                    'file_count': file_count,
                    'directory': directory
                }
            
            except Exception as e:
                logger.error(f"Error calculating usage for {category}: {e}")
                usage[category] = {'error': str(e)}
        
        return usage
    
    def store_transcript(self, transcript: str, metadata: Optional[Dict[str, Any]] = None) -> str:
        """
        Store a transcript with privacy considerations.
        
        Args:
            transcript (str): Transcript content
            metadata (Dict[str, Any], optional): Transcript metadata
            
        Returns:
            str: Path to stored transcript
        """
        try:
            # Generate unique filename
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            transcript_hash = hashlib.md5(transcript.encode()).hexdigest()[:8]
            filename = f"transcript_{timestamp}_{transcript_hash}.txt"
            file_path = os.path.join(self.transcripts_dir, filename)
            
            # Anonymize transcript if enabled
            if self.anonymize_data:
                transcript = self._anonymize_transcript(transcript)
            
            # Store transcript
            with open(file_path, 'w', encoding='utf-8') as f:
                f.write(transcript)
            
            # Set restrictive permissions
            os.chmod(file_path, 0o600)
            
            # Store metadata if provided
            if metadata:
                metadata_path = file_path.replace('.txt', '_metadata.json')
                with open(metadata_path, 'w', encoding='utf-8') as f:
                    json.dump(metadata, f, indent=2)
                os.chmod(metadata_path, 0o600)
            
            logger.info(f"Transcript stored: {filename}")
            return file_path
        
        except Exception as e:
            logger.error(f"Error storing transcript: {e}")
            raise
    
    def store_mom_output(self, mom_data: Dict[str, Any], output_format: str = 'json') -> str:
        """
        Store MoM output with privacy considerations.
        
        Args:
            mom_data (Dict[str, Any]): MoM data
            output_format (str): Output format
            
        Returns:
            str: Path to stored output
        """
        try:
            # Generate unique filename
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            meeting_title = mom_data.get('meeting_title', 'meeting')
            safe_title = "".join(c for c in meeting_title if c.isalnum() or c in (' ', '-', '_')).rstrip()[:20]
            filename = f"mom_{timestamp}_{safe_title}.{output_format}"
            file_path = os.path.join(self.outputs_dir, filename)
            
            # Anonymize MoM data if enabled
            if self.anonymize_data:
                mom_data = self._anonymize_mom_data(mom_data)
            
            # Store output
            if output_format == 'json':
                with open(file_path, 'w', encoding='utf-8') as f:
                    json.dump(mom_data, f, indent=2, ensure_ascii=False)
            else:
                # Assume text format
                with open(file_path, 'w', encoding='utf-8') as f:
                    f.write(str(mom_data))
            
            # Set restrictive permissions
            os.chmod(file_path, 0o600)
            
            logger.info(f"MoM output stored: {filename}")
            return file_path
        
        except Exception as e:
            logger.error(f"Error storing MoM output: {e}")
            raise
    
    def _anonymize_transcript(self, transcript: str) -> str:
        """
        Anonymize transcript by removing or replacing sensitive information.
        
        Args:
            transcript (str): Original transcript
            
        Returns:
            str: Anonymized transcript
        """
        import re
        
        anonymized = transcript
        
        # Replace email addresses
        anonymized = re.sub(r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b', 
                           '[EMAIL]', anonymized)
        
        # Replace phone numbers (simple pattern)
        anonymized = re.sub(r'\b\d{3}[-.]?\d{3}[-.]?\d{4}\b', '[PHONE]', anonymized)
        
        # Replace potential names (capitalized words followed by colon)
        # This is a simple heuristic and may need refinement
        anonymized = re.sub(r'\b[A-Z][a-z]+\s[A-Z][a-z]+:', 'Speaker:', anonymized)
        
        # Replace potential addresses (numbers followed by street-like words)
        anonymized = re.sub(r'\b\d+\s+[A-Z][a-z]+\s+(Street|St|Avenue|Ave|Road|Rd|Drive|Dr|Lane|Ln)\b', 
                           '[ADDRESS]', anonymized, flags=re.IGNORECASE)
        
        return anonymized
    
    def _anonymize_mom_data(self, mom_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Anonymize MoM data by removing or replacing sensitive information.
        
        Args:
            mom_data (Dict[str, Any]): Original MoM data
            
        Returns:
            Dict[str, Any]: Anonymized MoM data
        """
        anonymized = mom_data.copy()
        
        # Anonymize attendees
        if 'attendees' in anonymized:
            anonymized['attendees'] = [f"Attendee_{i+1}" for i in range(len(anonymized['attendees']))]
        
        # Anonymize speakers in discussion points
        if 'discussion_points' in anonymized:
            for i, point in enumerate(anonymized['discussion_points']):
                if isinstance(point, str):
                    anonymized['discussion_points'][i] = self._anonymize_transcript(point)
        
        # Anonymize action item assignees
        if 'action_items' in anonymized:
            for item in anonymized['action_items']:
                if isinstance(item, dict) and 'assignee' in item:
                    item['assignee'] = '[ASSIGNEE]'
        
        return anonymized
    
    def cleanup_old_data(self) -> Dict[str, Any]:
        """
        Clean up old data based on retention policy.
        
        Returns:
            Dict[str, Any]: Cleanup results
        """
        if not self.retention_policy.auto_delete:
            return {
                'cleaned': False,
                'reason': 'Auto-delete disabled',
                'deleted_files': []
            }
        
        deleted_files = []
        errors = []
        
        # Define directories and their categories
        directories = [
            (self.transcripts_dir, 'transcripts'),
            (self.outputs_dir, 'mom_outputs'),
            (self.temp_dir, 'temp_files'),
            (self.logs_dir, 'logs')
        ]
        
        for directory, category in directories:
            try:
                if not os.path.exists(directory):
                    continue
                
                for root, dirs, files in os.walk(directory):
                    for file in files:
                        file_path = os.path.join(root, file)
                        
                        if self.retention_policy.should_delete(file_path, category):
                            if self.secure_file_manager.secure_delete(file_path):
                                deleted_files.append(file_path)
                                logger.info(f"Deleted old file: {file_path}")
                            else:
                                errors.append(f"Failed to delete: {file_path}")
            
            except Exception as e:
                error_msg = f"Error cleaning up {directory}: {e}"
                errors.append(error_msg)
                logger.error(error_msg)
        
        return {
            'cleaned': True,
            'deleted_files': deleted_files,
            'deleted_count': len(deleted_files),
            'errors': errors
        }
    
    def delete_all_data(self) -> Dict[str, Any]:
        """
        Delete all stored data (for privacy compliance).
        
        Returns:
            Dict[str, Any]: Deletion results
        """
        try:
            deleted_directories = []
            errors = []
            
            # Directories to delete
            directories = [
                self.transcripts_dir,
                self.outputs_dir,
                self.temp_dir,
                self.logs_dir
            ]
            
            for directory in directories:
                if os.path.exists(directory):
                    if self.secure_file_manager.secure_delete_directory(directory):
                        deleted_directories.append(directory)
                        # Recreate empty directory
                        os.makedirs(directory, exist_ok=True)
                        os.chmod(directory, 0o700)
                    else:
                        errors.append(f"Failed to delete directory: {directory}")
            
            logger.info("All user data deleted")
            
            return {
                'success': True,
                'deleted_directories': deleted_directories,
                'errors': errors,
                'message': 'All user data has been securely deleted'
            }
        
        except Exception as e:
            error_msg = f"Error deleting all data: {e}"
            logger.error(error_msg)
            return {
                'success': False,
                'error': error_msg
            }
    
    def export_data(self, export_path: str) -> Dict[str, Any]:
        """
        Export all user data for portability (GDPR compliance).
        
        Args:
            export_path (str): Path to export data to
            
        Returns:
            Dict[str, Any]: Export results
        """
        try:
            # Create export directory
            os.makedirs(export_path, exist_ok=True)
            
            exported_files = []
            errors = []
            
            # Directories to export
            directories = [
                ('transcripts', self.transcripts_dir),
                ('outputs', self.outputs_dir)
            ]
            
            for category, source_dir in directories:
                if not os.path.exists(source_dir):
                    continue
                
                export_category_dir = os.path.join(export_path, category)
                os.makedirs(export_category_dir, exist_ok=True)
                
                try:
                    # Copy files
                    for root, dirs, files in os.walk(source_dir):
                        for file in files:
                            source_file = os.path.join(root, file)
                            relative_path = os.path.relpath(source_file, source_dir)
                            dest_file = os.path.join(export_category_dir, relative_path)
                            
                            # Create destination directory if needed
                            os.makedirs(os.path.dirname(dest_file), exist_ok=True)
                            
                            # Copy file
                            shutil.copy2(source_file, dest_file)
                            exported_files.append(dest_file)
                
                except Exception as e:
                    error_msg = f"Error exporting {category}: {e}"
                    errors.append(error_msg)
                    logger.error(error_msg)
            
            # Create export manifest
            manifest = {
                'export_date': datetime.now().isoformat(),
                'exported_files': exported_files,
                'privacy_status': self.get_privacy_status(),
                'export_version': '1.0'
            }
            
            manifest_path = os.path.join(export_path, 'export_manifest.json')
            with open(manifest_path, 'w', encoding='utf-8') as f:
                json.dump(manifest, f, indent=2)
            
            logger.info(f"Data exported to: {export_path}")
            
            return {
                'success': True,
                'export_path': export_path,
                'exported_files': exported_files,
                'manifest_path': manifest_path,
                'errors': errors
            }
        
        except Exception as e:
            error_msg = f"Error exporting data: {e}"
            logger.error(error_msg)
            return {
                'success': False,
                'error': error_msg
            }
    
    def create_privacy_report(self) -> Dict[str, Any]:
        """
        Create a comprehensive privacy report.
        
        Returns:
            Dict[str, Any]: Privacy report
        """
        try:
            privacy_status = self.get_privacy_status()
            
            # Calculate data age statistics
            data_age_stats = self._calculate_data_age_stats()
            
            # Check compliance status
            compliance_status = self._check_compliance_status()
            
            report = {
                'report_date': datetime.now().isoformat(),
                'privacy_settings': {
                    'privacy_mode': self.privacy_mode,
                    'anonymize_data': self.anonymize_data,
                    'encrypt_storage': self.encrypt_storage,
                    'auto_delete_enabled': self.retention_policy.auto_delete
                },
                'data_retention': {
                    'default_retention_days': self.retention_policy.retention_days,
                    'category_retention': self.retention_policy.categories
                },
                'storage_usage': privacy_status['storage_usage'],
                'data_age_statistics': data_age_stats,
                'compliance_status': compliance_status,
                'recommendations': self._generate_privacy_recommendations()
            }
            
            return report
        
        except Exception as e:
            logger.error(f"Error creating privacy report: {e}")
            return {'error': str(e)}
    
    def _calculate_data_age_stats(self) -> Dict[str, Any]:
        """Calculate statistics about data age."""
        stats = {}
        
        directories = [
            ('transcripts', self.transcripts_dir),
            ('outputs', self.outputs_dir)
        ]
        
        for category, directory in directories:
            if not os.path.exists(directory):
                stats[category] = {'file_count': 0}
                continue
            
            file_ages = []
            
            for root, dirs, files in os.walk(directory):
                for file in files:
                    file_path = os.path.join(root, file)
                    if os.path.exists(file_path):
                        file_age = datetime.now() - datetime.fromtimestamp(os.path.getmtime(file_path))
                        file_ages.append(file_age.days)
            
            if file_ages:
                stats[category] = {
                    'file_count': len(file_ages),
                    'oldest_file_days': max(file_ages),
                    'newest_file_days': min(file_ages),
                    'average_age_days': sum(file_ages) / len(file_ages)
                }
            else:
                stats[category] = {'file_count': 0}
        
        return stats
    
    def _check_compliance_status(self) -> Dict[str, Any]:
        """Check compliance with privacy regulations."""
        issues = []
        recommendations = []
        
        # Check retention policy compliance
        if not self.retention_policy.auto_delete:
            issues.append("Automatic data deletion is disabled")
            recommendations.append("Enable automatic data deletion for compliance")
        
        # Check for old data
        data_age_stats = self._calculate_data_age_stats()
        for category, stats in data_age_stats.items():
            if stats.get('oldest_file_days', 0) > self.retention_policy.get_retention_period(category):
                issues.append(f"Old {category} data exceeds retention policy")
                recommendations.append(f"Clean up old {category} data")
        
        # Check privacy settings
        if not self.privacy_mode and not self.anonymize_data:
            recommendations.append("Consider enabling privacy mode or data anonymization")
        
        return {
            'compliant': len(issues) == 0,
            'issues': issues,
            'recommendations': recommendations
        }
    
    def _generate_privacy_recommendations(self) -> List[str]:
        """Generate privacy recommendations."""
        recommendations = []
        
        if not self.privacy_mode:
            recommendations.append("Enable privacy mode for enhanced data protection")
        
        if not self.anonymize_data:
            recommendations.append("Enable data anonymization to protect personal information")
        
        if not self.retention_policy.auto_delete:
            recommendations.append("Enable automatic data deletion to comply with retention policies")
        
        if not self.encrypt_storage:
            recommendations.append("Consider enabling storage encryption for sensitive data")
        
        # Check storage usage
        storage_usage = self._get_storage_usage()
        total_size = sum(cat.get('size_mb', 0) for cat in storage_usage.values() if isinstance(cat, dict))
        
        if total_size > 1000:  # More than 1GB
            recommendations.append("Consider cleaning up old data to reduce storage usage")
        
        return recommendations