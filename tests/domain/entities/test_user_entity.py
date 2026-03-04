"""
Unit tests for UserEntity
"""
import pytest
from datetime import datetime
from pydantic import ValidationError
from src.domain.entities.user_entity import UserEntity


class TestUserEntity:
    """Test cases for UserEntity"""
    
    def test_create_user_entity_with_all_fields(self):
        """Test creating user entity with all fields"""
        user = UserEntity(
            user_id="user-123",
            name="John Doe",
            email="john.doe@example.com",
            password_hash="hashed_password",
            created_at=datetime(2023, 1, 1, 10, 0, 0)
        )
        
        assert user.user_id == "user-123"
        assert user.name == "John Doe"
        assert user.email == "john.doe@example.com"
        assert user.password_hash == "hashed_password"
        assert user.created_at == datetime(2023, 1, 1, 10, 0, 0)
    
    def test_create_user_entity_without_name(self):
        """Test creating user entity without optional name field"""
        user = UserEntity(
            user_id="user-123",
            email="john.doe@example.com",
            password_hash="hashed_password",
            created_at=datetime(2023, 1, 1, 10, 0, 0)
        )
        
        assert user.user_id == "user-123"
        assert user.name is None
        assert user.email == "john.doe@example.com"
    
    def test_user_entity_missing_required_field(self):
        """Test that missing required fields raise ValidationError"""
        with pytest.raises(ValidationError):
            UserEntity(
                user_id="user-123",
                email="john.doe@example.com",
                created_at=datetime(2023, 1, 1, 10, 0, 0)
                # Missing password_hash
            )
    
    def test_user_entity_invalid_email(self):
        """Test that invalid email raises ValidationError"""
        with pytest.raises(ValidationError):
            UserEntity(
                user_id="user-123",
                email="invalid-email",  # Invalid email format
                password_hash="hashed_password",
                created_at=datetime(2023, 1, 1, 10, 0, 0)
            )
    
    def test_user_entity_valid_email_formats(self):
        """Test various valid email formats"""
        valid_emails = [
            "user@example.com",
            "user.name@example.com",
            "user+tag@example.co.uk",
            "user123@test-domain.com"
        ]
        
        for email in valid_emails:
            user = UserEntity(
                user_id="user-123",
                email=email,
                password_hash="hashed_password",
                created_at=datetime(2023, 1, 1, 10, 0, 0)
            )
            assert user.email == email
    
    def test_user_entity_dict_conversion(self):
        """Test converting user entity to dict"""
        user = UserEntity(
            user_id="user-123",
            name="John Doe",
            email="john.doe@example.com",
            password_hash="hashed_password",
            created_at=datetime(2023, 1, 1, 10, 0, 0)
        )
        
        user_dict = user.model_dump()
        assert user_dict['user_id'] == "user-123"
        assert user_dict['name'] == "John Doe"
        assert user_dict['email'] == "john.doe@example.com"
        assert user_dict['password_hash'] == "hashed_password"
    
    def test_user_entity_json_serialization(self):
        """Test JSON serialization of user entity"""
        user = UserEntity(
            user_id="user-123",
            name="John Doe",
            email="john.doe@example.com",
            password_hash="hashed_password",
            created_at=datetime(2023, 1, 1, 10, 0, 0)
        )
        
        json_str = user.model_dump_json()
        assert "user-123" in json_str
        assert "john.doe@example.com" in json_str
        assert "John Doe" in json_str
    
    def test_user_entity_update_fields(self):
        """Test updating user entity fields"""
        user = UserEntity(
            user_id="user-123",
            name="John Doe",
            email="john.doe@example.com",
            password_hash="hashed_password",
            created_at=datetime(2023, 1, 1, 10, 0, 0)
        )
        
        # Pydantic models are immutable by default, use model_copy
        updated_user = user.model_copy(update={"name": "Jane Doe"})
        
        assert updated_user.name == "Jane Doe"
        assert updated_user.user_id == "user-123"
        assert updated_user.email == "john.doe@example.com"
    
    def test_user_entity_empty_password_hash(self):
        """Test that empty password_hash is accepted (validation could be added)"""
        user = UserEntity(
            user_id="user-123",
            email="john.doe@example.com",
            password_hash="",
            created_at=datetime(2023, 1, 1, 10, 0, 0)
        )
        
        assert user.password_hash == ""
