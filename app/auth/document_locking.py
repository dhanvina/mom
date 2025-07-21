"""
Document locking and finalization system for collaborative editing.
Handles document locks, finalization workflow, and change notifications.
"""

import asyncio
import json
import logging
import secrets
import time
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any, Set, Callable
from dataclasses import dataclass, asdict
from enum import Enum

logger = logging.getLogger(__name__)


class LockType(Enum):
    """Types of document locks"""
    EDIT_LOCK = "edit_lock"          # Prevents editing by others
    FINALIZATION_LOCK = "finalization_lock"  # Prevents all changes during finalization
    ADMIN_LOCK = "admin_lock"        # Administrative lock
    TEMPORARY_LOCK = "temporary_lock"  # Short-term lock for operations


class DocumentStatus(Enum):
    """Document status states"""
    DRAFT = "draft"
    IN_REVIEW = "in_review"
    LOCKED = "locked"
    FINALIZED = "finalized"
    ARCHIVED = "archived"


class NotificationType(Enum):
    """Types of notifications"""
    DOCUMENT_LOCKED = "document_locked"
    DOCUMENT_UNLOCKED = "document_unlocked"
    DOCUMENT_FINALIZED = "document_finalized"
    LOCK_EXPIRED = "lock_expired"
    FINALIZATION_STARTED = "finalization_started"
    FINALIZATION_COMPLETED = "finalization_completed"
    USER_PERMISSION_CHANGED = "user_permission_changed"


@dataclass
class DocumentLock:
    """Represents a document lock"""
    lock_id: str
    document_id: str
    lock_type: LockType
    locked_by: str
    locked_by_username: str
    locked_at: datetime
    expires_at: Optional[datetime]
    reason: str
    metadata: Dict[str, Any]
    is_active: bool = True
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert lock to dictionary"""
        return {
            'lock_id': self.lock_id,
            'document_id': self.document_id,
            'lock_type': self.lock_type.value,
            'locked_by': self.locked_by,
            'locked_by_username': self.locked_by_username,
            'locked_at': self.locked_at.isoformat(),
            'expires_at': self.expires_at.isoformat() if self.expires_at else None,
            'reason': self.reason,
            'metadata': self.metadata,
            'is_active': self.is_active
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'DocumentLock':
        """Create lock from dictionary"""
        return cls(
            lock_id=data['lock_id'],
            document_id=data['document_id'],
            lock_type=LockType(data['lock_type']),
            locked_by=data['locked_by'],
            locked_by_username=data['locked_by_username'],
            locked_at=datetime.fromisoformat(data['locked_at']),
            expires_at=datetime.fromisoformat(data['expires_at']) if data.get('expires_at') else None,
            reason=data['reason'],
            metadata=data.get('metadata', {}),
            is_active=data.get('is_active', True)
        )
    
    def is_expired(self) -> bool:
        """Check if lock is expired"""
        if not self.expires_at:
            return False
        return datetime.now() > self.expires_at


@dataclass
class DocumentState:
    """Represents the current state of a document"""
    document_id: str
    status: DocumentStatus
    current_locks: List[str]  # List of active lock IDs
    finalized_at: Optional[datetime]
    finalized_by: Optional[str]
    finalized_by_username: Optional[str]
    finalization_reason: Optional[str]
    last_modified: datetime
    permissions: Dict[str, List[str]]  # user_id -> list of permissions
    metadata: Dict[str, Any]
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert state to dictionary"""
        return {
            'document_id': self.document_id,
            'status': self.status.value,
            'current_locks': self.current_locks,
            'finalized_at': self.finalized_at.isoformat() if self.finalized_at else None,
            'finalized_by': self.finalized_by,
            'finalized_by_username': self.finalized_by_username,
            'finalization_reason': self.finalization_reason,
            'last_modified': self.last_modified.isoformat(),
            'permissions': self.permissions,
            'metadata': self.metadata
        }


@dataclass
class Notification:
    """Represents a notification"""
    notification_id: str
    document_id: str
    notification_type: NotificationType
    recipient_id: str
    recipient_username: str
    sender_id: Optional[str]
    sender_username: Optional[str]
    title: str
    message: str
    created_at: datetime
    read_at: Optional[datetime]
    metadata: Dict[str, Any]
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert notification to dictionary"""
        return {
            'notification_id': self.notification_id,
            'document_id': self.document_id,
            'notification_type': self.notification_type.value,
            'recipient_id': self.recipient_id,
            'recipient_username': self.recipient_username,
            'sender_id': self.sender_id,
            'sender_username': self.sender_username,
            'title': self.title,
            'message': self.message,
            'created_at': self.created_at.isoformat(),
            'read_at': self.read_at.isoformat() if self.read_at else None,
            'metadata': self.metadata
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'Notification':
        """Create notification from dictionary"""
        return cls(
            notification_id=data['notification_id'],
            document_id=data['document_id'],
            notification_type=NotificationType(data['notification_type']),
            recipient_id=data['recipient_id'],
            recipient_username=data['recipient_username'],
            sender_id=data.get('sender_id'),
            sender_username=data.get('sender_username'),
            title=data['title'],
            message=data['message'],
            created_at=datetime.fromisoformat(data['created_at']),
            read_at=datetime.fromisoformat(data['read_at']) if data.get('read_at') else None,
            metadata=data.get('metadata', {})
        )


class DocumentLockingManager:
    """
    Manages document locking, finalization, and notifications.
    Provides functionality to lock/unlock documents, finalize them, and notify users.
    """
    
    def __init__(self, config: Dict[str, Any] = None):
        self.config = config or {}
        
        # Storage (in-memory for demo, would use database in production)
        self.locks: Dict[str, DocumentLock] = {}  # lock_id -> lock
        self.document_locks: Dict[str, List[str]] = {}  # document_id -> list of lock_ids
        self.document_states: Dict[str, DocumentState] = {}  # document_id -> state
        self.notifications: Dict[str, List[Notification]] = {}  # user_id -> notifications
        
        # Configuration
        self.default_lock_duration_minutes = self.config.get('default_lock_duration_minutes', 30)
        self.max_lock_duration_hours = self.config.get('max_lock_duration_hours', 24)
        self.finalization_timeout_minutes = self.config.get('finalization_timeout_minutes', 10)
        self.notification_retention_days = self.config.get('notification_retention_days', 30)
        
        # Callbacks for external notifications (e.g., WebSocket, email)
        self.notification_callbacks: List[Callable] = []
        
        # Background task for cleanup
        self._cleanup_task = None
        self._running = False
        
        logger.info("DocumentLockingManager initialized")
    
    def _generate_id(self) -> str:
        """Generate unique ID"""
        return secrets.token_hex(16)
    
    def add_notification_callback(self, callback: Callable[[Notification], None]):
        """Add a callback for notifications"""
        self.notification_callbacks.append(callback)
    
    def remove_notification_callback(self, callback: Callable[[Notification], None]):
        """Remove a notification callback"""
        if callback in self.notification_callbacks:
            self.notification_callbacks.remove(callback)
    
    def _get_or_create_document_state(self, document_id: str) -> DocumentState:
        """Get or create document state"""
        if document_id not in self.document_states:
            self.document_states[document_id] = DocumentState(
                document_id=document_id,
                status=DocumentStatus.DRAFT,
                current_locks=[],
                finalized_at=None,
                finalized_by=None,
                finalized_by_username=None,
                finalization_reason=None,
                last_modified=datetime.now(),
                permissions={},
                metadata={}
            )
        return self.document_states[document_id]
    
    def lock_document(self, document_id: str, user_id: str, username: str,
                     lock_type: LockType = LockType.EDIT_LOCK,
                     duration_minutes: int = None, reason: str = "",
                     metadata: Dict[str, Any] = None) -> Dict[str, Any]:
        """
        Lock a document
        
        Args:
            document_id: Document identifier
            user_id: User requesting the lock
            username: Username of the user
            lock_type: Type of lock to apply
            duration_minutes: Lock duration in minutes
            reason: Reason for locking
            metadata: Additional metadata
        
        Returns:
            Dictionary with lock result
        """
        try:
            document_state = self._get_or_create_document_state(document_id)
            
            # Check if document is finalized
            if document_state.status == DocumentStatus.FINALIZED:
                return {
                    'success': False,
                    'error': 'Cannot lock finalized document'
                }
            
            # Check for conflicting locks
            if self._has_conflicting_lock(document_id, lock_type, user_id):
                return {
                    'success': False,
                    'error': 'Document has conflicting locks'
                }
            
            # Set lock duration
            if duration_minutes is None:
                duration_minutes = self.default_lock_duration_minutes
            
            duration_minutes = min(duration_minutes, self.max_lock_duration_hours * 60)
            expires_at = datetime.now() + timedelta(minutes=duration_minutes)
            
            # Create lock
            lock = DocumentLock(
                lock_id=self._generate_id(),
                document_id=document_id,
                lock_type=lock_type,
                locked_by=user_id,
                locked_by_username=username,
                locked_at=datetime.now(),
                expires_at=expires_at,
                reason=reason,
                metadata=metadata or {},
                is_active=True
            )
            
            # Store lock
            self.locks[lock.lock_id] = lock
            
            if document_id not in self.document_locks:
                self.document_locks[document_id] = []
            self.document_locks[document_id].append(lock.lock_id)
            
            # Update document state
            document_state.current_locks.append(lock.lock_id)
            document_state.status = DocumentStatus.LOCKED
            document_state.last_modified = datetime.now()
            
            # Send notifications
            self._notify_document_locked(document_id, lock)
            
            logger.info(f"Document {document_id} locked by {username} ({lock_type.value})")
            
            return {
                'success': True,
                'lock': lock.to_dict(),
                'message': f'Document locked successfully ({lock_type.value})'
            }
            
        except Exception as e:
            logger.error(f"Error locking document: {str(e)}")
            return {
                'success': False,
                'error': 'Failed to lock document'
            }
    
    def unlock_document(self, document_id: str, lock_id: str, user_id: str,
                       username: str, force: bool = False) -> Dict[str, Any]:
        """
        Unlock a document
        
        Args:
            document_id: Document identifier
            lock_id: Lock identifier to remove
            user_id: User requesting unlock
            username: Username of the user
            force: Force unlock even if not lock owner
        
        Returns:
            Dictionary with unlock result
        """
        try:
            if lock_id not in self.locks:
                return {
                    'success': False,
                    'error': 'Lock not found'
                }
            
            lock = self.locks[lock_id]
            
            # Check permissions
            if not force and lock.locked_by != user_id:
                return {
                    'success': False,
                    'error': 'Only lock owner can unlock document'
                }
            
            # Remove lock
            lock.is_active = False
            del self.locks[lock_id]
            
            # Update document state
            document_state = self._get_or_create_document_state(document_id)
            if lock_id in document_state.current_locks:
                document_state.current_locks.remove(lock_id)
            
            if document_id in self.document_locks:
                if lock_id in self.document_locks[document_id]:
                    self.document_locks[document_id].remove(lock_id)
            
            # Update document status if no more locks
            if not document_state.current_locks:
                document_state.status = DocumentStatus.DRAFT
            
            document_state.last_modified = datetime.now()
            
            # Send notifications
            self._notify_document_unlocked(document_id, lock, user_id, username)
            
            logger.info(f"Document {document_id} unlocked by {username}")
            
            return {
                'success': True,
                'message': 'Document unlocked successfully'
            }
            
        except Exception as e:
            logger.error(f"Error unlocking document: {str(e)}")
            return {
                'success': False,
                'error': 'Failed to unlock document'
            }
    
    def finalize_document(self, document_id: str, user_id: str, username: str,
                         reason: str = "", metadata: Dict[str, Any] = None) -> Dict[str, Any]:
        """
        Finalize a document (make it read-only)
        
        Args:
            document_id: Document identifier
            user_id: User finalizing the document
            username: Username of the user
            reason: Reason for finalization
            metadata: Additional metadata
        
        Returns:
            Dictionary with finalization result
        """
        try:
            document_state = self._get_or_create_document_state(document_id)
            
            # Check if already finalized
            if document_state.status == DocumentStatus.FINALIZED:
                return {
                    'success': False,
                    'error': 'Document is already finalized'
                }
            
            # Apply finalization lock first
            lock_result = self.lock_document(
                document_id=document_id,
                user_id=user_id,
                username=username,
                lock_type=LockType.FINALIZATION_LOCK,
                duration_minutes=self.finalization_timeout_minutes,
                reason=f"Finalization by {username}",
                metadata={'finalization': True}
            )
            
            if not lock_result['success']:
                return {
                    'success': False,
                    'error': f'Cannot finalize: {lock_result["error"]}'
                }
            
            # Send finalization started notification
            self._notify_finalization_started(document_id, user_id, username)
            
            # Update document state
            document_state.status = DocumentStatus.FINALIZED
            document_state.finalized_at = datetime.now()
            document_state.finalized_by = user_id
            document_state.finalized_by_username = username
            document_state.finalization_reason = reason
            document_state.last_modified = datetime.now()
            
            if metadata:
                document_state.metadata.update(metadata)
            
            # Remove all other locks except finalization lock
            locks_to_remove = []
            for lock_id in document_state.current_locks:
                if lock_id in self.locks:
                    lock = self.locks[lock_id]
                    if lock.lock_type != LockType.FINALIZATION_LOCK:
                        locks_to_remove.append(lock_id)
            
            for lock_id in locks_to_remove:
                self.unlock_document(document_id, lock_id, user_id, username, force=True)
            
            # Send finalization completed notification
            self._notify_finalization_completed(document_id, user_id, username, reason)
            
            logger.info(f"Document {document_id} finalized by {username}")
            
            return {
                'success': True,
                'message': 'Document finalized successfully',
                'finalized_at': document_state.finalized_at.isoformat()
            }
            
        except Exception as e:
            logger.error(f"Error finalizing document: {str(e)}")
            return {
                'success': False,
                'error': 'Failed to finalize document'
            }
    
    def unfinalize_document(self, document_id: str, user_id: str, username: str,
                           reason: str = "") -> Dict[str, Any]:
        """
        Unfinalize a document (admin only)
        
        Args:
            document_id: Document identifier
            user_id: User unfinalizing the document
            username: Username of the user
            reason: Reason for unfinalization
        
        Returns:
            Dictionary with unfinalization result
        """
        try:
            document_state = self._get_or_create_document_state(document_id)
            
            # Check if document is finalized
            if document_state.status != DocumentStatus.FINALIZED:
                return {
                    'success': False,
                    'error': 'Document is not finalized'
                }
            
            # Remove finalization
            document_state.status = DocumentStatus.DRAFT
            document_state.finalized_at = None
            document_state.finalized_by = None
            document_state.finalized_by_username = None
            document_state.finalization_reason = None
            document_state.last_modified = datetime.now()
            
            # Remove finalization locks
            locks_to_remove = []
            for lock_id in document_state.current_locks:
                if lock_id in self.locks:
                    lock = self.locks[lock_id]
                    if lock.lock_type == LockType.FINALIZATION_LOCK:
                        locks_to_remove.append(lock_id)
            
            for lock_id in locks_to_remove:
                self.unlock_document(document_id, lock_id, user_id, username, force=True)
            
            # Send notification
            self._send_notification(
                document_id=document_id,
                notification_type=NotificationType.DOCUMENT_UNLOCKED,
                title="Document Unfinalized",
                message=f"Document has been unfinalized by {username}. Reason: {reason}",
                sender_id=user_id,
                sender_username=username
            )
            
            logger.info(f"Document {document_id} unfinalized by {username}")
            
            return {
                'success': True,
                'message': 'Document unfinalized successfully'
            }
            
        except Exception as e:
            logger.error(f"Error unfinalizing document: {str(e)}")
            return {
                'success': False,
                'error': 'Failed to unfinalize document'
            }
    
    def get_document_state(self, document_id: str) -> Optional[DocumentState]:
        """Get current document state"""
        return self.document_states.get(document_id)
    
    def get_document_locks(self, document_id: str) -> List[DocumentLock]:
        """Get all active locks for a document"""
        if document_id not in self.document_locks:
            return []
        
        locks = []
        for lock_id in self.document_locks[document_id]:
            if lock_id in self.locks:
                lock = self.locks[lock_id]
                if lock.is_active and not lock.is_expired():
                    locks.append(lock)
        
        return locks
    
    def can_user_edit(self, document_id: str, user_id: str) -> bool:
        """Check if user can edit document"""
        document_state = self._get_or_create_document_state(document_id)
        
        # Cannot edit finalized documents
        if document_state.status == DocumentStatus.FINALIZED:
            return False
        
        # Check for blocking locks
        active_locks = self.get_document_locks(document_id)
        for lock in active_locks:
            if lock.lock_type in [LockType.FINALIZATION_LOCK, LockType.ADMIN_LOCK]:
                if lock.locked_by != user_id:
                    return False
            elif lock.lock_type == LockType.EDIT_LOCK:
                if lock.locked_by != user_id:
                    return False
        
        return True
    
    def _has_conflicting_lock(self, document_id: str, lock_type: LockType, user_id: str) -> bool:
        """Check if there are conflicting locks"""
        active_locks = self.get_document_locks(document_id)
        
        for lock in active_locks:
            # Same user can have multiple locks
            if lock.locked_by == user_id:
                continue
            
            # Check for conflicts
            if lock_type == LockType.FINALIZATION_LOCK:
                # Finalization lock conflicts with all other locks
                return True
            elif lock.lock_type == LockType.FINALIZATION_LOCK:
                # Cannot add any lock when finalization lock exists
                return True
            elif lock_type == LockType.EDIT_LOCK and lock.lock_type == LockType.EDIT_LOCK:
                # Only one edit lock at a time
                return True
            elif lock_type == LockType.ADMIN_LOCK or lock.lock_type == LockType.ADMIN_LOCK:
                # Admin locks conflict with everything
                return True
        
        return False
    
    def _send_notification(self, document_id: str, notification_type: NotificationType,
                          title: str, message: str, sender_id: str = None,
                          sender_username: str = None, recipient_id: str = None,
                          metadata: Dict[str, Any] = None):
        """Send notification to users"""
        try:
            # Determine recipients
            recipients = []
            if recipient_id:
                recipients = [recipient_id]
            else:
                # Send to all users who have interacted with the document
                # In a real implementation, this would query the database
                # For now, we'll send to users with active locks or permissions
                document_state = self._get_or_create_document_state(document_id)
                recipients = list(document_state.permissions.keys())
                
                # Add users with active locks
                for lock in self.get_document_locks(document_id):
                    if lock.locked_by not in recipients:
                        recipients.append(lock.locked_by)
            
            # Create and store notifications
            for recipient_id in recipients:
                if recipient_id == sender_id:
                    continue  # Don't notify sender
                
                notification = Notification(
                    notification_id=self._generate_id(),
                    document_id=document_id,
                    notification_type=notification_type,
                    recipient_id=recipient_id,
                    recipient_username="",  # Would be filled from user database
                    sender_id=sender_id,
                    sender_username=sender_username,
                    title=title,
                    message=message,
                    created_at=datetime.now(),
                    read_at=None,
                    metadata=metadata or {}
                )
                
                if recipient_id not in self.notifications:
                    self.notifications[recipient_id] = []
                self.notifications[recipient_id].append(notification)
                
                # Call external notification callbacks
                for callback in self.notification_callbacks:
                    try:
                        callback(notification)
                    except Exception as e:
                        logger.error(f"Notification callback error: {str(e)}")
            
        except Exception as e:
            logger.error(f"Error sending notification: {str(e)}")
    
    def _notify_document_locked(self, document_id: str, lock: DocumentLock):
        """Send document locked notification"""
        self._send_notification(
            document_id=document_id,
            notification_type=NotificationType.DOCUMENT_LOCKED,
            title="Document Locked",
            message=f"Document has been locked by {lock.locked_by_username} ({lock.lock_type.value}). Reason: {lock.reason}",
            sender_id=lock.locked_by,
            sender_username=lock.locked_by_username,
            metadata={'lock_id': lock.lock_id, 'lock_type': lock.lock_type.value}
        )
    
    def _notify_document_unlocked(self, document_id: str, lock: DocumentLock,
                                 unlocked_by: str, unlocked_by_username: str):
        """Send document unlocked notification"""
        self._send_notification(
            document_id=document_id,
            notification_type=NotificationType.DOCUMENT_UNLOCKED,
            title="Document Unlocked",
            message=f"Document has been unlocked by {unlocked_by_username}",
            sender_id=unlocked_by,
            sender_username=unlocked_by_username,
            metadata={'lock_id': lock.lock_id, 'lock_type': lock.lock_type.value}
        )
    
    def _notify_finalization_started(self, document_id: str, user_id: str, username: str):
        """Send finalization started notification"""
        self._send_notification(
            document_id=document_id,
            notification_type=NotificationType.FINALIZATION_STARTED,
            title="Document Finalization Started",
            message=f"Document finalization has been started by {username}",
            sender_id=user_id,
            sender_username=username
        )
    
    def _notify_finalization_completed(self, document_id: str, user_id: str,
                                     username: str, reason: str):
        """Send finalization completed notification"""
        self._send_notification(
            document_id=document_id,
            notification_type=NotificationType.FINALIZATION_COMPLETED,
            title="Document Finalized",
            message=f"Document has been finalized by {username}. Reason: {reason}",
            sender_id=user_id,
            sender_username=username,
            metadata={'finalization_reason': reason}
        )
    
    def get_user_notifications(self, user_id: str, unread_only: bool = False,
                              limit: int = None) -> List[Notification]:
        """Get notifications for a user"""
        if user_id not in self.notifications:
            return []
        
        notifications = self.notifications[user_id]
        
        if unread_only:
            notifications = [n for n in notifications if n.read_at is None]
        
        # Sort by creation time (newest first)
        notifications = sorted(notifications, key=lambda n: n.created_at, reverse=True)
        
        if limit:
            notifications = notifications[:limit]
        
        return notifications
    
    def mark_notification_read(self, user_id: str, notification_id: str) -> bool:
        """Mark a notification as read"""
        if user_id not in self.notifications:
            return False
        
        for notification in self.notifications[user_id]:
            if notification.notification_id == notification_id:
                notification.read_at = datetime.now()
                return True
        
        return False
    
    def cleanup_expired_locks(self):
        """Clean up expired locks"""
        try:
            expired_locks = []
            
            for lock_id, lock in self.locks.items():
                if lock.is_expired():
                    expired_locks.append(lock_id)
            
            for lock_id in expired_locks:
                lock = self.locks[lock_id]
                
                # Send expiration notification
                self._send_notification(
                    document_id=lock.document_id,
                    notification_type=NotificationType.LOCK_EXPIRED,
                    title="Lock Expired",
                    message=f"Lock ({lock.lock_type.value}) has expired",
                    sender_id=lock.locked_by,
                    sender_username=lock.locked_by_username,
                    metadata={'lock_id': lock_id}
                )
                
                # Remove lock
                self.unlock_document(
                    lock.document_id, lock_id, 
                    lock.locked_by, lock.locked_by_username, 
                    force=True
                )
            
            if expired_locks:
                logger.info(f"Cleaned up {len(expired_locks)} expired locks")
                
        except Exception as e:
            logger.error(f"Error cleaning up expired locks: {str(e)}")
    
    def cleanup_old_notifications(self, older_than_days: int = None):
        """Clean up old notifications"""
        try:
            if older_than_days is None:
                older_than_days = self.notification_retention_days
            
            cutoff_date = datetime.now() - timedelta(days=older_than_days)
            
            for user_id in list(self.notifications.keys()):
                self.notifications[user_id] = [
                    n for n in self.notifications[user_id]
                    if n.created_at >= cutoff_date
                ]
                
                if not self.notifications[user_id]:
                    del self.notifications[user_id]
            
            logger.info(f"Cleaned up notifications older than {older_than_days} days")
            
        except Exception as e:
            logger.error(f"Error cleaning up old notifications: {str(e)}")
    
    async def start_background_tasks(self):
        """Start background cleanup tasks"""
        self._running = True
        self._cleanup_task = asyncio.create_task(self._background_cleanup())
    
    async def stop_background_tasks(self):
        """Stop background cleanup tasks"""
        self._running = False
        if self._cleanup_task:
            self._cleanup_task.cancel()
            try:
                await self._cleanup_task
            except asyncio.CancelledError:
                pass
    
    async def _background_cleanup(self):
        """Background task for periodic cleanup"""
        while self._running:
            try:
                self.cleanup_expired_locks()
                self.cleanup_old_notifications()
                await asyncio.sleep(300)  # Run every 5 minutes
            except asyncio.CancelledError:
                break
            except Exception as e:
                logger.error(f"Background cleanup error: {str(e)}")
                await asyncio.sleep(60)  # Wait 1 minute before retrying