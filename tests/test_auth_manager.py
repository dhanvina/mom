"""
Unit tests for AuthManager
"""

import pytest
from datetime import datetime, timedelta
import time

from app.auth.auth_manager import AuthManager, User, AuthToken


class TestAuthManager:
    """Test cases for AuthManager"""
    
    def setup_method(self):
        """Set up test fixtures"""
        self.auth_manager = AuthManager({
            'token_expiry_hours': 1,
            'refresh_token_expiry_days': 7,
            'max_login_attempts': 3,
            'lockout_duration_minutes': 5
        })
    
    def test_user_registration_success(self):
        """Test successful user registration"""
        result = self.auth_manager.register_user(
            username="testuser",
            email="test@example.com",
            password="password123",
            role="user"
        )
        
        assert result['success'] is True
        assert 'user' in result
        assert result['user']['username'] == "testuser"
        assert result['user']['email'] == "test@example.com"
        assert result['user']['role'] == "user"
        assert 'user_id' in result['user']
    
    def test_user_registration_duplicate_username(self):
        """Test registration with duplicate username"""
        # Register first user
        self.auth_manager.register_user(
            username="testuser",
            email="test1@example.com",
            password="password123"
        )
        
        # Try to register with same username
        result = self.auth_manager.register_user(
            username="testuser",
            email="test2@example.com",
            password="password456"
        )
        
        assert result['success'] is False
        assert "Username already exists" in result['error']
    
    def test_user_registration_duplicate_email(self):
        """Test registration with duplicate email"""
        # Register first user
        self.auth_manager.register_user(
            username="testuser1",
            email="test@example.com",
            password="password123"
        )
        
        # Try to register with same email
        result = self.auth_manager.register_user(
            username="testuser2",
            email="test@example.com",
            password="password456"
        )
        
        assert result['success'] is False
        assert "Email already registered" in result['error']
    
    def test_user_registration_missing_fields(self):
        """Test registration with missing required fields"""
        result = self.auth_manager.register_user(
            username="",
            email="test@example.com",
            password="password123"
        )
        
        assert result['success'] is False
        assert "required" in result['error']
    
    def test_user_authentication_success(self):
        """Test successful user authentication"""
        # Register user first
        self.auth_manager.register_user(
            username="testuser",
            email="test@example.com",
            password="password123"
        )
        
        # Authenticate user
        result = self.auth_manager.authenticate_user("testuser", "password123")
        
        assert result['success'] is True
        assert 'user' in result
        assert 'access_token' in result
        assert 'refresh_token' in result
        assert 'session_id' in result
        assert result['user']['username'] == "testuser"
    
    def test_user_authentication_with_email(self):
        """Test authentication using email instead of username"""
        # Register user first
        self.auth_manager.register_user(
            username="testuser",
            email="test@example.com",
            password="password123"
        )
        
        # Authenticate with email
        result = self.auth_manager.authenticate_user("test@example.com", "password123")
        
        assert result['success'] is True
        assert result['user']['username'] == "testuser"
    
    def test_user_authentication_invalid_credentials(self):
        """Test authentication with invalid credentials"""
        # Register user first
        self.auth_manager.register_user(
            username="testuser",
            email="test@example.com",
            password="password123"
        )
        
        # Try with wrong password
        result = self.auth_manager.authenticate_user("testuser", "wrongpassword")
        
        assert result['success'] is False
        assert "Invalid credentials" in result['error']
    
    def test_user_authentication_nonexistent_user(self):
        """Test authentication with non-existent user"""
        result = self.auth_manager.authenticate_user("nonexistent", "password123")
        
        assert result['success'] is False
        assert "Invalid credentials" in result['error']
    
    def test_account_lockout_after_failed_attempts(self):
        """Test account lockout after multiple failed login attempts"""
        # Register user first
        self.auth_manager.register_user(
            username="testuser",
            email="test@example.com",
            password="password123"
        )
        
        # Make multiple failed attempts
        for _ in range(3):
            result = self.auth_manager.authenticate_user("testuser", "wrongpassword")
            assert result['success'] is False
        
        # Next attempt should be locked
        result = self.auth_manager.authenticate_user("testuser", "password123")
        assert result['success'] is False
        assert "locked" in result['error']
    
    def test_token_validation_success(self):
        """Test successful token validation"""
        # Register and authenticate user
        self.auth_manager.register_user(
            username="testuser",
            email="test@example.com",
            password="password123"
        )
        
        auth_result = self.auth_manager.authenticate_user("testuser", "password123")
        token = auth_result['access_token']
        
        # Validate token
        result = self.auth_manager.validate_token(token)
        
        assert result['valid'] is True
        assert 'user' in result
        assert result['user']['username'] == "testuser"
    
    def test_token_validation_invalid_token(self):
        """Test validation with invalid token"""
        result = self.auth_manager.validate_token("invalid_token")
        
        assert result['valid'] is False
        assert "Invalid token" in result['error']
    
    def test_token_refresh_success(self):
        """Test successful token refresh"""
        # Register and authenticate user
        self.auth_manager.register_user(
            username="testuser",
            email="test@example.com",
            password="password123"
        )
        
        auth_result = self.auth_manager.authenticate_user("testuser", "password123")
        refresh_token = auth_result['refresh_token']
        
        # Refresh token
        result = self.auth_manager.refresh_token(refresh_token)
        
        assert result['success'] is True
        assert 'access_token' in result
        assert 'expires_at' in result
    
    def test_token_refresh_invalid_token(self):
        """Test token refresh with invalid token"""
        result = self.auth_manager.refresh_token("invalid_token")
        
        assert result['success'] is False
        assert "Invalid refresh token" in result['error']
    
    def test_user_logout_success(self):
        """Test successful user logout"""
        # Register and authenticate user
        self.auth_manager.register_user(
            username="testuser",
            email="test@example.com",
            password="password123"
        )
        
        auth_result = self.auth_manager.authenticate_user("testuser", "password123")
        token = auth_result['access_token']
        
        # Logout user
        result = self.auth_manager.logout_user(token)
        
        assert result['success'] is True
        
        # Token should now be invalid
        validation_result = self.auth_manager.validate_token(token)
        assert validation_result['valid'] is False
    
    def test_get_user_by_id(self):
        """Test getting user by ID"""
        # Register user
        reg_result = self.auth_manager.register_user(
            username="testuser",
            email="test@example.com",
            password="password123"
        )
        
        user_id = reg_result['user']['user_id']
        user = self.auth_manager.get_user_by_id(user_id)
        
        assert user is not None
        assert user.username == "testuser"
        assert user.email == "test@example.com"
    
    def test_get_user_by_username(self):
        """Test getting user by username"""
        # Register user
        self.auth_manager.register_user(
            username="testuser",
            email="test@example.com",
            password="password123"
        )
        
        user = self.auth_manager.get_user_by_username("testuser")
        
        assert user is not None
        assert user.username == "testuser"
        assert user.email == "test@example.com"
    
    def test_update_user_role_success(self):
        """Test successful user role update by admin"""
        # Register admin user
        admin_reg = self.auth_manager.register_user(
            username="admin",
            email="admin@example.com",
            password="adminpass",
            role="admin"
        )
        
        # Register regular user
        user_reg = self.auth_manager.register_user(
            username="testuser",
            email="test@example.com",
            password="password123"
        )
        
        # Authenticate admin
        admin_auth = self.auth_manager.authenticate_user("admin", "adminpass")
        admin_token = admin_auth['access_token']
        
        # Update user role
        result = self.auth_manager.update_user_role(
            user_reg['user']['user_id'],
            "editor",
            admin_token
        )
        
        assert result['success'] is True
        assert result['user']['role'] == "editor"
    
    def test_update_user_role_non_admin(self):
        """Test user role update by non-admin user"""
        # Register two regular users
        user1_reg = self.auth_manager.register_user(
            username="user1",
            email="user1@example.com",
            password="password123"
        )
        
        user2_reg = self.auth_manager.register_user(
            username="user2",
            email="user2@example.com",
            password="password123"
        )
        
        # Authenticate first user
        user1_auth = self.auth_manager.authenticate_user("user1", "password123")
        user1_token = user1_auth['access_token']
        
        # Try to update second user's role
        result = self.auth_manager.update_user_role(
            user2_reg['user']['user_id'],
            "editor",
            user1_token
        )
        
        assert result['success'] is False
        assert "Admin privileges required" in result['error']
    
    def test_list_users_admin(self):
        """Test listing users by admin"""
        # Register admin user
        self.auth_manager.register_user(
            username="admin",
            email="admin@example.com",
            password="adminpass",
            role="admin"
        )
        
        # Register regular users
        self.auth_manager.register_user(
            username="user1",
            email="user1@example.com",
            password="password123"
        )
        
        self.auth_manager.register_user(
            username="user2",
            email="user2@example.com",
            password="password123"
        )
        
        # Authenticate admin
        admin_auth = self.auth_manager.authenticate_user("admin", "adminpass")
        admin_token = admin_auth['access_token']
        
        # List users
        result = self.auth_manager.list_users(admin_token)
        
        assert result['success'] is True
        assert 'users' in result
        assert result['count'] == 3  # admin + 2 regular users
    
    def test_list_users_non_admin(self):
        """Test listing users by non-admin user"""
        # Register regular user
        self.auth_manager.register_user(
            username="user1",
            email="user1@example.com",
            password="password123"
        )
        
        # Authenticate user
        user_auth = self.auth_manager.authenticate_user("user1", "password123")
        user_token = user_auth['access_token']
        
        # Try to list users
        result = self.auth_manager.list_users(user_token)
        
        assert result['success'] is False
        assert "Admin privileges required" in result['error']
    
    def test_cleanup_expired_tokens(self):
        """Test cleanup of expired tokens"""
        # Register and authenticate user
        self.auth_manager.register_user(
            username="testuser",
            email="test@example.com",
            password="password123"
        )
        
        auth_result = self.auth_manager.authenticate_user("testuser", "password123")
        token = auth_result['access_token']
        
        # Manually expire the token
        if token in self.auth_manager.tokens:
            self.auth_manager.tokens[token].expires_at = datetime.now() - timedelta(hours=1)
        
        # Run cleanup
        self.auth_manager.cleanup_expired_tokens()
        
        # Token should be removed
        assert token not in self.auth_manager.tokens
    
    def test_get_active_sessions_admin(self):
        """Test getting active sessions by admin"""
        # Register admin user
        self.auth_manager.register_user(
            username="admin",
            email="admin@example.com",
            password="adminpass",
            role="admin"
        )
        
        # Register and authenticate regular user
        self.auth_manager.register_user(
            username="user1",
            email="user1@example.com",
            password="password123"
        )
        
        self.auth_manager.authenticate_user("user1", "password123")
        
        # Authenticate admin
        admin_auth = self.auth_manager.authenticate_user("admin", "adminpass")
        admin_token = admin_auth['access_token']
        
        # Get active sessions
        result = self.auth_manager.get_active_sessions(admin_token)
        
        assert result['success'] is True
        assert 'sessions' in result
        assert result['count'] >= 2  # admin + user1 sessions


class TestUser:
    """Test cases for User model"""
    
    def test_user_creation(self):
        """Test user creation"""
        user = User(
            user_id="test123",
            username="testuser",
            email="test@example.com",
            role="user"
        )
        
        assert user.user_id == "test123"
        assert user.username == "testuser"
        assert user.email == "test@example.com"
        assert user.role == "user"
        assert user.is_active is True
    
    def test_user_to_dict(self):
        """Test user to dictionary conversion"""
        user = User(
            user_id="test123",
            username="testuser",
            email="test@example.com",
            role="user"
        )
        
        user_dict = user.to_dict()
        
        assert user_dict['user_id'] == "test123"
        assert user_dict['username'] == "testuser"
        assert user_dict['email'] == "test@example.com"
        assert user_dict['role'] == "user"
        assert user_dict['is_active'] is True
        assert 'password_hash' not in user_dict  # Should not include sensitive data
    
    def test_user_from_dict(self):
        """Test user creation from dictionary"""
        user_data = {
            'user_id': 'test123',
            'username': 'testuser',
            'email': 'test@example.com',
            'role': 'user',
            'is_active': True
        }
        
        user = User.from_dict(user_data)
        
        assert user.user_id == "test123"
        assert user.username == "testuser"
        assert user.email == "test@example.com"
        assert user.role == "user"
        assert user.is_active is True


class TestAuthToken:
    """Test cases for AuthToken model"""
    
    def test_token_creation(self):
        """Test token creation"""
        expires_at = datetime.now() + timedelta(hours=1)
        token = AuthToken(
            token="test_token",
            user_id="user123",
            expires_at=expires_at,
            token_type="access"
        )
        
        assert token.token == "test_token"
        assert token.user_id == "user123"
        assert token.expires_at == expires_at
        assert token.token_type == "access"
    
    def test_token_expiry_check(self):
        """Test token expiry checking"""
        # Create expired token
        expired_token = AuthToken(
            token="expired_token",
            user_id="user123",
            expires_at=datetime.now() - timedelta(hours=1),
            token_type="access"
        )
        
        # Create valid token
        valid_token = AuthToken(
            token="valid_token",
            user_id="user123",
            expires_at=datetime.now() + timedelta(hours=1),
            token_type="access"
        )
        
        assert expired_token.is_expired() is True
        assert valid_token.is_expired() is False
    
    def test_token_to_dict(self):
        """Test token to dictionary conversion"""
        expires_at = datetime.now() + timedelta(hours=1)
        token = AuthToken(
            token="test_token",
            user_id="user123",
            expires_at=expires_at,
            token_type="access"
        )
        
        token_dict = token.to_dict()
        
        assert token_dict['token'] == "test_token"
        assert token_dict['user_id'] == "user123"
        assert token_dict['token_type'] == "access"
        assert 'expires_at' in token_dict
        assert 'created_at' in token_dict