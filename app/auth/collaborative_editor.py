"""
CollaborativeEditor for real-time collaborative editing of MoM documents.
Supports WebSocket communication, conflict resolution, and presence indicators.
"""

import asyncio
import json
import logging
import secrets
import time
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any, Set, Callable
import websockets
from websockets.server import WebSocketServerProtocol
import threading
from dataclasses import dataclass, asdict
from enum import Enum

from .auth_manager import AuthManager

logger = logging.getLogger(__name__)


class OperationType(Enum):
    """Types of operations for collaborative editing"""
    INSERT = "insert"
    DELETE = "delete"
    REPLACE = "replace"
    FORMAT = "format"


@dataclass
class Operation:
    """Represents a single editing operation"""
    id: str
    type: OperationType
    position: int
    content: str = ""
    length: int = 0
    user_id: str = ""
    timestamp: float = 0.0
    metadata: Dict[str, Any] = None
    
    def __post_init__(self):
        if self.timestamp == 0.0:
            self.timestamp = time.time()
        if self.metadata is None:
            self.metadata = {}
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert operation to dictionary"""
        return {
            'id': self.id,
            'type': self.type.value,
            'position': self.position,
            'content': self.content,
            'length': self.length,
            'user_id': self.user_id,
            'timestamp': self.timestamp,
            'metadata': self.metadata
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'Operation':
        """Create operation from dictionary"""
        return cls(
            id=data['id'],
            type=OperationType(data['type']),
            position=data['position'],
            content=data.get('content', ''),
            length=data.get('length', 0),
            user_id=data.get('user_id', ''),
            timestamp=data.get('timestamp', time.time()),
            metadata=data.get('metadata', {})
        )


@dataclass
class DocumentState:
    """Represents the current state of a document"""
    document_id: str
    content: str
    version: int
    last_modified: datetime
    operations: List[Operation]
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert document state to dictionary"""
        return {
            'document_id': self.document_id,
            'content': self.content,
            'version': self.version,
            'last_modified': self.last_modified.isoformat(),
            'operations': [op.to_dict() for op in self.operations]
        }


@dataclass
class UserPresence:
    """Represents user presence in a document"""
    user_id: str
    username: str
    cursor_position: int
    selection_start: int
    selection_end: int
    last_seen: datetime
    is_active: bool
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert user presence to dictionary"""
        return {
            'user_id': self.user_id,
            'username': self.username,
            'cursor_position': self.cursor_position,
            'selection_start': self.selection_start,
            'selection_end': self.selection_end,
            'last_seen': self.last_seen.isoformat(),
            'is_active': self.is_active
        }


class OperationalTransform:
    """
    Operational Transformation for conflict resolution.
    Implements basic OT algorithms for text operations.
    """
    
    @staticmethod
    def transform_operation(op1: Operation, op2: Operation) -> tuple[Operation, Operation]:
        """
        Transform two concurrent operations to maintain consistency.
        Returns transformed versions of both operations.
        """
        # Create copies to avoid modifying originals
        transformed_op1 = Operation(
            id=op1.id,
            type=op1.type,
            position=op1.position,
            content=op1.content,
            length=op1.length,
            user_id=op1.user_id,
            timestamp=op1.timestamp,
            metadata=op1.metadata.copy() if op1.metadata else {}
        )
        
        transformed_op2 = Operation(
            id=op2.id,
            type=op2.type,
            position=op2.position,
            content=op2.content,
            length=op2.length,
            user_id=op2.user_id,
            timestamp=op2.timestamp,
            metadata=op2.metadata.copy() if op2.metadata else {}
        )
        
        # Transform based on operation types
        if op1.type == OperationType.INSERT and op2.type == OperationType.INSERT:
            if op1.position <= op2.position:
                transformed_op2.position += len(op1.content)
            else:
                transformed_op1.position += len(op2.content)
        
        elif op1.type == OperationType.INSERT and op2.type == OperationType.DELETE:
            if op1.position <= op2.position:
                transformed_op2.position += len(op1.content)
            elif op1.position < op2.position + op2.length:
                # Insert is within delete range
                transformed_op2.length += len(op1.content)
            else:
                # Insert is after delete range
                pass
        
        elif op1.type == OperationType.DELETE and op2.type == OperationType.INSERT:
            if op2.position <= op1.position:
                transformed_op1.position += len(op2.content)
            elif op2.position < op1.position + op1.length:
                # Insert is within delete range
                transformed_op1.length += len(op2.content)
            else:
                # Insert is after delete range
                pass
        
        elif op1.type == OperationType.DELETE and op2.type == OperationType.DELETE:
            if op1.position + op1.length <= op2.position:
                # op1 is completely before op2
                transformed_op2.position -= op1.length
            elif op2.position + op2.length <= op1.position:
                # op2 is completely before op1
                transformed_op1.position -= op2.length
            else:
                # Overlapping deletes - need to handle carefully
                if op1.position <= op2.position:
                    if op1.position + op1.length >= op2.position + op2.length:
                        # op1 completely contains op2
                        transformed_op1.length -= op2.length
                        transformed_op2.length = 0  # op2 becomes no-op
                    else:
                        # Partial overlap
                        overlap = op1.position + op1.length - op2.position
                        transformed_op1.length -= overlap
                        transformed_op2.position = op1.position
                        transformed_op2.length -= overlap
                else:
                    # op2.position < op1.position
                    if op2.position + op2.length >= op1.position + op1.length:
                        # op2 completely contains op1
                        transformed_op2.length -= op1.length
                        transformed_op1.length = 0  # op1 becomes no-op
                    else:
                        # Partial overlap
                        overlap = op2.position + op2.length - op1.position
                        transformed_op2.length -= overlap
                        transformed_op1.position = op2.position
                        transformed_op1.length -= overlap
        
        return transformed_op1, transformed_op2
    
    @staticmethod
    def apply_operation(content: str, operation: Operation) -> str:
        """Apply an operation to content and return the result"""
        if operation.type == OperationType.INSERT:
            return content[:operation.position] + operation.content + content[operation.position:]
        
        elif operation.type == OperationType.DELETE:
            end_pos = operation.position + operation.length
            return content[:operation.position] + content[end_pos:]
        
        elif operation.type == OperationType.REPLACE:
            end_pos = operation.position + operation.length
            return content[:operation.position] + operation.content + content[end_pos:]
        
        return content


class CollaborativeDocument:
    """Manages a single collaborative document"""
    
    def __init__(self, document_id: str, initial_content: str = ""):
        self.document_id = document_id
        self.state = DocumentState(
            document_id=document_id,
            content=initial_content,
            version=0,
            last_modified=datetime.now(),
            operations=[]
        )
        self.connected_users: Dict[str, UserPresence] = {}
        self.operation_history: List[Operation] = []
        self.lock = asyncio.Lock()
    
    async def add_user(self, user_id: str, username: str):
        """Add a user to the document"""
        async with self.lock:
            self.connected_users[user_id] = UserPresence(
                user_id=user_id,
                username=username,
                cursor_position=0,
                selection_start=0,
                selection_end=0,
                last_seen=datetime.now(),
                is_active=True
            )
    
    async def remove_user(self, user_id: str):
        """Remove a user from the document"""
        async with self.lock:
            if user_id in self.connected_users:
                del self.connected_users[user_id]
    
    async def update_user_presence(self, user_id: str, cursor_position: int, 
                                 selection_start: int = None, selection_end: int = None):
        """Update user presence information"""
        async with self.lock:
            if user_id in self.connected_users:
                presence = self.connected_users[user_id]
                presence.cursor_position = cursor_position
                if selection_start is not None:
                    presence.selection_start = selection_start
                if selection_end is not None:
                    presence.selection_end = selection_end
                presence.last_seen = datetime.now()
                presence.is_active = True
    
    async def apply_operation(self, operation: Operation) -> bool:
        """Apply an operation to the document with conflict resolution"""
        async with self.lock:
            try:
                # Transform operation against concurrent operations
                transformed_op = operation
                for existing_op in self.operation_history:
                    if existing_op.timestamp > operation.timestamp:
                        transformed_op, _ = OperationalTransform.transform_operation(
                            transformed_op, existing_op
                        )
                
                # Apply the transformed operation
                new_content = OperationalTransform.apply_operation(
                    self.state.content, transformed_op
                )
                
                # Update document state
                self.state.content = new_content
                self.state.version += 1
                self.state.last_modified = datetime.now()
                self.state.operations.append(transformed_op)
                self.operation_history.append(transformed_op)
                
                # Keep operation history manageable
                if len(self.operation_history) > 1000:
                    self.operation_history = self.operation_history[-500:]
                
                return True
                
            except Exception as e:
                logger.error(f"Error applying operation: {str(e)}")
                return False
    
    def get_state(self) -> DocumentState:
        """Get current document state"""
        return self.state
    
    def get_presence_info(self) -> List[Dict[str, Any]]:
        """Get presence information for all connected users"""
        return [presence.to_dict() for presence in self.connected_users.values()]


class CollaborativeEditor:
    """
    Main collaborative editor class that manages WebSocket connections,
    document synchronization, and real-time collaboration.
    """
    
    def __init__(self, auth_manager: AuthManager, config: Dict[str, Any] = None):
        self.auth_manager = auth_manager
        self.config = config or {}
        
        # Configuration
        self.host = self.config.get('host', 'localhost')
        self.port = self.config.get('port', 8765)
        self.max_connections = self.config.get('max_connections', 100)
        
        # Document management
        self.documents: Dict[str, CollaborativeDocument] = {}
        self.connections: Dict[str, WebSocketServerProtocol] = {}
        self.user_connections: Dict[str, Set[str]] = {}  # user_id -> set of connection_ids
        
        # WebSocket server
        self.server = None
        self.is_running = False
        
        logger.info("CollaborativeEditor initialized")
    
    async def start_server(self):
        """Start the WebSocket server"""
        try:
            self.server = await websockets.serve(
                self.handle_connection,
                self.host,
                self.port,
                max_size=1024*1024,  # 1MB max message size
                max_queue=32
            )
            self.is_running = True
            logger.info(f"CollaborativeEditor server started on {self.host}:{self.port}")
            
        except Exception as e:
            logger.error(f"Failed to start CollaborativeEditor server: {str(e)}")
            raise
    
    async def stop_server(self):
        """Stop the WebSocket server"""
        if self.server:
            self.server.close()
            await self.server.wait_closed()
            self.is_running = False
            logger.info("CollaborativeEditor server stopped")
    
    async def handle_connection(self, websocket: WebSocketServerProtocol, path: str):
        """Handle new WebSocket connection"""
        connection_id = secrets.token_hex(16)
        self.connections[connection_id] = websocket
        
        try:
            logger.info(f"New connection: {connection_id}")
            
            async for message in websocket:
                try:
                    data = json.loads(message)
                    await self.handle_message(connection_id, data)
                except json.JSONDecodeError:
                    await self.send_error(connection_id, "Invalid JSON format")
                except Exception as e:
                    logger.error(f"Error handling message: {str(e)}")
                    await self.send_error(connection_id, "Internal server error")
        
        except websockets.exceptions.ConnectionClosed:
            logger.info(f"Connection closed: {connection_id}")
        except Exception as e:
            logger.error(f"Connection error: {str(e)}")
        finally:
            await self.cleanup_connection(connection_id)
    
    async def handle_message(self, connection_id: str, data: Dict[str, Any]):
        """Handle incoming WebSocket message"""
        message_type = data.get('type')
        
        if message_type == 'authenticate':
            await self.handle_authentication(connection_id, data)
        elif message_type == 'join_document':
            await self.handle_join_document(connection_id, data)
        elif message_type == 'leave_document':
            await self.handle_leave_document(connection_id, data)
        elif message_type == 'operation':
            await self.handle_operation(connection_id, data)
        elif message_type == 'cursor_update':
            await self.handle_cursor_update(connection_id, data)
        elif message_type == 'ping':
            await self.send_message(connection_id, {'type': 'pong'})
        else:
            await self.send_error(connection_id, f"Unknown message type: {message_type}")
    
    async def handle_authentication(self, connection_id: str, data: Dict[str, Any]):
        """Handle user authentication"""
        token = data.get('token')
        if not token:
            await self.send_error(connection_id, "Authentication token required")
            return
        
        # Validate token
        validation_result = self.auth_manager.validate_token(token)
        if not validation_result['valid']:
            await self.send_error(connection_id, "Invalid authentication token")
            return
        
        user_id = validation_result['user']['user_id']
        username = validation_result['user']['username']
        
        # Store user connection mapping
        if user_id not in self.user_connections:
            self.user_connections[user_id] = set()
        self.user_connections[user_id].add(connection_id)
        
        # Send authentication success
        await self.send_message(connection_id, {
            'type': 'authenticated',
            'user': validation_result['user']
        })
        
        logger.info(f"User authenticated: {username} ({user_id}) on connection {connection_id}")
    
    async def handle_join_document(self, connection_id: str, data: Dict[str, Any]):
        """Handle user joining a document"""
        document_id = data.get('document_id')
        if not document_id:
            await self.send_error(connection_id, "Document ID required")
            return
        
        # Get user info from connection
        user_info = await self.get_user_from_connection(connection_id)
        if not user_info:
            await self.send_error(connection_id, "Authentication required")
            return
        
        # Create document if it doesn't exist
        if document_id not in self.documents:
            initial_content = data.get('initial_content', '')
            self.documents[document_id] = CollaborativeDocument(document_id, initial_content)
        
        document = self.documents[document_id]
        
        # Add user to document
        await document.add_user(user_info['user_id'], user_info['username'])
        
        # Send document state to user
        await self.send_message(connection_id, {
            'type': 'document_state',
            'document': document.get_state().to_dict(),
            'presence': document.get_presence_info()
        })
        
        # Notify other users
        await self.broadcast_to_document(document_id, {
            'type': 'user_joined',
            'user': user_info,
            'presence': document.get_presence_info()
        }, exclude_connection=connection_id)
        
        logger.info(f"User {user_info['username']} joined document {document_id}")
    
    async def handle_leave_document(self, connection_id: str, data: Dict[str, Any]):
        """Handle user leaving a document"""
        document_id = data.get('document_id')
        if not document_id or document_id not in self.documents:
            return
        
        user_info = await self.get_user_from_connection(connection_id)
        if not user_info:
            return
        
        document = self.documents[document_id]
        await document.remove_user(user_info['user_id'])
        
        # Notify other users
        await self.broadcast_to_document(document_id, {
            'type': 'user_left',
            'user': user_info,
            'presence': document.get_presence_info()
        }, exclude_connection=connection_id)
        
        logger.info(f"User {user_info['username']} left document {document_id}")
    
    async def handle_operation(self, connection_id: str, data: Dict[str, Any]):
        """Handle document operation"""
        document_id = data.get('document_id')
        operation_data = data.get('operation')
        
        if not document_id or not operation_data:
            await self.send_error(connection_id, "Document ID and operation required")
            return
        
        if document_id not in self.documents:
            await self.send_error(connection_id, "Document not found")
            return
        
        user_info = await self.get_user_from_connection(connection_id)
        if not user_info:
            await self.send_error(connection_id, "Authentication required")
            return
        
        try:
            # Create operation object
            operation = Operation.from_dict(operation_data)
            operation.user_id = user_info['user_id']
            operation.id = secrets.token_hex(16)
            
            # Apply operation to document
            document = self.documents[document_id]
            success = await document.apply_operation(operation)
            
            if success:
                # Broadcast operation to all users in document
                await self.broadcast_to_document(document_id, {
                    'type': 'operation_applied',
                    'operation': operation.to_dict(),
                    'document_version': document.get_state().version
                })
                
                logger.debug(f"Operation applied: {operation.type.value} by {user_info['username']}")
            else:
                await self.send_error(connection_id, "Failed to apply operation")
                
        except Exception as e:
            logger.error(f"Error handling operation: {str(e)}")
            await self.send_error(connection_id, "Invalid operation format")
    
    async def handle_cursor_update(self, connection_id: str, data: Dict[str, Any]):
        """Handle cursor position update"""
        document_id = data.get('document_id')
        cursor_position = data.get('cursor_position')
        selection_start = data.get('selection_start')
        selection_end = data.get('selection_end')
        
        if document_id not in self.documents:
            return
        
        user_info = await self.get_user_from_connection(connection_id)
        if not user_info:
            return
        
        document = self.documents[document_id]
        await document.update_user_presence(
            user_info['user_id'],
            cursor_position,
            selection_start,
            selection_end
        )
        
        # Broadcast presence update
        await self.broadcast_to_document(document_id, {
            'type': 'presence_update',
            'presence': document.get_presence_info()
        }, exclude_connection=connection_id)
    
    async def get_user_from_connection(self, connection_id: str) -> Optional[Dict[str, Any]]:
        """Get user information from connection ID"""
        # In a real implementation, you'd store this mapping during authentication
        # For now, we'll return None to indicate authentication is required
        for user_id, connection_ids in self.user_connections.items():
            if connection_id in connection_ids:
                user = self.auth_manager.get_user_by_id(user_id)
                if user:
                    return {
                        'user_id': user.user_id,
                        'username': user.username,
                        'role': user.role
                    }
        return None
    
    async def send_message(self, connection_id: str, message: Dict[str, Any]):
        """Send message to a specific connection"""
        if connection_id in self.connections:
            try:
                websocket = self.connections[connection_id]
                await websocket.send(json.dumps(message))
            except Exception as e:
                logger.error(f"Error sending message to {connection_id}: {str(e)}")
    
    async def send_error(self, connection_id: str, error_message: str):
        """Send error message to a connection"""
        await self.send_message(connection_id, {
            'type': 'error',
            'message': error_message
        })
    
    async def broadcast_to_document(self, document_id: str, message: Dict[str, Any], 
                                  exclude_connection: str = None):
        """Broadcast message to all users in a document"""
        if document_id not in self.documents:
            return
        
        document = self.documents[document_id]
        tasks = []
        
        for user_id in document.connected_users:
            if user_id in self.user_connections:
                for connection_id in self.user_connections[user_id]:
                    if connection_id != exclude_connection and connection_id in self.connections:
                        tasks.append(self.send_message(connection_id, message))
        
        if tasks:
            await asyncio.gather(*tasks, return_exceptions=True)
    
    async def cleanup_connection(self, connection_id: str):
        """Clean up connection and associated resources"""
        # Remove from connections
        if connection_id in self.connections:
            del self.connections[connection_id]
        
        # Remove from user connections
        user_to_remove = None
        for user_id, connection_ids in self.user_connections.items():
            if connection_id in connection_ids:
                connection_ids.remove(connection_id)
                if not connection_ids:  # No more connections for this user
                    user_to_remove = user_id
                break
        
        if user_to_remove:
            del self.user_connections[user_to_remove]
            
            # Remove user from all documents
            for document in self.documents.values():
                await document.remove_user(user_to_remove)
        
        logger.info(f"Connection cleaned up: {connection_id}")
    
    def create_document(self, document_id: str, initial_content: str = "") -> str:
        """Create a new collaborative document"""
        if document_id in self.documents:
            return document_id
        
        self.documents[document_id] = CollaborativeDocument(document_id, initial_content)
        logger.info(f"Created document: {document_id}")
        return document_id
    
    def get_document_state(self, document_id: str) -> Optional[DocumentState]:
        """Get current state of a document"""
        if document_id in self.documents:
            return self.documents[document_id].get_state()
        return None
    
    def list_documents(self) -> List[str]:
        """List all document IDs"""
        return list(self.documents.keys())
    
    def get_document_users(self, document_id: str) -> List[Dict[str, Any]]:
        """Get users currently in a document"""
        if document_id in self.documents:
            return self.documents[document_id].get_presence_info()
        return []
    
    async def run_server(self):
        """Run the server (blocking call)"""
        await self.start_server()
        try:
            # Keep server running
            await asyncio.Future()  # Run forever
        except KeyboardInterrupt:
            logger.info("Server interrupted")
        finally:
            await self.stop_server()


# Utility functions for running the server
def run_collaborative_editor(auth_manager: AuthManager, config: Dict[str, Any] = None):
    """Run collaborative editor server in a separate thread"""
    editor = CollaborativeEditor(auth_manager, config)
    
    def run_server():
        asyncio.run(editor.run_server())
    
    server_thread = threading.Thread(target=run_server, daemon=True)
    server_thread.start()
    
    return editor, server_thread