"""
AuthManager for user authentication and management in collaborative editing.
Handles user authentication, token management, and user permissions.
"""

import hashlib
import secrets
import time
import json
from typing import Dict, Optional, List, Any
from datetime import datetime, timedelta
import logging

logger = logging.getLogger(__name__)


class User:
    """User model for authentication system"""
    
    def __init__(self, user_id: str, username: str, email: str, 
                 password_hash: str = None, role: str = "user", 
                 created_at: datetime = None):
        self.user_id = user_id
        self.username = username
        self.email = email
        self.password_hash = password_hash
        self.role = role  # "admin", "editor", "viewer", "user"
        self.created_at = created_at or datetime.now()
        self.last_login = None
        self.is_active = True
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert user to dictionary (excluding sensitive data)"""
        return {
            'user_id': self.user_id,
            'username': self.username,
            'email': self.email,
            'role': self.role,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'last_login': self.last_login.isoformat() if self.last_login else None,
            'is_active': self.is_active
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'User':
        """Create user from dictionary"""
        user = cls(
            user_id=data['user_id'],
            username=data['username'],
            email=data['email'],
            password_hash=data.get('password_hash'),
            role=data.get('role', 'user')
        )
        if data.get('created_at'):
            user.created_at = datetime.fromisoformat(data['created_at'])
        if data.get('last_login'):
            user.last_login = datetime.fromisoformat(data['last_login'])
        user.is_active = data.get('is_active', True)
        return user


class AuthToken:
    """Authentication token model"""
    
    def __init__(self, token: str, user_id: str, expires_at: datetime, 
                 token_type: str = "access"):
        self.token = token
        self.user_id = user_id
        self.expires_at = expires_at
        self.token_type = token_type  # "access", "refresh"
        self.created_at = datetime.now()
    
    def is_expired(self) -> bool:
        """Check if token is expired"""
        return datetime.now() > self.expires_at
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert token to dictionary"""
        return {
            'token': self.token,
            'user_id': self.user_id,
            'expires_at': self.expires_at.isoformat(),
            'token_type': self.token_type,
            'created_at': self.created_at.isoformat()
        }


class AuthManager:
    """
    Authentication manager for collaborative editing features.
    Handles user registration, login, token management, and permissions.
    """
    
    def __init__(self, config: Dict[str, Any] = None):
        self.config = config or {}
        self.users: Dict[str, User] = {}  # In-memory storage for demo
        self.tokens: Dict[str, AuthToken] = {}  # In-memory token storage
        self.sessions: Dict[str, Dict[str, Any]] = {}  # Active sessions
        
        # Configuration
        self.token_expiry_hours = self.config.get('token_expiry_hours', 24)
        self.refresh_token_expiry_days = self.config.get('refresh_token_expiry_days', 30)
        self.max_login_attempts = self.config.get('max_login_attempts', 5)
        self.lockout_duration_minutes = self.config.get('lockout_duration_minutes', 15)
        
        # Login attempt tracking
        self.login_attempts: Dict[str, List[datetime]] = {}
        
        logger.info("AuthManager initialized")
    
    def _hash_password(self, password: str, salt: str = None) -> tuple[str, str]:
        """Hash password with salt"""
        if salt is None:
            salt = secrets.token_hex(32)
        
        password_hash = hashlib.pbkdf2_hmac(
            'sha256',
            password.encode('utf-8'),
            salt.encode('utf-8'),
            100000  # iterations
        )
        return password_hash.hex(), salt
    
    def _verify_password(self, password: str, password_hash: str, salt: str) -> bool:
        """Verify password against hash"""
        computed_hash, _ = self._hash_password(password, salt)
        return secrets.compare_digest(computed_hash, password_hash)
    
    def _generate_token(self, user_id: str, token_type: str = "access") -> AuthToken:
        """Generate authentication token"""
        token = secrets.token_urlsafe(32)
        
        if token_type == "access":
            expires_at = datetime.now() + timedelta(hours=self.token_expiry_hours)
        else:  # refresh token
            expires_at = datetime.now() + timedelta(days=self.refresh_token_expiry_days)
        
        auth_token = AuthToken(token, user_id, expires_at, token_type)
        self.tokens[token] = auth_token
        
        return auth_token
    
    def _is_account_locked(self, identifier: str) -> bool:
        """Check if account is locked due to failed login attempts"""
        if identifier not in self.login_attempts:
            return False
        
        attempts = self.login_attempts[identifier]
        recent_attempts = [
            attempt for attempt in attempts
            if datetime.now() - attempt < timedelta(minutes=self.lockout_duration_minutes)
        ]
        
        return len(recent_attempts) >= self.max_login_attempts
    
    def _record_login_attempt(self, identifier: str, success: bool):
        """Record login attempt"""
        if identifier not in self.login_attempts:
            self.login_attempts[identifier] = []
        
        if success:
            # Clear failed attempts on successful login
            self.login_attempts[identifier] = []
        else:
            # Record failed attempt
            self.login_attempts[identifier].append(datetime.now())
            
            # Clean old attempts
            cutoff_time = datetime.now() - timedelta(minutes=self.lockout_duration_minutes)
            self.login_attempts[identifier] = [
                attempt for attempt in self.login_attempts[identifier]
                if attempt > cutoff_time
            ]
    
    def register_user(self, username: str, email: str, password: str, 
                     role: str = "user") -> Dict[str, Any]:
        """
        Register a new user
        
        Args:
            username: Unique username
            email: User email address
            password: Plain text password
            role: User role (admin, editor, viewer, user)
        
        Returns:
            Dictionary with registration result
        """
        try:
            # Validate input
            if not username or not email or not password:
                return {
                    'success': False,
                    'error': 'Username, email, and password are required'
                }
            
            # Check if user already exists
            for user in self.users.values():
                if user.username == username:
                    return {
                        'success': False,
                        'error': 'Username already exists'
                    }
                if user.email == email:
                    return {
                        'success': False,
                        'error': 'Email already registered'
                    }
            
            # Generate user ID and hash password
            user_id = secrets.token_hex(16)
            password_hash, salt = self._hash_password(password)
            
            # Store salt with hash (in real implementation, use proper storage)
            full_hash = f"{password_hash}:{salt}"
            
            # Create user
            user = User(
                user_id=user_id,
                username=username,
                email=email,
                password_hash=full_hash,
                role=role
            )
            
            self.users[user_id] = user
            
            logger.info(f"User registered: {username} ({user_id})")
            
            return {
                'success': True,
                'user': user.to_dict(),
                'message': 'User registered successfully'
            }
            
        except Exception as e:
            logger.error(f"Registration error: {str(e)}")
            return {
                'success': False,
                'error': 'Registration failed'
            }
    
    def authenticate_user(self, username: str, password: str) -> Dict[str, Any]:
        """
        Authenticate user with username/password
        
        Args:
            username: Username or email
            password: Plain text password
        
        Returns:
            Dictionary with authentication result and tokens
        """
        try:
            # Check if account is locked
            if self._is_account_locked(username):
                return {
                    'success': False,
                    'error': 'Account temporarily locked due to failed login attempts'
                }
            
            # Find user by username or email
            user = None
            for u in self.users.values():
                if u.username == username or u.email == username:
                    user = u
                    break
            
            if not user or not user.is_active:
                self._record_login_attempt(username, False)
                return {
                    'success': False,
                    'error': 'Invalid credentials'
                }
            
            # Verify password
            if user.password_hash:
                hash_parts = user.password_hash.split(':')
                if len(hash_parts) == 2:
                    stored_hash, salt = hash_parts
                    if not self._verify_password(password, stored_hash, salt):
                        self._record_login_attempt(username, False)
                        return {
                            'success': False,
                            'error': 'Invalid credentials'
                        }
                else:
                    self._record_login_attempt(username, False)
                    return {
                        'success': False,
                        'error': 'Invalid credentials'
                    }
            
            # Update last login
            user.last_login = datetime.now()
            self._record_login_attempt(username, True)
            
            # Generate tokens
            access_token = self._generate_token(user.user_id, "access")
            refresh_token = self._generate_token(user.user_id, "refresh")
            
            # Create session
            session_id = secrets.token_hex(16)
            self.sessions[session_id] = {
                'user_id': user.user_id,
                'access_token': access_token.token,
                'refresh_token': refresh_token.token,
                'created_at': datetime.now(),
                'last_activity': datetime.now()
            }
            
            logger.info(f"User authenticated: {username} ({user.user_id})")
            
            return {
                'success': True,
                'user': user.to_dict(),
                'access_token': access_token.token,
                'refresh_token': refresh_token.token,
                'session_id': session_id,
                'expires_at': access_token.expires_at.isoformat()
            }
            
        except Exception as e:
            logger.error(f"Authentication error: {str(e)}")
            return {
                'success': False,
                'error': 'Authentication failed'
            }
    
    def validate_token(self, token: str) -> Dict[str, Any]:
        """
        Validate authentication token
        
        Args:
            token: Authentication token
        
        Returns:
            Dictionary with validation result and user info
        """
        try:
            if token not in self.tokens:
                return {
                    'valid': False,
                    'error': 'Invalid token'
                }
            
            auth_token = self.tokens[token]
            
            if auth_token.is_expired():
                # Clean up expired token
                del self.tokens[token]
                return {
                    'valid': False,
                    'error': 'Token expired'
                }
            
            # Get user
            user = self.users.get(auth_token.user_id)
            if not user or not user.is_active:
                return {
                    'valid': False,
                    'error': 'User not found or inactive'
                }
            
            return {
                'valid': True,
                'user': user.to_dict(),
                'token_type': auth_token.token_type
            }
            
        except Exception as e:
            logger.error(f"Token validation error: {str(e)}")
            return {
                'valid': False,
                'error': 'Token validation failed'
            }
    
    def refresh_token(self, refresh_token: str) -> Dict[str, Any]:
        """
        Refresh access token using refresh token
        
        Args:
            refresh_token: Refresh token
        
        Returns:
            Dictionary with new access token
        """
        try:
            validation_result = self.validate_token(refresh_token)
            
            if not validation_result['valid']:
                return {
                    'success': False,
                    'error': 'Invalid refresh token'
                }
            
            if validation_result.get('token_type') != 'refresh':
                return {
                    'success': False,
                    'error': 'Invalid token type'
                }
            
            user_id = None
            for token, auth_token in self.tokens.items():
                if token == refresh_token:
                    user_id = auth_token.user_id
                    break
            
            if not user_id:
                return {
                    'success': False,
                    'error': 'Token not found'
                }
            
            # Generate new access token
            new_access_token = self._generate_token(user_id, "access")
            
            return {
                'success': True,
                'access_token': new_access_token.token,
                'expires_at': new_access_token.expires_at.isoformat()
            }
            
        except Exception as e:
            logger.error(f"Token refresh error: {str(e)}")
            return {
                'success': False,
                'error': 'Token refresh failed'
            }
    
    def logout_user(self, token: str) -> Dict[str, Any]:
        """
        Logout user by invalidating token
        
        Args:
            token: Authentication token
        
        Returns:
            Dictionary with logout result
        """
        try:
            # Remove token
            if token in self.tokens:
                user_id = self.tokens[token].user_id
                del self.tokens[token]
                
                # Remove associated sessions
                sessions_to_remove = []
                for session_id, session in self.sessions.items():
                    if session.get('access_token') == token:
                        sessions_to_remove.append(session_id)
                
                for session_id in sessions_to_remove:
                    del self.sessions[session_id]
                
                logger.info(f"User logged out: {user_id}")
                
                return {
                    'success': True,
                    'message': 'Logged out successfully'
                }
            
            return {
                'success': False,
                'error': 'Token not found'
            }
            
        except Exception as e:
            logger.error(f"Logout error: {str(e)}")
            return {
                'success': False,
                'error': 'Logout failed'
            }
    
    def get_user_by_id(self, user_id: str) -> Optional[User]:
        """Get user by ID"""
        return self.users.get(user_id)
    
    def get_user_by_username(self, username: str) -> Optional[User]:
        """Get user by username"""
        for user in self.users.values():
            if user.username == username:
                return user
        return None
    
    def update_user_role(self, user_id: str, new_role: str, admin_token: str) -> Dict[str, Any]:
        """
        Update user role (admin only)
        
        Args:
            user_id: Target user ID
            new_role: New role to assign
            admin_token: Admin authentication token
        
        Returns:
            Dictionary with update result
        """
        try:
            # Validate admin token
            admin_validation = self.validate_token(admin_token)
            if not admin_validation['valid']:
                return {
                    'success': False,
                    'error': 'Invalid admin token'
                }
            
            admin_user = self.users.get(admin_validation['user']['user_id'])
            if not admin_user or admin_user.role != 'admin':
                return {
                    'success': False,
                    'error': 'Admin privileges required'
                }
            
            # Update user role
            target_user = self.users.get(user_id)
            if not target_user:
                return {
                    'success': False,
                    'error': 'User not found'
                }
            
            old_role = target_user.role
            target_user.role = new_role
            
            logger.info(f"User role updated: {target_user.username} from {old_role} to {new_role}")
            
            return {
                'success': True,
                'user': target_user.to_dict(),
                'message': f'Role updated from {old_role} to {new_role}'
            }
            
        except Exception as e:
            logger.error(f"Role update error: {str(e)}")
            return {
                'success': False,
                'error': 'Role update failed'
            }
    
    def list_users(self, admin_token: str) -> Dict[str, Any]:
        """
        List all users (admin only)
        
        Args:
            admin_token: Admin authentication token
        
        Returns:
            Dictionary with user list
        """
        try:
            # Validate admin token
            admin_validation = self.validate_token(admin_token)
            if not admin_validation['valid']:
                return {
                    'success': False,
                    'error': 'Invalid admin token'
                }
            
            admin_user = self.users.get(admin_validation['user']['user_id'])
            if not admin_user or admin_user.role != 'admin':
                return {
                    'success': False,
                    'error': 'Admin privileges required'
                }
            
            users_list = [user.to_dict() for user in self.users.values()]
            
            return {
                'success': True,
                'users': users_list,
                'count': len(users_list)
            }
            
        except Exception as e:
            logger.error(f"List users error: {str(e)}")
            return {
                'success': False,
                'error': 'Failed to list users'
            }
    
    def cleanup_expired_tokens(self):
        """Clean up expired tokens and sessions"""
        try:
            # Clean expired tokens
            expired_tokens = []
            for token, auth_token in self.tokens.items():
                if auth_token.is_expired():
                    expired_tokens.append(token)
            
            for token in expired_tokens:
                del self.tokens[token]
            
            # Clean expired sessions
            expired_sessions = []
            for session_id, session in self.sessions.items():
                if session.get('access_token') in expired_tokens:
                    expired_sessions.append(session_id)
            
            for session_id in expired_sessions:
                del self.sessions[session_id]
            
            if expired_tokens:
                logger.info(f"Cleaned up {len(expired_tokens)} expired tokens")
                
        except Exception as e:
            logger.error(f"Token cleanup error: {str(e)}")
    
    def get_active_sessions(self, admin_token: str) -> Dict[str, Any]:
        """
        Get active sessions (admin only)
        
        Args:
            admin_token: Admin authentication token
        
        Returns:
            Dictionary with active sessions
        """
        try:
            # Validate admin token
            admin_validation = self.validate_token(admin_token)
            if not admin_validation['valid']:
                return {
                    'success': False,
                    'error': 'Invalid admin token'
                }
            
            admin_user = self.users.get(admin_validation['user']['user_id'])
            if not admin_user or admin_user.role != 'admin':
                return {
                    'success': False,
                    'error': 'Admin privileges required'
                }
            
            sessions_info = []
            for session_id, session in self.sessions.items():
                user = self.users.get(session['user_id'])
                if user:
                    sessions_info.append({
                        'session_id': session_id,
                        'user': user.to_dict(),
                        'created_at': session['created_at'].isoformat(),
                        'last_activity': session['last_activity'].isoformat()
                    })
            
            return {
                'success': True,
                'sessions': sessions_info,
                'count': len(sessions_info)
            }
            
        except Exception as e:
            logger.error(f"Get sessions error: {str(e)}")
            return {
                'success': False,
                'error': 'Failed to get sessions'
            }