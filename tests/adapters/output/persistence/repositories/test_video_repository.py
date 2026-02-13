"""
Unit tests for VideoRepository
"""
import pytest
from unittest.mock import Mock, MagicMock, patch
from datetime import datetime
from src.adapters.output.persistence.repositories.video_repository import VideoRepository
from src.domain.entities.video_entity import VideoEntity
from src.domain.entities.user_entity import UserEntity


class TestVideoRepository:
    """Test cases for VideoRepository"""
    
    @pytest.fixture
    def mock_db_connection(self):
        """Mock database connection"""
        return MagicMock()
    
    @pytest.fixture
    def repository(self, mock_db_connection):
        """Create repository instance"""
        return VideoRepository(mock_db_connection)
    
    def test_repository_initialization(self, repository, mock_db_connection):
        """Test repository initialization"""
        assert repository is not None
        assert repository.db_connection == mock_db_connection
    
    def test_get_video_with_user_success(self, repository, mock_db_connection):
        """Test successful get video with user"""
        # Setup mock cursor
        mock_cursor = MagicMock()
        mock_cursor.fetchone.return_value = {
            'video_id': 'video-123',
            'user_id': 'user-456',
            'data_video_up': datetime(2023, 1, 1),
            'status': 1,
            'video_name': 'test.mp4',
            'zip_name': None,
            'descricao': 'Test desc',
            'titulo': 'Test Title',
            'metadados': {'key': 'value'},
            'u_user_id': 'user-456',
            'name': 'Test User',
            'email': 'test@example.com',
            'password_hash': 'hashed',
            'created_at': datetime(2023, 1, 1)
        }
        
        mock_connection = MagicMock()
        mock_connection.autocommit = False
        mock_connection.cursor.return_value = mock_cursor
        mock_db_connection.get_connection.return_value = mock_connection
        
        # Execute
        result = repository.get_video_with_user('video-123')
        
        # Assertions
        assert result is not None
        video, user = result
        
        assert isinstance(video, VideoEntity)
        assert video.video_id == 'video-123'
        assert video.user_id == 'user-456'
        assert video.status == 1
        
        assert isinstance(user, UserEntity)
        assert user.user_id == 'user-456'
        assert user.name == 'Test User'
        assert user.email == 'test@example.com'
        
        mock_cursor.execute.assert_called_once()
        mock_cursor.close.assert_called_once()
    
    def test_get_video_with_user_not_found(self, repository, mock_db_connection):
        """Test get video with user when video not found"""
        mock_cursor = MagicMock()
        mock_cursor.fetchone.return_value = None
        
        mock_connection = MagicMock()
        mock_connection.autocommit = False
        mock_connection.cursor.return_value = mock_cursor
        mock_db_connection.get_connection.return_value = mock_connection
        
        result = repository.get_video_with_user('nonexistent-video')
        
        assert result is None
        mock_cursor.close.assert_called_once()
    
    def test_get_video_with_user_exception(self, repository, mock_db_connection):
        """Test get video with user handles exceptions"""
        mock_cursor = MagicMock()
        mock_cursor.execute.side_effect = Exception("Database error")
        
        mock_connection = MagicMock()
        mock_connection.autocommit = False
        mock_connection.cursor.return_value = mock_cursor
        mock_db_connection.get_connection.return_value = mock_connection
        
        result = repository.get_video_with_user('video-123')
        
        assert result is None
        mock_db_connection.rollback.assert_called_once()
        mock_cursor.close.assert_called_once()
    
    def test_update_video_status_success(self, repository, mock_db_connection):
        """Test successful video status update"""
        mock_cursor = MagicMock()
        mock_connection = MagicMock()
        mock_connection.cursor.return_value = mock_cursor
        mock_db_connection.get_connection.return_value = mock_connection
        
        result = repository.update_video_status('video-123', 2)
        
        assert result is True
        mock_cursor.execute.assert_called_once()
        mock_connection.commit.assert_called_once()
        mock_cursor.close.assert_called_once()
    
    def test_update_video_status_with_zip_name(self, repository, mock_db_connection):
        """Test video status update with zip_name"""
        mock_cursor = MagicMock()
        mock_connection = MagicMock()
        mock_connection.cursor.return_value = mock_cursor
        mock_db_connection.get_connection.return_value = mock_connection
        
        result = repository.update_video_status('video-123', 3, 'test.zip')
        
        assert result is True
        
        # Verify correct SQL was used (with zip_name)
        call_args = mock_cursor.execute.call_args
        sql = call_args[0][0]
        assert 'zip_name' in sql
        assert call_args[0][1] == (3, 'test.zip', 'video-123')
        
        mock_connection.commit.assert_called_once()
        mock_cursor.close.assert_called_once()
    
    def test_update_video_status_exception(self, repository, mock_db_connection):
        """Test update video status handles exceptions"""
        mock_cursor = MagicMock()
        mock_cursor.execute.side_effect = Exception("Update error")
        
        mock_connection = MagicMock()
        mock_connection.cursor.return_value = mock_cursor
        mock_db_connection.get_connection.return_value = mock_connection
        
        result = repository.update_video_status('video-123', 2)
        
        assert result is False
        mock_db_connection.rollback.assert_called_once()
        mock_cursor.close.assert_called_once()
    
    def test_update_video_status_all_statuses(self, repository, mock_db_connection):
        """Test updating to different status values"""
        mock_cursor = MagicMock()
        mock_connection = MagicMock()
        mock_connection.cursor.return_value = mock_cursor
        mock_db_connection.get_connection.return_value = mock_connection
        
        statuses = [1, 2, 3, 4]  # aguardando, processando, finalizado, erro
        
        for status in statuses:
            result = repository.update_video_status('video-123', status)
            assert result is True
        
        assert mock_cursor.execute.call_count == len(statuses)
    
    def test_get_video_with_user_cursor_cleanup_on_exception(self, repository, mock_db_connection):
        """Test cursor is properly closed even when exception occurs"""
        mock_cursor = MagicMock()
        mock_cursor.fetchone.side_effect = Exception("Fetch error")
        
        mock_connection = MagicMock()
        mock_connection.autocommit = False
        mock_connection.cursor.return_value = mock_cursor
        mock_db_connection.get_connection.return_value = mock_connection
        
        result = repository.get_video_with_user('video-123')
        
        assert result is None
        # Cursor should be closed despite exception
        mock_cursor.close.assert_called_once()
