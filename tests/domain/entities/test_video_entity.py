"""
Unit tests for VideoEntity
"""
import pytest
from datetime import datetime
from pydantic import ValidationError
from src.domain.entities.video_entity import VideoEntity


class TestVideoEntity:
    """Test cases for VideoEntity"""
    
    def test_create_video_entity_with_all_fields(self):
        """Test creating video entity with all fields"""
        video = VideoEntity(
            video_id="video-123",
            user_id="user-456",
            data_video_up=datetime(2023, 1, 1, 12, 0, 0),
            status=1,
            video_name="test_video.mp4",
            zip_name="test_video.zip",
            descricao="Test description",
            titulo="Test Title",
            metadados={"duration": 120, "format": "mp4"},
            path="videos/test_video.mp4"
        )
        
        assert video.video_id == "video-123"
        assert video.user_id == "user-456"
        assert video.status == 1
        assert video.video_name == "test_video.mp4"
        assert video.zip_name == "test_video.zip"
        assert video.descricao == "Test description"
        assert video.titulo == "Test Title"
        assert video.metadados == {"duration": 120, "format": "mp4"}
        assert video.path == "videos/test_video.mp4"
    
    def test_create_video_entity_with_required_fields_only(self):
        """Test creating video entity with only required fields"""
        video = VideoEntity(
            video_id="video-123",
            user_id="user-456",
            data_video_up=datetime(2023, 1, 1, 12, 0, 0),
            status=1
        )
        
        assert video.video_id == "video-123"
        assert video.user_id == "user-456"
        assert video.status == 1
        assert video.video_name is None
        assert video.zip_name is None
        assert video.descricao is None
        assert video.titulo is None
        assert video.metadados is None
        assert video.path is None
    
    def test_video_entity_missing_required_field(self):
        """Test that missing required fields raise ValidationError"""
        with pytest.raises(ValidationError):
            VideoEntity(
                video_id="video-123",
                user_id="user-456",
                data_video_up=datetime(2023, 1, 1, 12, 0, 0)
                # Missing status
            )
    
    def test_video_entity_invalid_status_type(self):
        """Test that invalid status type raises ValidationError"""
        with pytest.raises(ValidationError):
            VideoEntity(
                video_id="video-123",
                user_id="user-456",
                data_video_up=datetime(2023, 1, 1, 12, 0, 0),
                status="invalid"  # Should be int
            )
    
    def test_video_entity_status_values(self):
        """Test different status values"""
        for status in [1, 2, 3, 4]:
            video = VideoEntity(
                video_id="video-123",
                user_id="user-456",
                data_video_up=datetime(2023, 1, 1, 12, 0, 0),
                status=status
            )
            assert video.status == status
    
    def test_video_entity_dict_conversion(self):
        """Test converting video entity to dict"""
        video = VideoEntity(
            video_id="video-123",
            user_id="user-456",
            data_video_up=datetime(2023, 1, 1, 12, 0, 0),
            status=1,
            video_name="test.mp4"
        )
        
        video_dict = video.model_dump()
        assert video_dict['video_id'] == "video-123"
        assert video_dict['user_id'] == "user-456"
        assert video_dict['status'] == 1
        assert video_dict['video_name'] == "test.mp4"
    
    def test_video_entity_json_serialization(self):
        """Test JSON serialization of video entity"""
        video = VideoEntity(
            video_id="video-123",
            user_id="user-456",
            data_video_up=datetime(2023, 1, 1, 12, 0, 0),
            status=1,
            metadados={"key": "value"}
        )
        
        json_str = video.model_dump_json()
        assert "video-123" in json_str
        assert "user-456" in json_str
    
    def test_video_entity_update_fields(self):
        """Test updating video entity fields"""
        video = VideoEntity(
            video_id="video-123",
            user_id="user-456",
            data_video_up=datetime(2023, 1, 1, 12, 0, 0),
            status=1
        )
        
        # Pydantic models are immutable by default, use model_copy
        updated_video = video.model_copy(update={"status": 2, "zip_name": "new.zip"})
        
        assert updated_video.status == 2
        assert updated_video.zip_name == "new.zip"
        assert updated_video.video_id == "video-123"
