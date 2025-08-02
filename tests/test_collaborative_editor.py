"""
Unit tests for CollaborativeEditor
"""

import pytest
import asyncio
import json
import time
from datetime import datetime, timedelta
from unittest.mock import Mock, AsyncMock, patch

from app.auth.auth_manager import AuthManager
from app.auth.collaborative_editor import (
    CollaborativeEditor, CollaborativeDocument, Operation, OperationType,
    DocumentState, UserPresence, OperationalTransform
)


class TestOperation:
    """Test cases for Operation class"""
    
    def test_operation_creation(self):
        """Test operation creation"""
        op = Operation(
            id="test123",
            type=OperationType.INSERT,
            position=10,
            content="hello",
            user_id="user1"
        )
        
        assert op.id == "test123"
        assert op.type == OperationType.INSERT
        assert op.position == 10
        assert op.content == "hello"
        assert op.user_id == "user1"
        assert op.timestamp > 0
    
    def test_operation_to_dict(self):
        """Test operation to dictionary conversion"""
        op = Operation(
            id="test123",
            type=OperationType.INSERT,
            position=10,
            content="hello",
            user_id="user1"
        )
        
        op_dict = op.to_dict()
        
        assert op_dict['id'] == "test123"
        assert op_dict['type'] == "insert"
        assert op_dict['position'] == 10
        assert op_dict['content'] == "hello"
        assert op_dict['user_id'] == "user1"
        assert 'timestamp' in op_dict
    
    def test_operation_from_dict(self):
        """Test operation creation from dictionary"""
        op_data = {
            'id': 'test123',
            'type': 'insert',
            'position': 10,
            'content': 'hello',
            'user_id': 'user1',
            'timestamp': time.time()
        }
        
        op = Operation.from_dict(op_data)
        
        assert op.id == "test123"
        assert op.type == OperationType.INSERT
        assert op.position == 10
        assert op.content == "hello"
        assert op.user_id == "user1"


class TestOperationalTransform:
    """Test cases for OperationalTransform"""
    
    def test_transform_insert_insert_before(self):
        """Test transforming two insert operations where first is before second"""
        op1 = Operation("1", OperationType.INSERT, 5, "hello", user_id="user1")
        op2 = Operation("2", OperationType.INSERT, 10, "world", user_id="user2")
        
        t_op1, t_op2 = OperationalTransform.transform_operation(op1, op2)
        
        assert t_op1.position == 5  # unchanged
        assert t_op2.position == 15  # moved by length of op1
    
    def test_transform_insert_insert_after(self):
        """Test transforming two insert operations where first is after second"""
        op1 = Operation("1", OperationType.INSERT, 10, "hello", user_id="user1")
        op2 = Operation("2", OperationType.INSERT, 5, "world", user_id="user2")
        
        t_op1, t_op2 = OperationalTransform.transform_operation(op1, op2)
        
        assert t_op1.position == 15  # moved by length of op2
        assert t_op2.position == 5   # unchanged
    
    def test_transform_insert_delete(self):
        """Test transforming insert and delete operations"""
        op1 = Operation("1", OperationType.INSERT, 5, "hello", user_id="user1")
        op2 = Operation("2", OperationType.DELETE, 10, length=3, user_id="user2")
        
        t_op1, t_op2 = OperationalTransform.transform_operation(op1, op2)
        
        assert t_op1.position == 5   # unchanged
        assert t_op2.position == 15  # moved by length of insert
    
    def test_transform_delete_delete_non_overlapping(self):
        """Test transforming two non-overlapping delete operations"""
        op1 = Operation("1", OperationType.DELETE, 5, length=3, user_id="user1")
        op2 = Operation("2", OperationType.DELETE, 10, length=2, user_id="user2")
        
        t_op1, t_op2 = OperationalTransform.transform_operation(op1, op2)
        
        assert t_op1.position == 5  # unchanged
        assert t_op1.length == 3    # unchanged
        assert t_op2.position == 7  # moved by length of op1
        assert t_op2.length == 2    # unchanged
    
    def test_apply_insert_operation(self):
        """Test applying insert operation"""
        content = "Hello world"
        op = Operation("1", OperationType.INSERT, 6, "beautiful ", user_id="user1")
        
        result = OperationalTransform.apply_operation(content, op)
        
        assert result == "Hello beautiful world"
    
    def test_apply_delete_operation(self):
        """Test applying delete operation"""
        content = "Hello beautiful world"
        op = Operation("1", OperationType.DELETE, 6, length=10, user_id="user1")
        
        result = OperationalTransform.apply_operation(content, op)
        
        assert result == "Hello world"
    
    def test_apply_replace_operation(self):
        """Test applying replace operation"""
        content = "Hello world"
        op = Operation("1", OperationType.REPLACE, 6, "universe", length=5, user_id="user1")
        
        result = OperationalTransform.apply_operation(content, op)
        
        assert result == "Hello universe"


class TestCollaborativeDocument:
    """Test cases for CollaborativeDocument"""
    
    @pytest.fixture
    def document(self):
        """Create a test document"""
        return CollaborativeDocument("test_doc", "Initial content")
    
    @pytest.mark.asyncio
    async def test_document_creation(self, document):
        """Test document creation"""
        assert document.document_id == "test_doc"
        assert document.state.content == "Initial content"
        assert document.state.version == 0
        assert len(document.connected_users) == 0
    
    @pytest.mark.asyncio
    async def test_add_user(self, document):
        """Test adding user to document"""
        await document.add_user("user1", "testuser")
        
        assert "user1" in document.connected_users
        assert document.connected_users["user1"].username == "testuser"
        assert document.connected_users["user1"].is_active is True
    
    @pytest.mark.asyncio
    async def test_remove_user(self, document):
        """Test removing user from document"""
        await document.add_user("user1", "testuser")
        await document.remove_user("user1")
        
        assert "user1" not in document.connected_users
    
    @pytest.mark.asyncio
    async def test_update_user_presence(self, document):
        """Test updating user presence"""
        await document.add_user("user1", "testuser")
        await document.update_user_presence("user1", 10, 5, 15)
        
        presence = document.connected_users["user1"]
        assert presence.cursor_position == 10
        assert presence.selection_start == 5
        assert presence.selection_end == 15
    
    @pytest.mark.asyncio
    async def test_apply_operation(self, document):
        """Test applying operation to document"""
        op = Operation("1", OperationType.INSERT, 7, " test", user_id="user1")
        
        success = await document.apply_operation(op)
        
        assert success is True
        assert document.state.content == "Initial test content"
        assert document.state.version == 1
        assert len(document.state.operations) == 1
    
    @pytest.mark.asyncio
    async def test_get_presence_info(self, document):
        """Test getting presence information"""
        await document.add_user("user1", "testuser1")
        await document.add_user("user2", "testuser2")
        
        presence_info = document.get_presence_info()
        
        assert len(presence_info) == 2
        assert any(p['username'] == 'testuser1' for p in presence_info)
        assert any(p['username'] == 'testuser2' for p in presence_info)


class TestCollaborativeEditor:
    """Test cases for CollaborativeEditor"""
    
    @pytest.fixture
    def auth_manager(self):
        """Create a test auth manager"""
        auth_manager = AuthManager()
        # Register test users
        auth_manager.register_user("testuser1", "test1@example.com", "password123")
        auth_manager.register_user("testuser2", "test2@example.com", "password123")
        return auth_manager
    
    @pytest.fixture
    def editor(self, auth_manager):
        """Create a test collaborative editor"""
        config = {
            'host': 'localhost',
            'port': 8766,  # Different port for testing
            'max_connections': 10
        }
        return CollaborativeEditor(auth_manager, config)
    
    def test_editor_initialization(self, editor):
        """Test editor initialization"""
        assert editor.host == 'localhost'
        assert editor.port == 8766
        assert editor.max_connections == 10
        assert len(editor.documents) == 0
        assert len(editor.connections) == 0
    
    def test_create_document(self, editor):
        """Test creating a document"""
        doc_id = editor.create_document("test_doc", "Initial content")
        
        assert doc_id == "test_doc"
        assert "test_doc" in editor.documents
        assert editor.documents["test_doc"].state.content == "Initial content"
    
    def test_get_document_state(self, editor):
        """Test getting document state"""
        editor.create_document("test_doc", "Initial content")
        
        state = editor.get_document_state("test_doc")
        
        assert state is not None
        assert state.document_id == "test_doc"
        assert state.content == "Initial content"
    
    def test_get_document_state_nonexistent(self, editor):
        """Test getting state of non-existent document"""
        state = editor.get_document_state("nonexistent")
        
        assert state is None
    
    def test_list_documents(self, editor):
        """Test listing documents"""
        editor.create_document("doc1", "Content 1")
        editor.create_document("doc2", "Content 2")
        
        docs = editor.list_documents()
        
        assert len(docs) == 2
        assert "doc1" in docs
        assert "doc2" in docs
    
    def test_get_document_users_empty(self, editor):
        """Test getting users from empty document"""
        editor.create_document("test_doc")
        
        users = editor.get_document_users("test_doc")
        
        assert len(users) == 0
    
    @pytest.mark.asyncio
    async def test_get_document_users_with_users(self, editor):
        """Test getting users from document with users"""
        editor.create_document("test_doc")
        document = editor.documents["test_doc"]
        
        await document.add_user("user1", "testuser1")
        await document.add_user("user2", "testuser2")
        
        users = editor.get_document_users("test_doc")
        
        assert len(users) == 2
        assert any(u['username'] == 'testuser1' for u in users)
        assert any(u['username'] == 'testuser2' for u in users)
    
    @pytest.mark.asyncio
    async def test_handle_authentication_success(self, editor, auth_manager):
        """Test successful authentication handling"""
        # Authenticate user to get token
        auth_result = auth_manager.authenticate_user("testuser1", "password123")
        token = auth_result['access_token']
        
        # Mock connection
        connection_id = "conn123"
        editor.connections[connection_id] = Mock()
        
        # Mock send_message
        editor.send_message = AsyncMock()
        
        # Handle authentication
        await editor.handle_authentication(connection_id, {'token': token})
        
        # Verify user connection mapping
        user_id = auth_result['user']['user_id']
        assert user_id in editor.user_connections
        assert connection_id in editor.user_connections[user_id]
        
        # Verify success message was sent
        editor.send_message.assert_called_once()
        call_args = editor.send_message.call_args[0]
        assert call_args[0] == connection_id
        assert call_args[1]['type'] == 'authenticated'
    
    @pytest.mark.asyncio
    async def test_handle_authentication_invalid_token(self, editor):
        """Test authentication with invalid token"""
        connection_id = "conn123"
        editor.connections[connection_id] = Mock()
        editor.send_error = AsyncMock()
        
        await editor.handle_authentication(connection_id, {'token': 'invalid_token'})
        
        editor.send_error.assert_called_once_with(connection_id, "Invalid authentication token")
    
    @pytest.mark.asyncio
    async def test_handle_authentication_missing_token(self, editor):
        """Test authentication with missing token"""
        connection_id = "conn123"
        editor.connections[connection_id] = Mock()
        editor.send_error = AsyncMock()
        
        await editor.handle_authentication(connection_id, {})
        
        editor.send_error.assert_called_once_with(connection_id, "Authentication token required")
    
    @pytest.mark.asyncio
    async def test_cleanup_connection(self, editor):
        """Test connection cleanup"""
        connection_id = "conn123"
        user_id = "user123"
        
        # Set up connection and user mapping
        editor.connections[connection_id] = Mock()
        editor.user_connections[user_id] = {connection_id}
        
        # Create document with user
        editor.create_document("test_doc")
        document = editor.documents["test_doc"]
        await document.add_user(user_id, "testuser")
        
        # Cleanup connection
        await editor.cleanup_connection(connection_id)
        
        # Verify cleanup
        assert connection_id not in editor.connections
        assert user_id not in editor.user_connections
        assert user_id not in document.connected_users
    
    @pytest.mark.asyncio
    async def test_send_message(self, editor):
        """Test sending message to connection"""
        connection_id = "conn123"
        mock_websocket = AsyncMock()
        editor.connections[connection_id] = mock_websocket
        
        message = {'type': 'test', 'data': 'hello'}
        await editor.send_message(connection_id, message)
        
        mock_websocket.send.assert_called_once_with(json.dumps(message))
    
    @pytest.mark.asyncio
    async def test_send_error(self, editor):
        """Test sending error message"""
        connection_id = "conn123"
        mock_websocket = AsyncMock()
        editor.connections[connection_id] = mock_websocket
        
        await editor.send_error(connection_id, "Test error")
        
        expected_message = json.dumps({
            'type': 'error',
            'message': 'Test error'
        })
        mock_websocket.send.assert_called_once_with(expected_message)


class TestUserPresence:
    """Test cases for UserPresence"""
    
    def test_user_presence_creation(self):
        """Test user presence creation"""
        presence = UserPresence(
            user_id="user1",
            username="testuser",
            cursor_position=10,
            selection_start=5,
            selection_end=15,
            last_seen=datetime.now(),
            is_active=True
        )
        
        assert presence.user_id == "user1"
        assert presence.username == "testuser"
        assert presence.cursor_position == 10
        assert presence.selection_start == 5
        assert presence.selection_end == 15
        assert presence.is_active is True
    
    def test_user_presence_to_dict(self):
        """Test user presence to dictionary conversion"""
        now = datetime.now()
        presence = UserPresence(
            user_id="user1",
            username="testuser",
            cursor_position=10,
            selection_start=5,
            selection_end=15,
            last_seen=now,
            is_active=True
        )
        
        presence_dict = presence.to_dict()
        
        assert presence_dict['user_id'] == "user1"
        assert presence_dict['username'] == "testuser"
        assert presence_dict['cursor_position'] == 10
        assert presence_dict['selection_start'] == 5
        assert presence_dict['selection_end'] == 15
        assert presence_dict['last_seen'] == now.isoformat()
        assert presence_dict['is_active'] is True


class TestDocumentState:
    """Test cases for DocumentState"""
    
    def test_document_state_creation(self):
        """Test document state creation"""
        now = datetime.now()
        operations = [
            Operation("1", OperationType.INSERT, 0, "Hello", user_id="user1")
        ]
        
        state = DocumentState(
            document_id="test_doc",
            content="Hello world",
            version=1,
            last_modified=now,
            operations=operations
        )
        
        assert state.document_id == "test_doc"
        assert state.content == "Hello world"
        assert state.version == 1
        assert state.last_modified == now
        assert len(state.operations) == 1
    
    def test_document_state_to_dict(self):
        """Test document state to dictionary conversion"""
        now = datetime.now()
        operations = [
            Operation("1", OperationType.INSERT, 0, "Hello", user_id="user1")
        ]
        
        state = DocumentState(
            document_id="test_doc",
            content="Hello world",
            version=1,
            last_modified=now,
            operations=operations
        )
        
        state_dict = state.to_dict()
        
        assert state_dict['document_id'] == "test_doc"
        assert state_dict['content'] == "Hello world"
        assert state_dict['version'] == 1
        assert state_dict['last_modified'] == now.isoformat()
        assert len(state_dict['operations']) == 1
        assert state_dict['operations'][0]['type'] == "insert"