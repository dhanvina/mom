"""
Version history and change tracking for collaborative editing.
Tracks document versions, changes, and provides diff visualization.
"""

import json
import logging
import time
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any, Tuple
from dataclasses import dataclass, asdict
from enum import Enum
import difflib
import hashlib

logger = logging.getLogger(__name__)


class ChangeType(Enum):
    """Types of changes that can be tracked"""
    CONTENT_CHANGE = "content_change"
    METADATA_CHANGE = "metadata_change"
    USER_JOIN = "user_join"
    USER_LEAVE = "user_leave"
    DOCUMENT_LOCK = "document_lock"
    DOCUMENT_UNLOCK = "document_unlock"
    DOCUMENT_FINALIZE = "document_finalize"


@dataclass
class DocumentVersion:
    """Represents a version of a document"""
    version_id: str
    document_id: str
    version_number: int
    content: str
    content_hash: str
    created_at: datetime
    created_by: str
    created_by_username: str
    change_summary: str
    metadata: Dict[str, Any]
    parent_version: Optional[str] = None
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert version to dictionary"""
        return {
            'version_id': self.version_id,
            'document_id': self.document_id,
            'version_number': self.version_number,
            'content': self.content,
            'content_hash': self.content_hash,
            'created_at': self.created_at.isoformat(),
            'created_by': self.created_by,
            'created_by_username': self.created_by_username,
            'change_summary': self.change_summary,
            'metadata': self.metadata,
            'parent_version': self.parent_version
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'DocumentVersion':
        """Create version from dictionary"""
        return cls(
            version_id=data['version_id'],
            document_id=data['document_id'],
            version_number=data['version_number'],
            content=data['content'],
            content_hash=data['content_hash'],
            created_at=datetime.fromisoformat(data['created_at']),
            created_by=data['created_by'],
            created_by_username=data['created_by_username'],
            change_summary=data['change_summary'],
            metadata=data.get('metadata', {}),
            parent_version=data.get('parent_version')
        )


@dataclass
class ChangeRecord:
    """Represents a single change record"""
    change_id: str
    document_id: str
    version_id: str
    change_type: ChangeType
    user_id: str
    username: str
    timestamp: datetime
    description: str
    details: Dict[str, Any]
    before_state: Optional[str] = None
    after_state: Optional[str] = None
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert change record to dictionary"""
        return {
            'change_id': self.change_id,
            'document_id': self.document_id,
            'version_id': self.version_id,
            'change_type': self.change_type.value,
            'user_id': self.user_id,
            'username': self.username,
            'timestamp': self.timestamp.isoformat(),
            'description': self.description,
            'details': self.details,
            'before_state': self.before_state,
            'after_state': self.after_state
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'ChangeRecord':
        """Create change record from dictionary"""
        return cls(
            change_id=data['change_id'],
            document_id=data['document_id'],
            version_id=data['version_id'],
            change_type=ChangeType(data['change_type']),
            user_id=data['user_id'],
            username=data['username'],
            timestamp=datetime.fromisoformat(data['timestamp']),
            description=data['description'],
            details=data.get('details', {}),
            before_state=data.get('before_state'),
            after_state=data.get('after_state')
        )


@dataclass
class UserActivity:
    """Represents user activity in a document"""
    activity_id: str
    user_id: str
    username: str
    document_id: str
    activity_type: str
    timestamp: datetime
    details: Dict[str, Any]
    session_id: Optional[str] = None
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert user activity to dictionary"""
        return {
            'activity_id': self.activity_id,
            'user_id': self.user_id,
            'username': self.username,
            'document_id': self.document_id,
            'activity_type': self.activity_type,
            'timestamp': self.timestamp.isoformat(),
            'details': self.details,
            'session_id': self.session_id
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'UserActivity':
        """Create user activity from dictionary"""
        return cls(
            activity_id=data['activity_id'],
            user_id=data['user_id'],
            username=data['username'],
            document_id=data['document_id'],
            activity_type=data['activity_type'],
            timestamp=datetime.fromisoformat(data['timestamp']),
            details=data.get('details', {}),
            session_id=data.get('session_id')
        )


class DiffGenerator:
    """Generates diffs between document versions"""
    
    @staticmethod
    def generate_text_diff(old_content: str, new_content: str) -> Dict[str, Any]:
        """Generate a text diff between two content versions"""
        old_lines = old_content.splitlines(keepends=True)
        new_lines = new_content.splitlines(keepends=True)
        
        # Generate unified diff
        unified_diff = list(difflib.unified_diff(
            old_lines, new_lines,
            fromfile='old_version',
            tofile='new_version',
            lineterm=''
        ))
        
        # Generate HTML diff
        html_diff = difflib.HtmlDiff()
        html_table = html_diff.make_table(
            old_lines, new_lines,
            fromdesc='Previous Version',
            todesc='Current Version',
            context=True,
            numlines=3
        )
        
        # Calculate statistics
        differ = difflib.SequenceMatcher(None, old_content, new_content)
        similarity_ratio = differ.ratio()
        
        # Count changes
        additions = sum(1 for line in unified_diff if line.startswith('+') and not line.startswith('+++'))
        deletions = sum(1 for line in unified_diff if line.startswith('-') and not line.startswith('---'))
        
        # If no unified diff changes detected but content is different, count as one change
        if additions == 0 and deletions == 0 and old_content != new_content:
            if len(new_content) > len(old_content):
                additions = 1
            elif len(new_content) < len(old_content):
                deletions = 1
            else:
                additions = 1  # Content changed but same length
        
        return {
            'unified_diff': unified_diff,
            'html_diff': html_table,
            'similarity_ratio': similarity_ratio,
            'additions': additions,
            'deletions': deletions,
            'total_changes': additions + deletions
        }
    
    @staticmethod
    def generate_word_diff(old_content: str, new_content: str) -> Dict[str, Any]:
        """Generate a word-level diff between two content versions"""
        old_words = old_content.split()
        new_words = new_content.split()
        
        differ = difflib.SequenceMatcher(None, old_words, new_words)
        
        word_changes = []
        for tag, i1, i2, j1, j2 in differ.get_opcodes():
            if tag == 'replace':
                word_changes.append({
                    'type': 'replace',
                    'old_words': old_words[i1:i2],
                    'new_words': new_words[j1:j2],
                    'position': i1
                })
            elif tag == 'delete':
                word_changes.append({
                    'type': 'delete',
                    'old_words': old_words[i1:i2],
                    'position': i1
                })
            elif tag == 'insert':
                word_changes.append({
                    'type': 'insert',
                    'new_words': new_words[j1:j2],
                    'position': i1
                })
        
        return {
            'word_changes': word_changes,
            'similarity_ratio': differ.ratio()
        }


class VersionHistoryManager:
    """
    Manages version history and change tracking for documents.
    Provides functionality to create versions, track changes, and generate diffs.
    """
    
    def __init__(self, config: Dict[str, Any] = None):
        self.config = config or {}
        
        # Storage (in-memory for demo, would use database in production)
        self.versions: Dict[str, List[DocumentVersion]] = {}  # document_id -> versions
        self.changes: Dict[str, List[ChangeRecord]] = {}  # document_id -> changes
        self.user_activities: Dict[str, List[UserActivity]] = {}  # document_id -> activities
        
        # Configuration
        self.max_versions_per_document = self.config.get('max_versions_per_document', 100)
        self.max_changes_per_document = self.config.get('max_changes_per_document', 1000)
        self.max_activities_per_document = self.config.get('max_activities_per_document', 1000)
        self.auto_version_interval = self.config.get('auto_version_interval_minutes', 5)
        
        logger.info("VersionHistoryManager initialized")
    
    def _generate_content_hash(self, content: str) -> str:
        """Generate hash for content"""
        return hashlib.sha256(content.encode('utf-8')).hexdigest()
    
    def _generate_id(self) -> str:
        """Generate unique ID"""
        return hashlib.sha256(f"{time.time()}".encode()).hexdigest()[:16]
    
    def create_version(self, document_id: str, content: str, user_id: str, 
                      username: str, change_summary: str = "", 
                      metadata: Dict[str, Any] = None) -> DocumentVersion:
        """
        Create a new version of a document
        
        Args:
            document_id: Document identifier
            content: Document content
            user_id: User who created the version
            username: Username of the creator
            change_summary: Summary of changes made
            metadata: Additional metadata
        
        Returns:
            Created DocumentVersion
        """
        try:
            if document_id not in self.versions:
                self.versions[document_id] = []
            
            # Get current version number
            current_versions = self.versions[document_id]
            version_number = len(current_versions) + 1
            
            # Get parent version
            parent_version = None
            if current_versions:
                parent_version = current_versions[-1].version_id
            
            # Create version
            version = DocumentVersion(
                version_id=self._generate_id(),
                document_id=document_id,
                version_number=version_number,
                content=content,
                content_hash=self._generate_content_hash(content),
                created_at=datetime.now(),
                created_by=user_id,
                created_by_username=username,
                change_summary=change_summary or f"Version {version_number}",
                metadata=metadata or {},
                parent_version=parent_version
            )
            
            # Add to versions
            self.versions[document_id].append(version)
            
            # Limit number of versions
            if len(self.versions[document_id]) > self.max_versions_per_document:
                self.versions[document_id] = self.versions[document_id][-self.max_versions_per_document:]
            
            # Record change
            self.record_change(
                document_id=document_id,
                version_id=version.version_id,
                change_type=ChangeType.CONTENT_CHANGE,
                user_id=user_id,
                username=username,
                description=f"Created version {version_number}: {change_summary}",
                details={'version_number': version_number, 'content_length': len(content)}
            )
            
            logger.info(f"Created version {version_number} for document {document_id}")
            return version
            
        except Exception as e:
            logger.error(f"Error creating version: {str(e)}")
            raise
    
    def get_version_history(self, document_id: str, limit: int = None) -> List[DocumentVersion]:
        """
        Get version history for a document
        
        Args:
            document_id: Document identifier
            limit: Maximum number of versions to return
        
        Returns:
            List of DocumentVersion objects
        """
        if document_id not in self.versions:
            return []
        
        versions = self.versions[document_id]
        if limit:
            return versions[-limit:]
        return versions
    
    def get_version_by_id(self, document_id: str, version_id: str) -> Optional[DocumentVersion]:
        """Get a specific version by ID"""
        if document_id not in self.versions:
            return None
        
        for version in self.versions[document_id]:
            if version.version_id == version_id:
                return version
        return None
    
    def get_version_by_number(self, document_id: str, version_number: int) -> Optional[DocumentVersion]:
        """Get a specific version by number"""
        if document_id not in self.versions:
            return None
        
        for version in self.versions[document_id]:
            if version.version_number == version_number:
                return version
        return None
    
    def get_latest_version(self, document_id: str) -> Optional[DocumentVersion]:
        """Get the latest version of a document"""
        if document_id not in self.versions or not self.versions[document_id]:
            return None
        
        return self.versions[document_id][-1]
    
    def compare_versions(self, document_id: str, version1_id: str, 
                        version2_id: str) -> Dict[str, Any]:
        """
        Compare two versions of a document
        
        Args:
            document_id: Document identifier
            version1_id: First version ID
            version2_id: Second version ID
        
        Returns:
            Dictionary containing comparison results
        """
        try:
            version1 = self.get_version_by_id(document_id, version1_id)
            version2 = self.get_version_by_id(document_id, version2_id)
            
            if not version1 or not version2:
                return {
                    'success': False,
                    'error': 'One or both versions not found'
                }
            
            # Generate diffs
            text_diff = DiffGenerator.generate_text_diff(version1.content, version2.content)
            word_diff = DiffGenerator.generate_word_diff(version1.content, version2.content)
            
            return {
                'success': True,
                'version1': version1.to_dict(),
                'version2': version2.to_dict(),
                'text_diff': text_diff,
                'word_diff': word_diff,
                'time_difference': (version2.created_at - version1.created_at).total_seconds()
            }
            
        except Exception as e:
            logger.error(f"Error comparing versions: {str(e)}")
            return {
                'success': False,
                'error': 'Comparison failed'
            }
    
    def record_change(self, document_id: str, version_id: str, change_type: ChangeType,
                     user_id: str, username: str, description: str,
                     details: Dict[str, Any] = None, before_state: str = None,
                     after_state: str = None) -> ChangeRecord:
        """
        Record a change to a document
        
        Args:
            document_id: Document identifier
            version_id: Version identifier
            change_type: Type of change
            user_id: User who made the change
            username: Username of the user
            description: Description of the change
            details: Additional details
            before_state: State before change
            after_state: State after change
        
        Returns:
            Created ChangeRecord
        """
        try:
            if document_id not in self.changes:
                self.changes[document_id] = []
            
            change = ChangeRecord(
                change_id=self._generate_id(),
                document_id=document_id,
                version_id=version_id,
                change_type=change_type,
                user_id=user_id,
                username=username,
                timestamp=datetime.now(),
                description=description,
                details=details or {},
                before_state=before_state,
                after_state=after_state
            )
            
            self.changes[document_id].append(change)
            
            # Limit number of changes
            if len(self.changes[document_id]) > self.max_changes_per_document:
                self.changes[document_id] = self.changes[document_id][-self.max_changes_per_document:]
            
            logger.debug(f"Recorded change: {change_type.value} for document {document_id}")
            return change
            
        except Exception as e:
            logger.error(f"Error recording change: {str(e)}")
            raise
    
    def get_change_history(self, document_id: str, limit: int = None,
                          change_type: ChangeType = None,
                          user_id: str = None) -> List[ChangeRecord]:
        """
        Get change history for a document
        
        Args:
            document_id: Document identifier
            limit: Maximum number of changes to return
            change_type: Filter by change type
            user_id: Filter by user ID
        
        Returns:
            List of ChangeRecord objects
        """
        if document_id not in self.changes:
            return []
        
        changes = self.changes[document_id]
        
        # Apply filters
        if change_type:
            changes = [c for c in changes if c.change_type == change_type]
        
        if user_id:
            changes = [c for c in changes if c.user_id == user_id]
        
        # Apply limit
        if limit:
            changes = changes[-limit:]
        
        return changes
    
    def record_user_activity(self, user_id: str, username: str, document_id: str,
                           activity_type: str, details: Dict[str, Any] = None,
                           session_id: str = None) -> UserActivity:
        """
        Record user activity in a document
        
        Args:
            user_id: User identifier
            username: Username
            document_id: Document identifier
            activity_type: Type of activity
            details: Additional details
            session_id: Session identifier
        
        Returns:
            Created UserActivity
        """
        try:
            if document_id not in self.user_activities:
                self.user_activities[document_id] = []
            
            activity = UserActivity(
                activity_id=self._generate_id(),
                user_id=user_id,
                username=username,
                document_id=document_id,
                activity_type=activity_type,
                timestamp=datetime.now(),
                details=details or {},
                session_id=session_id
            )
            
            self.user_activities[document_id].append(activity)
            
            # Limit number of activities
            if len(self.user_activities[document_id]) > self.max_activities_per_document:
                self.user_activities[document_id] = self.user_activities[document_id][-self.max_activities_per_document:]
            
            logger.debug(f"Recorded activity: {activity_type} by {username} in document {document_id}")
            return activity
            
        except Exception as e:
            logger.error(f"Error recording user activity: {str(e)}")
            raise
    
    def get_user_activities(self, document_id: str, limit: int = None,
                           user_id: str = None, activity_type: str = None,
                           since: datetime = None) -> List[UserActivity]:
        """
        Get user activities for a document
        
        Args:
            document_id: Document identifier
            limit: Maximum number of activities to return
            user_id: Filter by user ID
            activity_type: Filter by activity type
            since: Filter activities since this timestamp
        
        Returns:
            List of UserActivity objects
        """
        if document_id not in self.user_activities:
            return []
        
        activities = self.user_activities[document_id]
        
        # Apply filters
        if user_id:
            activities = [a for a in activities if a.user_id == user_id]
        
        if activity_type:
            activities = [a for a in activities if a.activity_type == activity_type]
        
        if since:
            activities = [a for a in activities if a.timestamp >= since]
        
        # Apply limit
        if limit:
            activities = activities[-limit:]
        
        return activities
    
    def get_document_statistics(self, document_id: str) -> Dict[str, Any]:
        """
        Get statistics for a document
        
        Args:
            document_id: Document identifier
        
        Returns:
            Dictionary containing document statistics
        """
        try:
            versions = self.get_version_history(document_id)
            changes = self.get_change_history(document_id)
            activities = self.get_user_activities(document_id)
            
            if not versions:
                return {
                    'document_id': document_id,
                    'total_versions': 0,
                    'total_changes': 0,
                    'total_activities': 0
                }
            
            # Calculate statistics
            latest_version = versions[-1]
            first_version = versions[0]
            
            # User statistics
            unique_contributors = set()
            for version in versions:
                unique_contributors.add(version.created_by)
            
            # Activity statistics
            activity_types = {}
            for activity in activities:
                activity_types[activity.activity_type] = activity_types.get(activity.activity_type, 0) + 1
            
            # Change statistics
            change_types = {}
            for change in changes:
                change_types[change.change_type.value] = change_types.get(change.change_type.value, 0) + 1
            
            return {
                'document_id': document_id,
                'total_versions': len(versions),
                'total_changes': len(changes),
                'total_activities': len(activities),
                'unique_contributors': len(unique_contributors),
                'first_version_date': first_version.created_at.isoformat(),
                'latest_version_date': latest_version.created_at.isoformat(),
                'latest_version_number': latest_version.version_number,
                'content_length': len(latest_version.content),
                'activity_types': activity_types,
                'change_types': change_types,
                'contributors': list(unique_contributors)
            }
            
        except Exception as e:
            logger.error(f"Error getting document statistics: {str(e)}")
            return {
                'document_id': document_id,
                'error': 'Failed to get statistics'
            }
    
    def revert_to_version(self, document_id: str, version_id: str, user_id: str,
                         username: str) -> Optional[DocumentVersion]:
        """
        Revert document to a previous version
        
        Args:
            document_id: Document identifier
            version_id: Version to revert to
            user_id: User performing the revert
            username: Username of the user
        
        Returns:
            New version created from the revert
        """
        try:
            target_version = self.get_version_by_id(document_id, version_id)
            if not target_version:
                return None
            
            # Create new version with reverted content
            new_version = self.create_version(
                document_id=document_id,
                content=target_version.content,
                user_id=user_id,
                username=username,
                change_summary=f"Reverted to version {target_version.version_number}",
                metadata={
                    'reverted_from': version_id,
                    'reverted_from_version': target_version.version_number
                }
            )
            
            # Record the revert activity
            self.record_user_activity(
                user_id=user_id,
                username=username,
                document_id=document_id,
                activity_type="revert",
                details={
                    'reverted_to_version': target_version.version_number,
                    'reverted_to_version_id': version_id,
                    'new_version_id': new_version.version_id
                }
            )
            
            logger.info(f"Reverted document {document_id} to version {target_version.version_number}")
            return new_version
            
        except Exception as e:
            logger.error(f"Error reverting to version: {str(e)}")
            return None
    
    def cleanup_old_data(self, older_than_days: int = 30):
        """
        Clean up old version history data
        
        Args:
            older_than_days: Remove data older than this many days
        """
        try:
            cutoff_date = datetime.now() - timedelta(days=older_than_days)
            
            # Clean up versions
            for document_id in list(self.versions.keys()):
                self.versions[document_id] = [
                    v for v in self.versions[document_id]
                    if v.created_at >= cutoff_date
                ]
                if not self.versions[document_id]:
                    del self.versions[document_id]
            
            # Clean up changes
            for document_id in list(self.changes.keys()):
                self.changes[document_id] = [
                    c for c in self.changes[document_id]
                    if c.timestamp >= cutoff_date
                ]
                if not self.changes[document_id]:
                    del self.changes[document_id]
            
            # Clean up activities
            for document_id in list(self.user_activities.keys()):
                self.user_activities[document_id] = [
                    a for a in self.user_activities[document_id]
                    if a.timestamp >= cutoff_date
                ]
                if not self.user_activities[document_id]:
                    del self.user_activities[document_id]
            
            logger.info(f"Cleaned up data older than {older_than_days} days")
            
        except Exception as e:
            logger.error(f"Error cleaning up old data: {str(e)}")