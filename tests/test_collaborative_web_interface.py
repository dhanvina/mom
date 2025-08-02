"""
Unit tests for Collaborative Web Interface
"""

import pytest
import asyncio
import json
from datetime import datetime, timedelta
from unittest.mock import Mock, AsyncMock, patch

from app.auth.auth_manager import AuthManager
from app.auth.collaborative_editor import CollaborativeEditor
from app.auth.version_history import VersionHistoryManager
from app.auth.document_locking import DocumentLockingManager
from app.auth.collaborative_web_interface import (
    CollaborativeWebInterface, WebSession, UserPresenceInfo
)


class TestWebSession:
    """Test cases for WebSession"""
    
    def test_session_creation(self):
        """Test web session creation"""
        now = datetime.now()
        
        session = WebSession(
            session_id="session123",
            user_id="user1",
            username="testuser",
            connection_id="conn123",
            document_id="doc1",
            joined_at=now,
            last_activity=now,
            permissions=["read", "write"],
            metadata={"test": "data"}
        )
        
        assert session.session_id == "session123"
        assert session.user_id == "user1"
        assert session.username == "testuser"
        assert session.document_id == "doc1"
        assert session.permissions == ["read", "write"]
    
    def test_session_to_dict(self):
        """Test session to dictionary conversion"""
        now = datetime.now()
        
        session = WebSession(
            session_id="session123",
            user_id="user1",
            username="testuser",
            connection_id="conn123",
            document_id="doc1",
            joined_at=now,
            last_activity=now,
            permissions=["read", "write"],
            metadata={"test": "data"}
        )
        
        session_dict = session.to_dict()
        
        assert session_dict['session_id'] == "session123"
        assert session_dict['user_id'] == "user1"
        assert session_dict['username'] == "testuser"
        assert session_dict['document_id'] == "doc1"
        assert session_dict['permissions'] == ["read", "write"]
        assert session_dict['metadata']['test'] == "data"


class TestUserPresenceInfo:
    """Test cases for UserPresenceInfo"""
    
    def test_presence_creation(self):
        """Test user presence info creation"""
        now = datetime.now()
        
        presence = UserPresenceInfo(
            user_id="user1",
            username="testuser",
            session_id="session123",
            cursor_position=10,
            selection_start=5,
            selection_end=15,
            is_typing=True,
            last_seen=now,
            user_color="#FF6B6B",
            avatar_url="https://example.com/avatar.jpg"
        )
        
        assert presence.user_id == "user1"
        assert presence.username == "testuser"
        assert presence.cursor_position == 10
        assert presence.is_typing is True
        assert presence.user_color == "#FF6B6B"
    
    def test_presence_to_dict(self):
        """Test presence info to dictionary conversion"""
        now = datetime.now()
        
        presence = UserPresenceInfo(
            user_id="user1",
            username="testuser",
            session_id="session123",
            cursor_position=10,
            selection_start=5,
            selection_end=15,
            is_typing=True,
            last_seen=now,
            user_color="#FF6B6B",
            avatar_url="https://example.com/avatar.jpg"
        )
        
        presence_dict = presence.to_dict()
        
        assert presence_dict['user_id'] == "user1"
        assert presence_dict['username'] == "testuser"
        assert presence_dict['cursor_position'] == 10
        assert presence_dict['is_typing'] is True
        assert presence_dict['user_color'] == "#FF6B6B"
        assert presence_dict['avatar_url'] == "https://example.com/avatar.jpg"


class TestCollaborativeWebInterface:
    """Test cases for CollaborativeWebInterface"""
    
    @pytest.fixture
    def auth_manager(self):
        """Create a test auth manager"""
        auth_manager = AuthManager()
        # Register test users
        auth_manager.register_user("testuser1", "test1@example.com", "password123", "user")
        auth_manager.register_user("testuser2", "test2@example.com", "password123", "editor")
        auth_manager.register_user("admin", "admin@example.com", "adminpass", "admin")
        return auth_manager
    
    @pytest.fixture
    def collaborative_editor(self, auth_manager):
        """Create a test collaborative editor"""
        return CollaborativeEditor(auth_manager)
    
    @pytest.fixture
    def version_manager(self):
        """Create a test version history manager"""
        return VersionHistoryManager()
    
    @pytest.fixture
    def locking_manager(self):
        """Create a test document locking manager"""
        return DocumentLockingManager()
    
    @pytest.fixture
    def web_interface(self, auth_manager, collaborative_editor, version_manager, locking_manager):
        """Create a test collaborative web interface"""
        config = {
            'host': 'localhost',
            'port': 8081,  # Different port for testing
            'max_sessions': 10
        }
        return CollaborativeWebInterface(
            auth_manager, collaborative_editor, version_manager, locking_manager, config
        )
    
    def test_interface_initialization(self, web_interface):
        """Test web interface initialization"""
        assert web_interface.host == 'localhost'
        assert web_interface.port == 8081
        assert web_interface.max_sessions == 10
        assert len(web_interface.sessions) == 0
        assert len(web_interface.document_sessions) == 0
        assert len(web_interface.user_colors) > 0
    
    def test_assign_user_color(self, web_interface):
        """Test user color assignment"""
        # First user gets first color
        color1 = web_interface._assign_user_color("user1")
        assert color1 in web_interface.user_colors
        assert web_interface.assigned_colors["user1"] == color1
        
        # Second user gets different color
        color2 = web_interface._assign_user_color("user2")
        assert color2 in web_interface.user_colors
        assert color2 != color1
        
        # Same user gets same color
        color1_again = web_interface._assign_user_color("user1")
        assert color1_again == color1
    
    def test_get_user_permissions_user(self, web_interface):
        """Test getting permissions for regular user"""
        permissions = web_interface._get_user_permissions("user")
        
        assert "read" in permissions
        assert "write" in permissions
        assert "lock" not in permissions
        assert "finalize" not in permissions
    
    def test_get_user_permissions_editor(self, web_interface):
        """Test getting permissions for editor"""
        permissions = web_interface._get_user_permissions("editor")
        
        assert "read" in permissions
        assert "write" in permissions
        assert "lock" in permissions
        assert "version_history" in permissions
        assert "finalize" not in permissions
    
    def test_get_user_permissions_admin(self, web_interface):
        """Test getting permissions for admin"""
        permissions = web_interface._get_user_permissions("admin")
        
        assert "read" in permissions
        assert "write" in permissions
        assert "lock" in permissions
        assert "version_history" in permissions
        assert "finalize" in permissions
        assert "force_unlock" in permissions
        assert "user_management" in permissions
    
    def test_can_user_access_document(self, web_interface):
        """Test user document access check"""
        # For now, all authenticated users can access documents
        assert web_interface._can_user_access_document("user1", "doc1") is True
        assert web_interface._can_user_access_document("user2", "doc2") is True
    
    @pytest.mark.asyncio
    async def test_handle_authentication_success(self, web_interface, auth_manager):
        """Test successful authentication handling"""
        # Authenticate user to get token
        auth_result = auth_manager.authenticate_user("testuser1", "password123")
        token = auth_result['access_token']
        
        # Mock websocket
        mock_websocket = AsyncMock()
        connection_id = "conn123"
        
        # Handle authentication
        await web_interface.handle_authentication(connection_id, mock_websocket, {
            'token': token
        })
        
        # Verify session was created
        session_id = web_interface.connection_sessions.get(connection_id)
        assert session_id is not None
        
        session = web_interface.sessions.get(session_id)
        assert session is not None
        assert session.user_id == auth_result['user']['user_id']
        assert session.username == "testuser1"
        
        # Verify response was sent
        mock_websocket.send.assert_called_once()
        sent_message = mock_websocket.send.call_args[0][0]
        response = json.loads(sent_message)  # Convert JSON string back to dict
        assert response['type'] == 'authenticated'
        assert 'session_id' in response
        assert 'user_color' in response
    
    @pytest.mark.asyncio
    async def test_handle_authentication_invalid_token(self, web_interface):
        """Test authentication with invalid token"""
        mock_websocket = AsyncMock()
        connection_id = "conn123"
        
        await web_interface.handle_authentication(connection_id, mock_websocket, {
            'token': 'invalid_token'
        })
        
        # Verify error was sent
        mock_websocket.send.assert_called_once()
        sent_message = mock_websocket.send.call_args[0][0]
        response = json.loads(sent_message)
        assert response['type'] == 'error'
        assert "Invalid authentication token" in response['message']
    
    @pytest.mark.asyncio
    async def test_handle_authentication_missing_token(self, web_interface):
        """Test authentication with missing token"""
        mock_websocket = AsyncMock()
        connection_id = "conn123"
        
        await web_interface.handle_authentication(connection_id, mock_websocket, {})
        
        # Verify error was sent
        mock_websocket.send.assert_called_once()
        sent_message = mock_websocket.send.call_args[0][0]
        response = json.loads(sent_message)
        assert response['type'] == 'error'
        assert "Authentication token required" in response['message']
    
    def test_get_session_by_connection(self, web_interface):
        """Test getting session by connection ID"""
        # Create a session
        now = datetime.now()
        session = WebSession(
            session_id="session123",
            user_id="user1",
            username="testuser",
            connection_id="conn123",
            document_id=None,
            joined_at=now,
            last_activity=now,
            permissions=["read", "write"],
            metadata={}
        )
        
        web_interface.sessions["session123"] = session
        web_interface.connection_sessions["conn123"] = "session123"
        
        # Test retrieval
        retrieved_session = web_interface._get_session_by_connection("conn123")
        assert retrieved_session is not None
        assert retrieved_session.session_id == "session123"
        assert retrieved_session.user_id == "user1"
        
        # Test non-existent connection
        non_existent = web_interface._get_session_by_connection("nonexistent")
        assert non_existent is None
    
    def test_get_document_presence_empty(self, web_interface):
        """Test getting presence for document with no users"""
        presence = web_interface._get_document_presence("doc1")
        assert len(presence) == 0
    
    def test_get_document_presence_with_users(self, web_interface):
        """Test getting presence for document with users"""
        now = datetime.now()
        
        # Create sessions
        session1 = WebSession(
            session_id="session1",
            user_id="user1",
            username="testuser1",
            connection_id="conn1",
            document_id="doc1",
            joined_at=now,
            last_activity=now,
            permissions=["read", "write"],
            metadata={}
        )
        
        session2 = WebSession(
            session_id="session2",
            user_id="user2",
            username="testuser2",
            connection_id="conn2",
            document_id="doc1",
            joined_at=now,
            last_activity=now,
            permissions=["read", "write"],
            metadata={}
        )
        
        web_interface.sessions["session1"] = session1
        web_interface.sessions["session2"] = session2
        web_interface.document_sessions["doc1"] = {"session1", "session2"}
        web_interface.assigned_colors["user1"] = "#FF6B6B"
        web_interface.assigned_colors["user2"] = "#4ECDC4"
        
        # Get presence
        presence = web_interface._get_document_presence("doc1")
        
        assert len(presence) == 2
        assert any(p['user_id'] == 'user1' for p in presence)
        assert any(p['user_id'] == 'user2' for p in presence)
        assert any(p['username'] == 'testuser1' for p in presence)
        assert any(p['username'] == 'testuser2' for p in presence)
    
    @pytest.mark.asyncio
    async def test_send_message(self, web_interface):
        """Test sending message to websocket"""
        mock_websocket = AsyncMock()
        
        message = {'type': 'test', 'data': 'hello'}
        await web_interface.send_message(mock_websocket, message)
        
        mock_websocket.send.assert_called_once_with('{"type": "test", "data": "hello"}')
    
    @pytest.mark.asyncio
    async def test_send_error(self, web_interface):
        """Test sending error message"""
        mock_websocket = AsyncMock()
        
        await web_interface.send_error(mock_websocket, "Test error")
        
        mock_websocket.send.assert_called_once()
        sent_message = mock_websocket.send.call_args[0][0]
        response = json.loads(sent_message)
        assert response['type'] == 'error'
        assert response['message'] == 'Test error'
    
    @pytest.mark.asyncio
    async def test_cleanup_connection(self, web_interface):
        """Test connection cleanup"""
        now = datetime.now()
        
        # Create session
        session = WebSession(
            session_id="session123",
            user_id="user1",
            username="testuser",
            connection_id="conn123",
            document_id="doc1",
            joined_at=now,
            last_activity=now,
            permissions=["read", "write"],
            metadata={}
        )
        
        web_interface.sessions["session123"] = session
        web_interface.connection_sessions["conn123"] = "session123"
        web_interface.document_sessions["doc1"] = {"session123"}
        
        # Cleanup connection
        await web_interface.cleanup_connection("conn123")
        
        # Verify cleanup
        assert "conn123" not in web_interface.connection_sessions
        assert "session123" not in web_interface.sessions
        assert "doc1" not in web_interface.document_sessions
    
    def test_get_active_sessions(self, web_interface):
        """Test getting active sessions"""
        now = datetime.now()
        
        # Create sessions
        session1 = WebSession(
            session_id="session1",
            user_id="user1",
            username="testuser1",
            connection_id="conn1",
            document_id="doc1",
            joined_at=now,
            last_activity=now,
            permissions=["read", "write"],
            metadata={}
        )
        
        session2 = WebSession(
            session_id="session2",
            user_id="user2",
            username="testuser2",
            connection_id="conn2",
            document_id="doc2",
            joined_at=now,
            last_activity=now,
            permissions=["read", "write"],
            metadata={}
        )
        
        web_interface.sessions["session1"] = session1
        web_interface.sessions["session2"] = session2
        
        # Get active sessions
        active_sessions = web_interface.get_active_sessions()
        
        assert len(active_sessions) == 2
        assert any(s['session_id'] == 'session1' for s in active_sessions)
        assert any(s['session_id'] == 'session2' for s in active_sessions)
    
    def test_get_document_sessions(self, web_interface):
        """Test getting sessions for a specific document"""
        now = datetime.now()
        
        # Create sessions
        session1 = WebSession(
            session_id="session1",
            user_id="user1",
            username="testuser1",
            connection_id="conn1",
            document_id="doc1",
            joined_at=now,
            last_activity=now,
            permissions=["read", "write"],
            metadata={}
        )
        
        session2 = WebSession(
            session_id="session2",
            user_id="user2",
            username="testuser2",
            connection_id="conn2",
            document_id="doc1",
            joined_at=now,
            last_activity=now,
            permissions=["read", "write"],
            metadata={}
        )
        
        session3 = WebSession(
            session_id="session3",
            user_id="user3",
            username="testuser3",
            connection_id="conn3",
            document_id="doc2",
            joined_at=now,
            last_activity=now,
            permissions=["read", "write"],
            metadata={}
        )
        
        web_interface.sessions["session1"] = session1
        web_interface.sessions["session2"] = session2
        web_interface.sessions["session3"] = session3
        web_interface.document_sessions["doc1"] = {"session1", "session2"}
        web_interface.document_sessions["doc2"] = {"session3"}
        
        # Get sessions for doc1
        doc1_sessions = web_interface.get_document_sessions("doc1")
        
        assert len(doc1_sessions) == 2
        assert any(s['session_id'] == 'session1' for s in doc1_sessions)
        assert any(s['session_id'] == 'session2' for s in doc1_sessions)
        
        # Get sessions for doc2
        doc2_sessions = web_interface.get_document_sessions("doc2")
        
        assert len(doc2_sessions) == 1
        assert doc2_sessions[0]['session_id'] == 'session3'
        
        # Get sessions for non-existent document
        empty_sessions = web_interface.get_document_sessions("nonexistent")
        assert len(empty_sessions) == 0
    
    @pytest.mark.asyncio
    async def test_handle_locking_notification(self, web_interface, locking_manager):
        """Test handling locking notification"""
        # Create a mock notification
        from app.auth.document_locking import Notification, NotificationType
        
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
            created_at=datetime.now(),
            read_at=None,
            metadata={}
        )
        
        # Mock broadcast method
        web_interface.broadcast_to_document = AsyncMock()
        
        # Handle notification
        await web_interface._handle_locking_notification(notification)
        
        # Verify broadcast was called
        web_interface.broadcast_to_document.assert_called_once_with(
            "doc1",
            {
                'type': 'notification',
                'notification': notification.to_dict()
            }
        )