"""
Collaborative Web Interface for real-time document editing.
Provides a web-based interface with real-time updates, presence indicators,
and user permissions management.
"""

import asyncio
import json
import logging
import secrets
from datetime import datetime
from typing import Dict, List, Optional, Any, Set
from dataclasses import dataclass, asdict
import websockets
from websockets.server import WebSocketServerProtocol

from .auth_manager import AuthManager
from .collaborative_editor import CollaborativeEditor
from .version_history import VersionHistoryManager
from .document_locking import DocumentLockingManager

logger = logging.getLogger(__name__)


@dataclass
class WebSession:
    """Represents a web session"""
    session_id: str
    user_id: str
    username: str
    connection_id: str
    document_id: Optional[str]
    joined_at: datetime
    last_activity: datetime
    permissions: List[str]
    metadata: Dict[str, Any]
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert session to dictionary"""
        return {
            'session_id': self.session_id,
            'user_id': self.user_id,
            'username': self.username,
            'connection_id': self.connection_id,
            'document_id': self.document_id,
            'joined_at': self.joined_at.isoformat(),
            'last_activity': self.last_activity.isoformat(),
            'permissions': self.permissions,
            'metadata': self.metadata
        }


@dataclass
class UserPresenceInfo:
    """Enhanced user presence information for web interface"""
    user_id: str
    username: str
    session_id: str
    cursor_position: int
    selection_start: int
    selection_end: int
    is_typing: bool
    last_seen: datetime
    user_color: str  # Color for user identification
    avatar_url: Optional[str]
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert presence info to dictionary"""
        return {
            'user_id': self.user_id,
            'username': self.username,
            'session_id': self.session_id,
            'cursor_position': self.cursor_position,
            'selection_start': self.selection_start,
            'selection_end': self.selection_end,
            'is_typing': self.is_typing,
            'last_seen': self.last_seen.isoformat(),
            'user_color': self.user_color,
            'avatar_url': self.avatar_url
        }


class CollaborativeWebInterface:
    """
    Web interface for collaborative document editing.
    Integrates with CollaborativeEditor, VersionHistoryManager, and DocumentLockingManager
    to provide a complete collaborative editing experience.
    """
    
    def __init__(self, auth_manager: AuthManager, 
                 collaborative_editor: CollaborativeEditor,
                 version_manager: VersionHistoryManager,
                 locking_manager: DocumentLockingManager,
                 config: Dict[str, Any] = None):
        self.auth_manager = auth_manager
        self.collaborative_editor = collaborative_editor
        self.version_manager = version_manager
        self.locking_manager = locking_manager
        self.config = config or {}
        
        # Configuration
        self.host = self.config.get('host', 'localhost')
        self.port = self.config.get('port', 8080)
        self.max_sessions = self.config.get('max_sessions', 100)
        
        # Session management
        self.sessions: Dict[str, WebSession] = {}  # session_id -> session
        self.connection_sessions: Dict[str, str] = {}  # connection_id -> session_id
        self.document_sessions: Dict[str, Set[str]] = {}  # document_id -> set of session_ids
        
        # User presence and colors
        self.user_colors = [
            '#FF6B6B', '#4ECDC4', '#45B7D1', '#96CEB4', '#FFEAA7',
            '#DDA0DD', '#98D8C8', '#F7DC6F', '#BB8FCE', '#85C1E9'
        ]
        self.assigned_colors: Dict[str, str] = {}  # user_id -> color
        
        # WebSocket server
        self.server = None
        self.is_running = False
        
        # Setup notification callback for document locking
        self.locking_manager.add_notification_callback(self._handle_locking_notification)
        
        logger.info("CollaborativeWebInterface initialized")
    
    def _generate_session_id(self) -> str:
        """Generate unique session ID"""
        return secrets.token_hex(16)
    
    def _assign_user_color(self, user_id: str) -> str:
        """Assign a color to a user"""
        if user_id not in self.assigned_colors:
            # Find an unused color or cycle through colors
            used_colors = set(self.assigned_colors.values())
            available_colors = [c for c in self.user_colors if c not in used_colors]
            
            if available_colors:
                color = available_colors[0]
            else:
                # All colors used, cycle through
                color = self.user_colors[len(self.assigned_colors) % len(self.user_colors)]
            
            self.assigned_colors[user_id] = color
        
        return self.assigned_colors[user_id]
    
    async def start_server(self):
        """Start the web interface server"""
        try:
            self.server = await websockets.serve(
                self.handle_connection,
                self.host,
                self.port,
                max_size=1024*1024,  # 1MB max message size
                max_queue=32
            )
            self.is_running = True
            logger.info(f"CollaborativeWebInterface server started on {self.host}:{self.port}")
            
        except Exception as e:
            logger.error(f"Failed to start CollaborativeWebInterface server: {str(e)}")
            raise
    
    async def stop_server(self):
        """Stop the web interface server"""
        if self.server:
            self.server.close()
            await self.server.wait_closed()
            self.is_running = False
            logger.info("CollaborativeWebInterface server stopped")
    
    async def handle_connection(self, websocket: WebSocketServerProtocol, path: str):
        """Handle new WebSocket connection"""
        connection_id = secrets.token_hex(16)
        
        try:
            logger.info(f"New web interface connection: {connection_id}")
            
            async for message in websocket:
                try:
                    data = json.loads(message)
                    await self.handle_message(connection_id, websocket, data)
                except json.JSONDecodeError:
                    await self.send_error(websocket, "Invalid JSON format")
                except Exception as e:
                    logger.error(f"Error handling message: {str(e)}")
                    await self.send_error(websocket, "Internal server error")
        
        except websockets.exceptions.ConnectionClosed:
            logger.info(f"Web interface connection closed: {connection_id}")
        except Exception as e:
            logger.error(f"Web interface connection error: {str(e)}")
        finally:
            await self.cleanup_connection(connection_id)
    
    async def handle_message(self, connection_id: str, websocket: WebSocketServerProtocol, 
                           data: Dict[str, Any]):
        """Handle incoming WebSocket message"""
        message_type = data.get('type')
        
        if message_type == 'authenticate':
            await self.handle_authentication(connection_id, websocket, data)
        elif message_type == 'join_document':
            await self.handle_join_document(connection_id, websocket, data)
        elif message_type == 'leave_document':
            await self.handle_leave_document(connection_id, websocket, data)
        elif message_type == 'get_document_info':
            await self.handle_get_document_info(connection_id, websocket, data)
        elif message_type == 'get_version_history':
            await self.handle_get_version_history(connection_id, websocket, data)
        elif message_type == 'compare_versions':
            await self.handle_compare_versions(connection_id, websocket, data)
        elif message_type == 'lock_document':
            await self.handle_lock_document(connection_id, websocket, data)
        elif message_type == 'unlock_document':
            await self.handle_unlock_document(connection_id, websocket, data)
        elif message_type == 'finalize_document':
            await self.handle_finalize_document(connection_id, websocket, data)
        elif message_type == 'get_notifications':
            await self.handle_get_notifications(connection_id, websocket, data)
        elif message_type == 'mark_notification_read':
            await self.handle_mark_notification_read(connection_id, websocket, data)
        elif message_type == 'update_presence':
            await self.handle_update_presence(connection_id, websocket, data)
        elif message_type == 'ping':
            await self.send_message(websocket, {'type': 'pong'})
        else:
            await self.send_error(websocket, f"Unknown message type: {message_type}")
    
    async def handle_authentication(self, connection_id: str, websocket: WebSocketServerProtocol,
                                  data: Dict[str, Any]):
        """Handle user authentication"""
        token = data.get('token')
        if not token:
            await self.send_error(websocket, "Authentication token required")
            return
        
        # Validate token
        validation_result = self.auth_manager.validate_token(token)
        if not validation_result['valid']:
            await self.send_error(websocket, "Invalid authentication token")
            return
        
        user_id = validation_result['user']['user_id']
        username = validation_result['user']['username']
        role = validation_result['user']['role']
        
        # Create session
        session_id = self._generate_session_id()
        session = WebSession(
            session_id=session_id,
            user_id=user_id,
            username=username,
            connection_id=connection_id,
            document_id=None,
            joined_at=datetime.now(),
            last_activity=datetime.now(),
            permissions=self._get_user_permissions(role),
            metadata={}
        )
        
        self.sessions[session_id] = session
        self.connection_sessions[connection_id] = session_id
        
        # Assign user color
        user_color = self._assign_user_color(user_id)
        
        # Send authentication success
        await self.send_message(websocket, {
            'type': 'authenticated',
            'session_id': session_id,
            'user': validation_result['user'],
            'user_color': user_color,
            'permissions': session.permissions
        })
        
        logger.info(f"Web interface user authenticated: {username} ({user_id})")
    
    async def handle_join_document(self, connection_id: str, websocket: WebSocketServerProtocol,
                                 data: Dict[str, Any]):
        """Handle user joining a document"""
        session = self._get_session_by_connection(connection_id)
        if not session:
            await self.send_error(websocket, "Authentication required")
            return
        
        document_id = data.get('document_id')
        if not document_id:
            await self.send_error(websocket, "Document ID required")
            return
        
        # Check if user can access document
        if not self._can_user_access_document(session.user_id, document_id):
            await self.send_error(websocket, "Access denied")
            return
        
        # Update session
        session.document_id = document_id
        session.last_activity = datetime.now()
        
        # Add to document sessions
        if document_id not in self.document_sessions:
            self.document_sessions[document_id] = set()
        self.document_sessions[document_id].add(session.session_id)
        
        # Get document information
        document_state = self.locking_manager.get_document_state(document_id)
        document_locks = self.locking_manager.get_document_locks(document_id)
        can_edit = self.locking_manager.can_user_edit(document_id, session.user_id)
        
        # Get collaborative editor document state
        collab_doc_state = self.collaborative_editor.get_document_state(document_id)
        
        # Get presence information
        presence_info = self._get_document_presence(document_id)
        
        # Send document state to user
        await self.send_message(websocket, {
            'type': 'document_joined',
            'document_id': document_id,
            'document_state': document_state.to_dict() if document_state else None,
            'collaborative_state': collab_doc_state.to_dict() if collab_doc_state else None,
            'locks': [lock.to_dict() for lock in document_locks],
            'can_edit': can_edit,
            'presence': presence_info,
            'user_color': self.assigned_colors.get(session.user_id, '#000000')
        })
        
        # Notify other users
        await self.broadcast_to_document(document_id, {
            'type': 'user_joined_document',
            'user': {
                'user_id': session.user_id,
                'username': session.username,
                'session_id': session.session_id,
                'user_color': self.assigned_colors.get(session.user_id, '#000000')
            },
            'presence': presence_info
        }, exclude_session=session.session_id)
        
        logger.info(f"User {session.username} joined document {document_id}")
    
    async def handle_leave_document(self, connection_id: str, websocket: WebSocketServerProtocol,
                                  data: Dict[str, Any]):
        """Handle user leaving a document"""
        session = self._get_session_by_connection(connection_id)
        if not session or not session.document_id:
            return
        
        document_id = session.document_id
        
        # Remove from document sessions
        if document_id in self.document_sessions:
            self.document_sessions[document_id].discard(session.session_id)
            if not self.document_sessions[document_id]:
                del self.document_sessions[document_id]
        
        # Update session
        session.document_id = None
        session.last_activity = datetime.now()
        
        # Notify other users
        await self.broadcast_to_document(document_id, {
            'type': 'user_left_document',
            'user': {
                'user_id': session.user_id,
                'username': session.username,
                'session_id': session.session_id
            },
            'presence': self._get_document_presence(document_id)
        }, exclude_session=session.session_id)
        
        logger.info(f"User {session.username} left document {document_id}")
    
    async def handle_get_document_info(self, connection_id: str, websocket: WebSocketServerProtocol,
                                     data: Dict[str, Any]):
        """Handle request for document information"""
        session = self._get_session_by_connection(connection_id)
        if not session:
            await self.send_error(websocket, "Authentication required")
            return
        
        document_id = data.get('document_id')
        if not document_id:
            await self.send_error(websocket, "Document ID required")
            return
        
        # Get document information
        document_state = self.locking_manager.get_document_state(document_id)
        document_locks = self.locking_manager.get_document_locks(document_id)
        version_stats = self.version_manager.get_document_statistics(document_id)
        
        await self.send_message(websocket, {
            'type': 'document_info',
            'document_id': document_id,
            'document_state': document_state.to_dict() if document_state else None,
            'locks': [lock.to_dict() for lock in document_locks],
            'version_statistics': version_stats,
            'can_edit': self.locking_manager.can_user_edit(document_id, session.user_id)
        })
    
    async def handle_get_version_history(self, connection_id: str, websocket: WebSocketServerProtocol,
                                       data: Dict[str, Any]):
        """Handle request for version history"""
        session = self._get_session_by_connection(connection_id)
        if not session:
            await self.send_error(websocket, "Authentication required")
            return
        
        document_id = data.get('document_id')
        limit = data.get('limit', 20)
        
        if not document_id:
            await self.send_error(websocket, "Document ID required")
            return
        
        # Get version history
        versions = self.version_manager.get_version_history(document_id, limit)
        
        await self.send_message(websocket, {
            'type': 'version_history',
            'document_id': document_id,
            'versions': [version.to_dict() for version in versions]
        })
    
    async def handle_compare_versions(self, connection_id: str, websocket: WebSocketServerProtocol,
                                    data: Dict[str, Any]):
        """Handle request to compare versions"""
        session = self._get_session_by_connection(connection_id)
        if not session:
            await self.send_error(websocket, "Authentication required")
            return
        
        document_id = data.get('document_id')
        version1_id = data.get('version1_id')
        version2_id = data.get('version2_id')
        
        if not all([document_id, version1_id, version2_id]):
            await self.send_error(websocket, "Document ID and version IDs required")
            return
        
        # Compare versions
        comparison = self.version_manager.compare_versions(document_id, version1_id, version2_id)
        
        await self.send_message(websocket, {
            'type': 'version_comparison',
            'document_id': document_id,
            'comparison': comparison
        })
    
    async def handle_lock_document(self, connection_id: str, websocket: WebSocketServerProtocol,
                                 data: Dict[str, Any]):
        """Handle document lock request"""
        session = self._get_session_by_connection(connection_id)
        if not session:
            await self.send_error(websocket, "Authentication required")
            return
        
        document_id = data.get('document_id')
        lock_type = data.get('lock_type', 'edit_lock')
        duration_minutes = data.get('duration_minutes')
        reason = data.get('reason', '')
        
        if not document_id:
            await self.send_error(websocket, "Document ID required")
            return
        
        # Lock document
        from .document_locking import LockType
        lock_type_enum = LockType(lock_type)
        
        result = self.locking_manager.lock_document(
            document_id=document_id,
            user_id=session.user_id,
            username=session.username,
            lock_type=lock_type_enum,
            duration_minutes=duration_minutes,
            reason=reason
        )
        
        await self.send_message(websocket, {
            'type': 'lock_result',
            'document_id': document_id,
            'result': result
        })
        
        # Broadcast lock status to other users
        if result['success']:
            await self.broadcast_to_document(document_id, {
                'type': 'document_lock_changed',
                'document_id': document_id,
                'locks': [lock.to_dict() for lock in self.locking_manager.get_document_locks(document_id)]
            }, exclude_session=session.session_id)
    
    async def handle_unlock_document(self, connection_id: str, websocket: WebSocketServerProtocol,
                                   data: Dict[str, Any]):
        """Handle document unlock request"""
        session = self._get_session_by_connection(connection_id)
        if not session:
            await self.send_error(websocket, "Authentication required")
            return
        
        document_id = data.get('document_id')
        lock_id = data.get('lock_id')
        force = data.get('force', False)
        
        if not all([document_id, lock_id]):
            await self.send_error(websocket, "Document ID and lock ID required")
            return
        
        # Unlock document
        result = self.locking_manager.unlock_document(
            document_id=document_id,
            lock_id=lock_id,
            user_id=session.user_id,
            username=session.username,
            force=force
        )
        
        await self.send_message(websocket, {
            'type': 'unlock_result',
            'document_id': document_id,
            'result': result
        })
        
        # Broadcast lock status to other users
        if result['success']:
            await self.broadcast_to_document(document_id, {
                'type': 'document_lock_changed',
                'document_id': document_id,
                'locks': [lock.to_dict() for lock in self.locking_manager.get_document_locks(document_id)]
            }, exclude_session=session.session_id)
    
    async def handle_finalize_document(self, connection_id: str, websocket: WebSocketServerProtocol,
                                     data: Dict[str, Any]):
        """Handle document finalization request"""
        session = self._get_session_by_connection(connection_id)
        if not session:
            await self.send_error(websocket, "Authentication required")
            return
        
        document_id = data.get('document_id')
        reason = data.get('reason', '')
        
        if not document_id:
            await self.send_error(websocket, "Document ID required")
            return
        
        # Finalize document
        result = self.locking_manager.finalize_document(
            document_id=document_id,
            user_id=session.user_id,
            username=session.username,
            reason=reason
        )
        
        await self.send_message(websocket, {
            'type': 'finalize_result',
            'document_id': document_id,
            'result': result
        })
        
        # Broadcast finalization to other users
        if result['success']:
            await self.broadcast_to_document(document_id, {
                'type': 'document_finalized',
                'document_id': document_id,
                'finalized_by': session.username,
                'reason': reason
            }, exclude_session=session.session_id)
    
    async def handle_get_notifications(self, connection_id: str, websocket: WebSocketServerProtocol,
                                     data: Dict[str, Any]):
        """Handle request for user notifications"""
        session = self._get_session_by_connection(connection_id)
        if not session:
            await self.send_error(websocket, "Authentication required")
            return
        
        unread_only = data.get('unread_only', False)
        limit = data.get('limit', 50)
        
        # Get notifications
        notifications = self.locking_manager.get_user_notifications(
            session.user_id, unread_only, limit
        )
        
        await self.send_message(websocket, {
            'type': 'notifications',
            'notifications': [notif.to_dict() for notif in notifications]
        })
    
    async def handle_mark_notification_read(self, connection_id: str, websocket: WebSocketServerProtocol,
                                          data: Dict[str, Any]):
        """Handle marking notification as read"""
        session = self._get_session_by_connection(connection_id)
        if not session:
            await self.send_error(websocket, "Authentication required")
            return
        
        notification_id = data.get('notification_id')
        if not notification_id:
            await self.send_error(websocket, "Notification ID required")
            return
        
        # Mark notification as read
        success = self.locking_manager.mark_notification_read(session.user_id, notification_id)
        
        await self.send_message(websocket, {
            'type': 'notification_marked_read',
            'notification_id': notification_id,
            'success': success
        })
    
    async def handle_update_presence(self, connection_id: str, websocket: WebSocketServerProtocol,
                                   data: Dict[str, Any]):
        """Handle presence update"""
        session = self._get_session_by_connection(connection_id)
        if not session or not session.document_id:
            return
        
        cursor_position = data.get('cursor_position', 0)
        selection_start = data.get('selection_start', 0)
        selection_end = data.get('selection_end', 0)
        is_typing = data.get('is_typing', False)
        
        # Update session activity
        session.last_activity = datetime.now()
        
        # Broadcast presence update
        await self.broadcast_to_document(session.document_id, {
            'type': 'presence_update',
            'user': {
                'user_id': session.user_id,
                'username': session.username,
                'session_id': session.session_id,
                'cursor_position': cursor_position,
                'selection_start': selection_start,
                'selection_end': selection_end,
                'is_typing': is_typing,
                'last_seen': session.last_activity.isoformat(),
                'user_color': self.assigned_colors.get(session.user_id, '#000000')
            }
        }, exclude_session=session.session_id)
    
    def _get_session_by_connection(self, connection_id: str) -> Optional[WebSession]:
        """Get session by connection ID"""
        session_id = self.connection_sessions.get(connection_id)
        if session_id:
            return self.sessions.get(session_id)
        return None
    
    def _get_user_permissions(self, role: str) -> List[str]:
        """Get user permissions based on role"""
        permissions = ['read']
        
        if role in ['user', 'editor', 'admin']:
            permissions.append('write')
        
        if role in ['editor', 'admin']:
            permissions.extend(['lock', 'version_history'])
        
        if role == 'admin':
            permissions.extend(['finalize', 'force_unlock', 'user_management'])
        
        return permissions
    
    def _can_user_access_document(self, user_id: str, document_id: str) -> bool:
        """Check if user can access document"""
        # In a real implementation, this would check document permissions
        # For now, allow all authenticated users
        return True
    
    def _get_document_presence(self, document_id: str) -> List[Dict[str, Any]]:
        """Get presence information for all users in document"""
        presence_info = []
        
        if document_id in self.document_sessions:
            for session_id in self.document_sessions[document_id]:
                session = self.sessions.get(session_id)
                if session:
                    presence_info.append({
                        'user_id': session.user_id,
                        'username': session.username,
                        'session_id': session.session_id,
                        'last_activity': session.last_activity.isoformat(),
                        'user_color': self.assigned_colors.get(session.user_id, '#000000')
                    })
        
        return presence_info
    
    async def send_message(self, websocket: WebSocketServerProtocol, message: Dict[str, Any]):
        """Send message to websocket"""
        try:
            await websocket.send(json.dumps(message))
        except Exception as e:
            logger.error(f"Error sending message: {str(e)}")
    
    async def send_error(self, websocket: WebSocketServerProtocol, error_message: str):
        """Send error message to websocket"""
        await self.send_message(websocket, {
            'type': 'error',
            'message': error_message
        })
    
    async def broadcast_to_document(self, document_id: str, message: Dict[str, Any],
                                  exclude_session: str = None):
        """Broadcast message to all users in a document"""
        if document_id not in self.document_sessions:
            return
        
        tasks = []
        for session_id in self.document_sessions[document_id]:
            if session_id != exclude_session:
                session = self.sessions.get(session_id)
                if session:
                    # Find websocket for this session (would need to be stored)
                    # For now, we'll skip the actual websocket sending
                    pass
        
        if tasks:
            await asyncio.gather(*tasks, return_exceptions=True)
    
    async def cleanup_connection(self, connection_id: str):
        """Clean up connection and associated resources"""
        session_id = self.connection_sessions.get(connection_id)
        if session_id:
            session = self.sessions.get(session_id)
            if session:
                # Remove from document sessions
                if session.document_id and session.document_id in self.document_sessions:
                    self.document_sessions[session.document_id].discard(session_id)
                    if not self.document_sessions[session.document_id]:
                        del self.document_sessions[session.document_id]
                
                # Remove session
                del self.sessions[session_id]
            
            del self.connection_sessions[connection_id]
        
        logger.info(f"Web interface connection cleaned up: {connection_id}")
    
    async def _handle_locking_notification(self, notification):
        """Handle notification from document locking manager"""
        try:
            # Broadcast notification to relevant users
            if notification.document_id:
                await self.broadcast_to_document(notification.document_id, {
                    'type': 'notification',
                    'notification': notification.to_dict()
                })
        except Exception as e:
            logger.error(f"Error handling locking notification: {str(e)}")
    
    def get_active_sessions(self) -> List[Dict[str, Any]]:
        """Get all active sessions"""
        return [session.to_dict() for session in self.sessions.values()]
    
    def get_document_sessions(self, document_id: str) -> List[Dict[str, Any]]:
        """Get sessions for a specific document"""
        sessions = []
        if document_id in self.document_sessions:
            for session_id in self.document_sessions[document_id]:
                session = self.sessions.get(session_id)
                if session:
                    sessions.append(session.to_dict())
        return sessions
    
    async def run_server(self):
        """Run the server (blocking call)"""
        await self.start_server()
        try:
            # Keep server running
            await asyncio.Future()  # Run forever
        except KeyboardInterrupt:
            logger.info("Web interface server interrupted")
        finally:
            await self.stop_server()