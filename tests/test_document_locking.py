"""
Unit tests for Document Locking and Finalization
"""

import pytest
import asyncio
from datetime import datetime, timedelta
import time

from app.auth.document_locking import (
    DocumentLockingManager, DocumentLock, DocumentState, Notification,
    LockType, DocumentStatus, NotificationType
)


class TestDocumentLock:
    """Test cases for DocumentLock"""
    
    def test_lock_creation(self):
        """Test document lock creation"""
        now = datetime.now()
        expires_at = now + timedelta(hours=1)
        
        lock = DocumentLock(
            lock_id="lock123",
            document_id="doc1",
            lock_type=LockType.EDIT_LOCK,
            locked_by="user1",
            locked_by_username="testuser",
            locked_at=now,
            expires_at=expires_at,
            reason="Testing",
            metadata={"test": "data"}
        )
        
        assert lock.lock_id == "lock123"
        assert lock.document_id == "doc1"
        assert lock.lock_type == LockType.EDIT_LOCK
        assert lock.locked_by == "user1"
        assert lock.reason == "Testing"
        assert lock.is_active is True
    
    def test_lock_expiry_check(self):
        """Test lock expiry checking"""
        now = datetime.now()
        
        # Expired lock
        expired_lock = DocumentLock(
            lock_id="lock1",
            document_id="doc1",
            lock_type=LockType.EDIT_LOCK,
            locked_by="user1",
            locked_by_username="testuser",
            locked_at=now - timedelta(hours=2),
            expires_at=now - timedelta(hours=1),
            reason="Test",
            metadata={}
        )
        
        # Valid lock
        valid_lock = DocumentLock(
            lock_id="lock2",
            document_id="doc1",
            lock_type=LockType.EDIT_LOCK,
            locked_by="user1",
            locked_by_username="testuser",
            locked_at=now,
            expires_at=now + timedelta(hours=1),
            reason="Test",
            metadata={}
        )
        
        # Permanent lock (no expiry)
        permanent_lock = DocumentLock(
            lock_id="lock3",
            document_id="doc1",
            lock_type=LockType.ADMIN_LOCK,
            locked_by="admin",
            locked_by_username="admin",
            locked_at=now,
            expires_at=None,
            reason="Admin lock",
            metadata={}
        )
        
        assert expired_lock.is_expired() is True
        assert valid_lock.is_expired() is False
        assert permanent_lock.is_expired() is False
    
    def test_lock_to_dict(self):
        """Test lock to dictionary conversion"""
        now = datetime.now()
        expires_at = now + timedelta(hours=1)
        
        lock = DocumentLock(
            lock_id="lock123",
            document_id="doc1",
            lock_type=LockType.EDIT_LOCK,
            locked_by="user1",
            locked_by_username="testuser",
            locked_at=now,
            expires_at=expires_at,
            reason="Testing",
            metadata={"test": "data"}
        )
        
        lock_dict = lock.to_dict()
        
        assert lock_dict['lock_id'] == "lock123"
        assert lock_dict['lock_type'] == "edit_lock"
        assert lock_dict['locked_by'] == "user1"
        assert lock_dict['reason'] == "Testing"
        assert lock_dict['metadata']['test'] == "data"
    
    def test_lock_from_dict(self):
        """Test lock creation from dictionary"""
        now = datetime.now()
        expires_at = now + timedelta(hours=1)
        
        lock_data = {
            'lock_id': 'lock123',
            'document_id': 'doc1',
            'lock_type': 'edit_lock',
            'locked_by': 'user1',
            'locked_by_username': 'testuser',
            'locked_at': now.isoformat(),
            'expires_at': expires_at.isoformat(),
            'reason': 'Testing',
            'metadata': {'test': 'data'},
            'is_active': True
        }
        
        lock = DocumentLock.from_dict(lock_data)
        
        assert lock.lock_id == "lock123"
        assert lock.lock_type == LockType.EDIT_LOCK
        assert lock.locked_by == "user1"
        assert lock.reason == "Testing"


class TestDocumentState:
    """Test cases for DocumentState"""
    
    def test_state_creation(self):
        """Test document state creation"""
        now = datetime.now()
        
        state = DocumentState(
            document_id="doc1",
            status=DocumentStatus.DRAFT,
            current_locks=["lock1", "lock2"],
            finalized_at=None,
            finalized_by=None,
            finalized_by_username=None,
            finalization_reason=None,
            last_modified=now,
            permissions={"user1": ["read", "write"]},
            metadata={"version": 1}
        )
        
        assert state.document_id == "doc1"
        assert state.status == DocumentStatus.DRAFT
        assert len(state.current_locks) == 2
        assert state.finalized_at is None
        assert state.permissions["user1"] == ["read", "write"]
    
    def test_state_to_dict(self):
        """Test state to dictionary conversion"""
        now = datetime.now()
        
        state = DocumentState(
            document_id="doc1",
            status=DocumentStatus.FINALIZED,
            current_locks=[],
            finalized_at=now,
            finalized_by="user1",
            finalized_by_username="testuser",
            finalization_reason="Review complete",
            last_modified=now,
            permissions={},
            metadata={}
        )
        
        state_dict = state.to_dict()
        
        assert state_dict['document_id'] == "doc1"
        assert state_dict['status'] == "finalized"
        assert state_dict['finalized_by'] == "user1"
        assert state_dict['finalization_reason'] == "Review complete"


class TestNotification:
    """Test cases for Notification"""
    
    def test_notification_creation(self):
        """Test notification creation"""
        now = datetime.now()
        
        notification = Notification(
            notification_id="notif123",
            document_id="doc1",
            notification_type=NotificationType.DOCUMENT_LOCKED,
            recipient_id="user1",
            recipient_username="testuser",
            sender_id="user2",
            sender_username="sender",
            title="Document Locked",
            message="Document has been locked",
            created_at=now,
            read_at=None,
            metadata={"lock_type": "edit_lock"}
        )
        
        assert notification.notification_id == "notif123"
        assert notification.notification_type == NotificationType.DOCUMENT_LOCKED
        assert notification.recipient_id == "user1"
        assert notification.title == "Document Locked"
        assert notification.read_at is None
    
    def test_notification_to_dict(self):
        """Test notification to dictionary conversion"""
        now = datetime.now()
        
        notification = Notification(
            notification_id="notif123",
            document_id="doc1",
            notification_type=NotificationType.DOCUMENT_LOCKED,
            recipient_id="user1",
            recipient_username="testuser",
            sender_id="user2",
            sender_username="sender",
            title="Document Locked",
            message="Document has been locked",
            created_at=now,
            read_at=None,
            metadata={"lock_type": "edit_lock"}
        )
        
        notif_dict = notification.to_dict()
        
        assert notif_dict['notification_id'] == "notif123"
        assert notif_dict['notification_type'] == "document_locked"
        assert notif_dict['recipient_id'] == "user1"
        assert notif_dict['title'] == "Document Locked"
        assert notif_dict['metadata']['lock_type'] == "edit_lock"
    
    def test_notification_from_dict(self):
        """Test notification creation from dictionary"""
        now = datetime.now()
        
        notif_data = {
            'notification_id': 'notif123',
            'document_id': 'doc1',
            'notification_type': 'document_locked',
            'recipient_id': 'user1',
            'recipient_username': 'testuser',
            'sender_id': 'user2',
            'sender_username': 'sender',
            'title': 'Document Locked',
            'message': 'Document has been locked',
            'created_at': now.isoformat(),
            'read_at': None,
            'metadata': {'lock_type': 'edit_lock'}
        }
        
        notification = Notification.from_dict(notif_data)
        
        assert notification.notification_id == "notif123"
        assert notification.notification_type == NotificationType.DOCUMENT_LOCKED
        assert notification.recipient_id == "user1"
        assert notification.title == "Document Locked"


class TestDocumentLockingManager:
    """Test cases for DocumentLockingManager"""
    
    @pytest.fixture
    def manager(self):
        """Create a test document locking manager"""
        return DocumentLockingManager({
            'default_lock_duration_minutes': 30,
            'max_lock_duration_hours': 2,
            'finalization_timeout_minutes': 5,
            'notification_retention_days': 7
        })
    
    def test_manager_initialization(self, manager):
        """Test manager initialization"""
        assert manager.default_lock_duration_minutes == 30
        assert manager.max_lock_duration_hours == 2
        assert manager.finalization_timeout_minutes == 5
        assert len(manager.locks) == 0
        assert len(manager.document_states) == 0
    
    def test_lock_document_success(self, manager):
        """Test successful document locking"""
        result = manager.lock_document(
            document_id="doc1",
            user_id="user1",
            username="testuser",
            lock_type=LockType.EDIT_LOCK,
            reason="Testing"
        )
        
        assert result['success'] is True
        assert 'lock' in result
        assert result['lock']['document_id'] == "doc1"
        assert result['lock']['locked_by'] == "user1"
        assert result['lock']['lock_type'] == "edit_lock"
        
        # Check document state
        state = manager.get_document_state("doc1")
        assert state is not None
        assert state.status == DocumentStatus.LOCKED
        assert len(state.current_locks) == 1
    
    def test_lock_document_conflicting_lock(self, manager):
        """Test locking document with conflicting lock"""
        # First user locks document
        manager.lock_document("doc1", "user1", "testuser1", LockType.EDIT_LOCK)
        
        # Second user tries to lock same document
        result = manager.lock_document("doc1", "user2", "testuser2", LockType.EDIT_LOCK)
        
        assert result['success'] is False
        assert "conflicting locks" in result['error']
    
    def test_lock_finalized_document(self, manager):
        """Test locking finalized document"""
        # Finalize document first
        manager.finalize_document("doc1", "user1", "testuser", "Complete")
        
        # Try to lock finalized document
        result = manager.lock_document("doc1", "user2", "testuser2", LockType.EDIT_LOCK)
        
        assert result['success'] is False
        assert "finalized document" in result['error']
    
    def test_unlock_document_success(self, manager):
        """Test successful document unlocking"""
        # Lock document first
        lock_result = manager.lock_document("doc1", "user1", "testuser", LockType.EDIT_LOCK)
        lock_id = lock_result['lock']['lock_id']
        
        # Unlock document
        result = manager.unlock_document("doc1", lock_id, "user1", "testuser")
        
        assert result['success'] is True
        
        # Check document state
        state = manager.get_document_state("doc1")
        assert state.status == DocumentStatus.DRAFT
        assert len(state.current_locks) == 0
    
    def test_unlock_document_not_owner(self, manager):
        """Test unlocking document by non-owner"""
        # Lock document
        lock_result = manager.lock_document("doc1", "user1", "testuser1", LockType.EDIT_LOCK)
        lock_id = lock_result['lock']['lock_id']
        
        # Try to unlock by different user
        result = manager.unlock_document("doc1", lock_id, "user2", "testuser2")
        
        assert result['success'] is False
        assert "Only lock owner" in result['error']
    
    def test_unlock_document_force(self, manager):
        """Test force unlocking document"""
        # Lock document
        lock_result = manager.lock_document("doc1", "user1", "testuser1", LockType.EDIT_LOCK)
        lock_id = lock_result['lock']['lock_id']
        
        # Force unlock by different user
        result = manager.unlock_document("doc1", lock_id, "user2", "testuser2", force=True)
        
        assert result['success'] is True
    
    def test_finalize_document_success(self, manager):
        """Test successful document finalization"""
        result = manager.finalize_document(
            document_id="doc1",
            user_id="user1",
            username="testuser",
            reason="Review complete"
        )
        
        assert result['success'] is True
        assert 'finalized_at' in result
        
        # Check document state
        state = manager.get_document_state("doc1")
        assert state.status == DocumentStatus.FINALIZED
        assert state.finalized_by == "user1"
        assert state.finalization_reason == "Review complete"
    
    def test_finalize_already_finalized(self, manager):
        """Test finalizing already finalized document"""
        # Finalize document
        manager.finalize_document("doc1", "user1", "testuser", "Complete")
        
        # Try to finalize again
        result = manager.finalize_document("doc1", "user2", "testuser2", "Again")
        
        assert result['success'] is False
        assert "already finalized" in result['error']
    
    def test_unfinalize_document_success(self, manager):
        """Test successful document unfinalization"""
        # Finalize document first
        manager.finalize_document("doc1", "user1", "testuser", "Complete")
        
        # Unfinalize document
        result = manager.unfinalize_document("doc1", "admin", "admin", "Needs changes")
        
        assert result['success'] is True
        
        # Check document state
        state = manager.get_document_state("doc1")
        assert state.status == DocumentStatus.DRAFT
        assert state.finalized_at is None
    
    def test_unfinalize_not_finalized(self, manager):
        """Test unfinalizing non-finalized document"""
        result = manager.unfinalize_document("doc1", "admin", "admin", "Test")
        
        assert result['success'] is False
        assert "not finalized" in result['error']
    
    def test_can_user_edit_draft(self, manager):
        """Test user edit permission on draft document"""
        # Draft document - should allow editing
        assert manager.can_user_edit("doc1", "user1") is True
    
    def test_can_user_edit_finalized(self, manager):
        """Test user edit permission on finalized document"""
        # Finalize document
        manager.finalize_document("doc1", "user1", "testuser", "Complete")
        
        # Should not allow editing
        assert manager.can_user_edit("doc1", "user1") is False
        assert manager.can_user_edit("doc1", "user2") is False
    
    def test_can_user_edit_with_lock(self, manager):
        """Test user edit permission with locks"""
        # Lock document by user1
        manager.lock_document("doc1", "user1", "testuser1", LockType.EDIT_LOCK)
        
        # user1 should be able to edit, user2 should not
        assert manager.can_user_edit("doc1", "user1") is True
        assert manager.can_user_edit("doc1", "user2") is False
    
    def test_get_document_locks(self, manager):
        """Test getting document locks"""
        # Lock document with multiple locks
        manager.lock_document("doc1", "user1", "testuser1", LockType.EDIT_LOCK)
        manager.lock_document("doc1", "user1", "testuser1", LockType.TEMPORARY_LOCK)
        
        locks = manager.get_document_locks("doc1")
        
        assert len(locks) == 2
        assert any(lock.lock_type == LockType.EDIT_LOCK for lock in locks)
        assert any(lock.lock_type == LockType.TEMPORARY_LOCK for lock in locks)
    
    def test_get_document_locks_empty(self, manager):
        """Test getting locks for document with no locks"""
        locks = manager.get_document_locks("doc1")
        assert len(locks) == 0
    
    def test_notification_callbacks(self, manager):
        """Test notification callbacks"""
        notifications_received = []
        
        def callback(notification):
            notifications_received.append(notification)
        
        manager.add_notification_callback(callback)
        
        # Set up document state with permissions to trigger notifications
        state = manager._get_or_create_document_state("doc1")
        state.permissions["user2"] = ["read"]
        
        # Lock document to trigger notification
        manager.lock_document("doc1", "user1", "testuser", LockType.EDIT_LOCK)
        
        # Should have received notification
        assert len(notifications_received) > 0
        assert notifications_received[0].notification_type == NotificationType.DOCUMENT_LOCKED
        
        # Remove callback
        manager.remove_notification_callback(callback)
    
    def test_get_user_notifications(self, manager):
        """Test getting user notifications"""
        # Set up document state with permissions to trigger notifications
        state = manager._get_or_create_document_state("doc1")
        state.permissions["user2"] = ["read"]
        
        # Lock document to generate notification
        manager.lock_document("doc1", "user1", "testuser1", LockType.EDIT_LOCK)
        
        # Get notifications for user2
        notifications = manager.get_user_notifications("user2")
        
        assert len(notifications) > 0
        assert notifications[0].notification_type == NotificationType.DOCUMENT_LOCKED
    
    def test_mark_notification_read(self, manager):
        """Test marking notification as read"""
        # Set up document state with permissions
        state = manager._get_or_create_document_state("doc1")
        state.permissions["user2"] = ["read"]
        
        # Lock document to generate notification
        manager.lock_document("doc1", "user1", "testuser1", LockType.EDIT_LOCK)
        
        # Get notification
        notifications = manager.get_user_notifications("user2")
        assert len(notifications) > 0
        
        notification_id = notifications[0].notification_id
        
        # Mark as read
        result = manager.mark_notification_read("user2", notification_id)
        assert result is True
        
        # Check that it's marked as read
        updated_notifications = manager.get_user_notifications("user2")
        assert updated_notifications[0].read_at is not None
    
    def test_cleanup_expired_locks(self, manager):
        """Test cleanup of expired locks"""
        # Create lock with short duration
        lock_result = manager.lock_document(
            "doc1", "user1", "testuser", LockType.EDIT_LOCK, 
            duration_minutes=1
        )
        
        # Manually expire the lock
        lock_id = lock_result['lock']['lock_id']
        lock = manager.locks[lock_id]
        lock.expires_at = datetime.now() - timedelta(minutes=1)
        
        # Run cleanup
        manager.cleanup_expired_locks()
        
        # Lock should be removed
        assert lock_id not in manager.locks
        
        # Document should be unlocked
        state = manager.get_document_state("doc1")
        assert state.status == DocumentStatus.DRAFT
    
    def test_cleanup_old_notifications(self, manager):
        """Test cleanup of old notifications"""
        # Set up document state with permissions
        state = manager._get_or_create_document_state("doc1")
        state.permissions["user1"] = ["read"]
        
        # Generate notification
        manager.lock_document("doc1", "user2", "testuser2", LockType.EDIT_LOCK)
        
        # Manually age the notification
        notifications = manager.get_user_notifications("user1")
        if notifications:
            notifications[0].created_at = datetime.now() - timedelta(days=10)
        
        # Run cleanup (older than 5 days)
        manager.cleanup_old_notifications(older_than_days=5)
        
        # Notification should be removed
        remaining_notifications = manager.get_user_notifications("user1")
        assert len(remaining_notifications) == 0
    
    @pytest.mark.asyncio
    async def test_background_tasks(self, manager):
        """Test background cleanup tasks"""
        # Start background tasks
        await manager.start_background_tasks()
        
        # Wait a short time
        await asyncio.sleep(0.1)
        
        # Stop background tasks
        await manager.stop_background_tasks()
        
        # Should complete without errors
        assert True