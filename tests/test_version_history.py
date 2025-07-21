"""
Unit tests for Version History and Change Tracking
"""

import pytest
from datetime import datetime, timedelta
import time

from app.auth.version_history import (
    VersionHistoryManager, DocumentVersion, ChangeRecord, UserActivity,
    ChangeType, DiffGenerator
)


class TestDiffGenerator:
    """Test cases for DiffGenerator"""
    
    def test_generate_text_diff_simple(self):
        """Test simple text diff generation"""
        old_content = "Hello world"
        new_content = "Hello beautiful world"
        
        diff = DiffGenerator.generate_text_diff(old_content, new_content)
        
        assert 'unified_diff' in diff
        assert 'html_diff' in diff
        assert 'similarity_ratio' in diff
        assert 'additions' in diff
        assert 'deletions' in diff
        assert diff['additions'] > 0
        assert diff['similarity_ratio'] > 0.5
    
    def test_generate_text_diff_identical(self):
        """Test diff generation for identical content"""
        content = "Hello world"
        
        diff = DiffGenerator.generate_text_diff(content, content)
        
        assert diff['similarity_ratio'] == 1.0
        assert diff['additions'] == 0
        assert diff['deletions'] == 0
        assert diff['total_changes'] == 0
    
    def test_generate_word_diff(self):
        """Test word-level diff generation"""
        old_content = "Hello world today"
        new_content = "Hello beautiful world tomorrow"
        
        diff = DiffGenerator.generate_word_diff(old_content, new_content)
        
        assert 'word_changes' in diff
        assert 'similarity_ratio' in diff
        assert len(diff['word_changes']) > 0
        assert diff['similarity_ratio'] > 0


class TestDocumentVersion:
    """Test cases for DocumentVersion"""
    
    def test_version_creation(self):
        """Test document version creation"""
        now = datetime.now()
        version = DocumentVersion(
            version_id="v123",
            document_id="doc1",
            version_number=1,
            content="Hello world",
            content_hash="hash123",
            created_at=now,
            created_by="user1",
            created_by_username="testuser",
            change_summary="Initial version",
            metadata={"test": "data"}
        )
        
        assert version.version_id == "v123"
        assert version.document_id == "doc1"
        assert version.version_number == 1
        assert version.content == "Hello world"
        assert version.created_by == "user1"
        assert version.change_summary == "Initial version"
    
    def test_version_to_dict(self):
        """Test version to dictionary conversion"""
        now = datetime.now()
        version = DocumentVersion(
            version_id="v123",
            document_id="doc1",
            version_number=1,
            content="Hello world",
            content_hash="hash123",
            created_at=now,
            created_by="user1",
            created_by_username="testuser",
            change_summary="Initial version",
            metadata={"test": "data"}
        )
        
        version_dict = version.to_dict()
        
        assert version_dict['version_id'] == "v123"
        assert version_dict['document_id'] == "doc1"
        assert version_dict['version_number'] == 1
        assert version_dict['content'] == "Hello world"
        assert version_dict['created_by'] == "user1"
        assert version_dict['metadata']['test'] == "data"
    
    def test_version_from_dict(self):
        """Test version creation from dictionary"""
        now = datetime.now()
        version_data = {
            'version_id': 'v123',
            'document_id': 'doc1',
            'version_number': 1,
            'content': 'Hello world',
            'content_hash': 'hash123',
            'created_at': now.isoformat(),
            'created_by': 'user1',
            'created_by_username': 'testuser',
            'change_summary': 'Initial version',
            'metadata': {'test': 'data'}
        }
        
        version = DocumentVersion.from_dict(version_data)
        
        assert version.version_id == "v123"
        assert version.document_id == "doc1"
        assert version.version_number == 1
        assert version.content == "Hello world"
        assert version.created_by == "user1"


class TestChangeRecord:
    """Test cases for ChangeRecord"""
    
    def test_change_record_creation(self):
        """Test change record creation"""
        now = datetime.now()
        change = ChangeRecord(
            change_id="c123",
            document_id="doc1",
            version_id="v123",
            change_type=ChangeType.CONTENT_CHANGE,
            user_id="user1",
            username="testuser",
            timestamp=now,
            description="Content updated",
            details={"lines_changed": 5}
        )
        
        assert change.change_id == "c123"
        assert change.document_id == "doc1"
        assert change.change_type == ChangeType.CONTENT_CHANGE
        assert change.user_id == "user1"
        assert change.description == "Content updated"
    
    def test_change_record_to_dict(self):
        """Test change record to dictionary conversion"""
        now = datetime.now()
        change = ChangeRecord(
            change_id="c123",
            document_id="doc1",
            version_id="v123",
            change_type=ChangeType.CONTENT_CHANGE,
            user_id="user1",
            username="testuser",
            timestamp=now,
            description="Content updated",
            details={"lines_changed": 5}
        )
        
        change_dict = change.to_dict()
        
        assert change_dict['change_id'] == "c123"
        assert change_dict['change_type'] == "content_change"
        assert change_dict['user_id'] == "user1"
        assert change_dict['details']['lines_changed'] == 5
    
    def test_change_record_from_dict(self):
        """Test change record creation from dictionary"""
        now = datetime.now()
        change_data = {
            'change_id': 'c123',
            'document_id': 'doc1',
            'version_id': 'v123',
            'change_type': 'content_change',
            'user_id': 'user1',
            'username': 'testuser',
            'timestamp': now.isoformat(),
            'description': 'Content updated',
            'details': {'lines_changed': 5}
        }
        
        change = ChangeRecord.from_dict(change_data)
        
        assert change.change_id == "c123"
        assert change.change_type == ChangeType.CONTENT_CHANGE
        assert change.user_id == "user1"
        assert change.details['lines_changed'] == 5


class TestUserActivity:
    """Test cases for UserActivity"""
    
    def test_user_activity_creation(self):
        """Test user activity creation"""
        now = datetime.now()
        activity = UserActivity(
            activity_id="a123",
            user_id="user1",
            username="testuser",
            document_id="doc1",
            activity_type="edit",
            timestamp=now,
            details={"action": "typing"}
        )
        
        assert activity.activity_id == "a123"
        assert activity.user_id == "user1"
        assert activity.username == "testuser"
        assert activity.document_id == "doc1"
        assert activity.activity_type == "edit"
    
    def test_user_activity_to_dict(self):
        """Test user activity to dictionary conversion"""
        now = datetime.now()
        activity = UserActivity(
            activity_id="a123",
            user_id="user1",
            username="testuser",
            document_id="doc1",
            activity_type="edit",
            timestamp=now,
            details={"action": "typing"}
        )
        
        activity_dict = activity.to_dict()
        
        assert activity_dict['activity_id'] == "a123"
        assert activity_dict['user_id'] == "user1"
        assert activity_dict['activity_type'] == "edit"
        assert activity_dict['details']['action'] == "typing"
    
    def test_user_activity_from_dict(self):
        """Test user activity creation from dictionary"""
        now = datetime.now()
        activity_data = {
            'activity_id': 'a123',
            'user_id': 'user1',
            'username': 'testuser',
            'document_id': 'doc1',
            'activity_type': 'edit',
            'timestamp': now.isoformat(),
            'details': {'action': 'typing'}
        }
        
        activity = UserActivity.from_dict(activity_data)
        
        assert activity.activity_id == "a123"
        assert activity.user_id == "user1"
        assert activity.activity_type == "edit"
        assert activity.details['action'] == "typing"


class TestVersionHistoryManager:
    """Test cases for VersionHistoryManager"""
    
    @pytest.fixture
    def manager(self):
        """Create a test version history manager"""
        return VersionHistoryManager({
            'max_versions_per_document': 10,
            'max_changes_per_document': 50,
            'max_activities_per_document': 100
        })
    
    def test_manager_initialization(self, manager):
        """Test manager initialization"""
        assert manager.max_versions_per_document == 10
        assert manager.max_changes_per_document == 50
        assert manager.max_activities_per_document == 100
        assert len(manager.versions) == 0
        assert len(manager.changes) == 0
        assert len(manager.user_activities) == 0
    
    def test_create_version(self, manager):
        """Test creating a document version"""
        version = manager.create_version(
            document_id="doc1",
            content="Hello world",
            user_id="user1",
            username="testuser",
            change_summary="Initial version"
        )
        
        assert version.document_id == "doc1"
        assert version.content == "Hello world"
        assert version.version_number == 1
        assert version.created_by == "user1"
        assert version.change_summary == "Initial version"
        assert version.parent_version is None
        
        # Check that version was stored
        assert "doc1" in manager.versions
        assert len(manager.versions["doc1"]) == 1
    
    def test_create_multiple_versions(self, manager):
        """Test creating multiple versions"""
        # Create first version
        v1 = manager.create_version(
            document_id="doc1",
            content="Hello world",
            user_id="user1",
            username="testuser",
            change_summary="Initial version"
        )
        
        # Create second version
        v2 = manager.create_version(
            document_id="doc1",
            content="Hello beautiful world",
            user_id="user1",
            username="testuser",
            change_summary="Added adjective"
        )
        
        assert v1.version_number == 1
        assert v2.version_number == 2
        assert v2.parent_version == v1.version_id
        assert len(manager.versions["doc1"]) == 2
    
    def test_get_version_history(self, manager):
        """Test getting version history"""
        # Create versions
        manager.create_version("doc1", "Version 1", "user1", "testuser")
        manager.create_version("doc1", "Version 2", "user1", "testuser")
        manager.create_version("doc1", "Version 3", "user1", "testuser")
        
        # Get all versions
        history = manager.get_version_history("doc1")
        assert len(history) == 3
        
        # Get limited versions
        limited_history = manager.get_version_history("doc1", limit=2)
        assert len(limited_history) == 2
        assert limited_history[-1].version_number == 3  # Latest versions
    
    def test_get_version_by_id(self, manager):
        """Test getting version by ID"""
        version = manager.create_version("doc1", "Hello world", "user1", "testuser")
        
        retrieved = manager.get_version_by_id("doc1", version.version_id)
        
        assert retrieved is not None
        assert retrieved.version_id == version.version_id
        assert retrieved.content == "Hello world"
    
    def test_get_version_by_number(self, manager):
        """Test getting version by number"""
        manager.create_version("doc1", "Version 1", "user1", "testuser")
        manager.create_version("doc1", "Version 2", "user1", "testuser")
        
        version = manager.get_version_by_number("doc1", 2)
        
        assert version is not None
        assert version.version_number == 2
        assert version.content == "Version 2"
    
    def test_get_latest_version(self, manager):
        """Test getting latest version"""
        manager.create_version("doc1", "Version 1", "user1", "testuser")
        manager.create_version("doc1", "Version 2", "user1", "testuser")
        manager.create_version("doc1", "Version 3", "user1", "testuser")
        
        latest = manager.get_latest_version("doc1")
        
        assert latest is not None
        assert latest.version_number == 3
        assert latest.content == "Version 3"
    
    def test_compare_versions(self, manager):
        """Test comparing versions"""
        v1 = manager.create_version("doc1", "Hello world", "user1", "testuser")
        v2 = manager.create_version("doc1", "Hello beautiful world", "user1", "testuser")
        
        # Verify versions were created correctly
        assert v1.content == "Hello world"
        assert v2.content == "Hello beautiful world"
        
        comparison = manager.compare_versions("doc1", v1.version_id, v2.version_id)
        
        assert comparison['success'] is True
        assert 'version1' in comparison
        assert 'version2' in comparison
        assert 'text_diff' in comparison
        assert 'word_diff' in comparison
        assert 'time_difference' in comparison
    
    def test_record_change(self, manager):
        """Test recording a change"""
        version = manager.create_version("doc1", "Hello world", "user1", "testuser")
        
        change = manager.record_change(
            document_id="doc1",
            version_id=version.version_id,
            change_type=ChangeType.CONTENT_CHANGE,
            user_id="user1",
            username="testuser",
            description="Updated content",
            details={"lines_changed": 1}
        )
        
        assert change.document_id == "doc1"
        assert change.change_type == ChangeType.CONTENT_CHANGE
        assert change.description == "Updated content"
        assert change.details['lines_changed'] == 1
        
        # Check that change was stored
        assert "doc1" in manager.changes
        # Note: create_version also records a change, so we expect 2 changes
        assert len(manager.changes["doc1"]) == 2
    
    def test_get_change_history(self, manager):
        """Test getting change history"""
        version = manager.create_version("doc1", "Hello world", "user1", "testuser")
        
        manager.record_change(
            document_id="doc1",
            version_id=version.version_id,
            change_type=ChangeType.CONTENT_CHANGE,
            user_id="user1",
            username="testuser",
            description="Change 1"
        )
        
        manager.record_change(
            document_id="doc1",
            version_id=version.version_id,
            change_type=ChangeType.METADATA_CHANGE,
            user_id="user2",
            username="testuser2",
            description="Change 2"
        )
        
        # Get all changes
        all_changes = manager.get_change_history("doc1")
        assert len(all_changes) == 3  # Including the one from create_version
        
        # Filter by change type
        content_changes = manager.get_change_history("doc1", change_type=ChangeType.CONTENT_CHANGE)
        assert len(content_changes) == 2  # create_version + manual record
        
        # Filter by user
        user1_changes = manager.get_change_history("doc1", user_id="user1")
        assert len(user1_changes) == 2
    
    def test_record_user_activity(self, manager):
        """Test recording user activity"""
        activity = manager.record_user_activity(
            user_id="user1",
            username="testuser",
            document_id="doc1",
            activity_type="edit",
            details={"action": "typing"},
            session_id="session123"
        )
        
        assert activity.user_id == "user1"
        assert activity.username == "testuser"
        assert activity.document_id == "doc1"
        assert activity.activity_type == "edit"
        assert activity.details['action'] == "typing"
        assert activity.session_id == "session123"
        
        # Check that activity was stored
        assert "doc1" in manager.user_activities
        assert len(manager.user_activities["doc1"]) == 1
    
    def test_get_user_activities(self, manager):
        """Test getting user activities"""
        manager.record_user_activity("user1", "testuser1", "doc1", "edit", {"action": "typing"})
        manager.record_user_activity("user2", "testuser2", "doc1", "view", {"action": "reading"})
        manager.record_user_activity("user1", "testuser1", "doc1", "save", {"action": "saving"})
        
        # Get all activities
        all_activities = manager.get_user_activities("doc1")
        assert len(all_activities) == 3
        
        # Filter by user
        user1_activities = manager.get_user_activities("doc1", user_id="user1")
        assert len(user1_activities) == 2
        
        # Filter by activity type
        edit_activities = manager.get_user_activities("doc1", activity_type="edit")
        assert len(edit_activities) == 1
    
    def test_get_document_statistics(self, manager):
        """Test getting document statistics"""
        # Create some data
        manager.create_version("doc1", "Version 1", "user1", "testuser1")
        manager.create_version("doc1", "Version 2", "user2", "testuser2")
        manager.record_user_activity("user1", "testuser1", "doc1", "edit")
        manager.record_user_activity("user2", "testuser2", "doc1", "view")
        
        stats = manager.get_document_statistics("doc1")
        
        assert stats['document_id'] == "doc1"
        assert stats['total_versions'] == 2
        assert stats['total_changes'] == 2  # One per version creation
        assert stats['total_activities'] == 2
        assert stats['unique_contributors'] == 2
        assert stats['latest_version_number'] == 2
        assert 'first_version_date' in stats
        assert 'latest_version_date' in stats
    
    def test_revert_to_version(self, manager):
        """Test reverting to a previous version"""
        v1 = manager.create_version("doc1", "Original content", "user1", "testuser")
        v2 = manager.create_version("doc1", "Modified content", "user1", "testuser")
        
        # Revert to v1
        reverted = manager.revert_to_version("doc1", v1.version_id, "user1", "testuser")
        
        assert reverted is not None
        assert reverted.content == "Original content"
        assert reverted.version_number == 3  # New version number
        assert "Reverted to version 1" in reverted.change_summary
        assert reverted.metadata['reverted_from'] == v1.version_id
        
        # Check that revert activity was recorded
        activities = manager.get_user_activities("doc1", activity_type="revert")
        assert len(activities) == 1
    
    def test_cleanup_old_data(self, manager):
        """Test cleaning up old data"""
        # Create some old data
        old_time = datetime.now() - timedelta(days=35)
        
        # Manually create old version (simulating old data)
        old_version = manager.create_version("doc1", "Old content", "user1", "testuser")
        old_version.created_at = old_time
        
        # Create recent data
        manager.create_version("doc1", "Recent content", "user1", "testuser")
        
        # Cleanup data older than 30 days
        manager.cleanup_old_data(older_than_days=30)
        
        # Check that old data was removed and recent data remains
        versions = manager.get_version_history("doc1")
        assert len(versions) == 1
        assert versions[0].content == "Recent content"
    
    def test_nonexistent_document(self, manager):
        """Test operations on non-existent document"""
        # Test getting history for non-existent document
        history = manager.get_version_history("nonexistent")
        assert len(history) == 0
        
        # Test getting latest version for non-existent document
        latest = manager.get_latest_version("nonexistent")
        assert latest is None
        
        # Test getting version by ID for non-existent document
        version = manager.get_version_by_id("nonexistent", "v123")
        assert version is None