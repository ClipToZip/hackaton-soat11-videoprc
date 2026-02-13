"""
Unit tests for ProcessVideoUseCase
"""
import pytest
from unittest.mock import Mock, patch, MagicMock, call
from datetime import datetime
from src.application.use_cases.process_video_use_case import ProcessVideoUseCase
from src.domain.entities.video_entity import VideoEntity
from src.domain.entities.user_entity import UserEntity


class TestProcessVideoUseCase:
    """Test cases for ProcessVideoUseCase"""
    
    @pytest.fixture
    def mock_video_service(self):
        """Mock video service"""
        service = Mock()
        service.extract_frames = Mock(return_value=['/tmp/frame_001.jpg', '/tmp/frame_002.jpg'])
        service.cleanup_files = Mock()
        return service
    
    @pytest.fixture
    def use_case(self, mock_storage, mock_message_producer, mock_video_service, mock_repository):
        """Create use case instance with mocked dependencies"""
        return ProcessVideoUseCase(
            storage=mock_storage,
            message_producer=mock_message_producer,
            video_service=mock_video_service,
            repository=mock_repository
        )
    
    @pytest.fixture
    def video_entity(self):
        """Sample video entity"""
        return VideoEntity(
            video_id="test-video-123",
            user_id="test-user-456",
            data_video_up=datetime(2023, 1, 1),
            status=1,
            video_name="test_video.mp4",
            titulo="Test Video"
        )
    
    @pytest.fixture
    def user_entity(self):
        """Sample user entity"""
        return UserEntity(
            user_id="test-user-456",
            name="Test User",
            email="test@example.com",
            password_hash="hashed",
            created_at=datetime(2023, 1, 1)
        )
    
    def test_use_case_initialization(self, use_case):
        """Test use case initialization"""
        assert use_case is not None
        assert use_case.storage is not None
        assert use_case.message_producer is not None
        assert use_case.video_service is not None
        assert use_case.repository is not None
    
    @patch('src.application.use_cases.process_video_use_case.tempfile.mkstemp')
    @patch('src.application.use_cases.process_video_use_case.zipfile.ZipFile')
    @patch('src.application.use_cases.process_video_use_case.os.fdopen')
    @patch('src.application.use_cases.process_video_use_case.os.close')
    @patch('src.application.use_cases.process_video_use_case.os.remove')
    @patch('src.application.use_cases.process_video_use_case.os.path.exists')
    def test_execute_success(
        self, 
        mock_exists,
        mock_remove,
        mock_close,
        mock_fdopen,
        mock_zipfile,
        mock_mkstemp,
        use_case, 
        mock_repository, 
        video_entity, 
        user_entity,
        mock_storage,
        mock_message_producer,
        mock_video_service
    ):
        """Test successful video processing"""
        # Setup mocks
        mock_repository.get_video_with_user.return_value = (video_entity, user_entity)
        mock_repository.update_video_status.return_value = True
        mock_mkstemp.side_effect = [(1, '/tmp/video.mp4'), (2, '/tmp/output.zip')]
        mock_fdopen.return_value.__enter__ = Mock()
        mock_fdopen.return_value.__exit__ = Mock()
        mock_fdopen.return_value.write = Mock()
        mock_exists.return_value = True
        mock_storage.upload_file.return_value = True
        mock_message_producer.send_message.return_value = True
        mock_video_service.extract_frames.return_value = ['/tmp/frame1.jpg', '/tmp/frame2.jpg']
        
        # Mock zipfile
        mock_zip = MagicMock()
        mock_zipfile.return_value.__enter__.return_value = mock_zip
        
        # Execute
        result = use_case.execute("test-video-123", b"video content", "https://queue.url")
        
        # Assertions
        assert result is True
        mock_repository.get_video_with_user.assert_called_once_with("test-video-123")
        assert mock_repository.update_video_status.call_count == 2  # Status 2 and 3
        mock_storage.upload_file.assert_called_once()
        mock_message_producer.send_message.assert_called_once()
    
    def test_execute_video_not_found(self, use_case, mock_repository):
        """Test execution when video not found"""
        mock_repository.get_video_with_user.return_value = None
        
        result = use_case.execute("nonexistent-video", b"content", "https://queue.url")
        
        assert result is False
        mock_repository.get_video_with_user.assert_called_once_with("nonexistent-video")
    
    def test_execute_invalid_status(self, use_case, mock_repository, video_entity, user_entity):
        """Test execution when video has invalid status"""
        video_entity.status = 3  # Not status 1
        mock_repository.get_video_with_user.return_value = (video_entity, user_entity)
        
        result = use_case.execute("test-video-123", b"content", "https://queue.url")
        
        assert result is False
    
    def test_execute_update_status_fails(self, use_case, mock_repository, video_entity, user_entity):
        """Test execution when status update fails"""
        mock_repository.get_video_with_user.return_value = (video_entity, user_entity)
        mock_repository.update_video_status.return_value = False
        
        result = use_case.execute("test-video-123", b"content", "https://queue.url")
        
        assert result is False
    
    @patch('src.application.use_cases.process_video_use_case.tempfile.mkstemp')
    @patch('src.application.use_cases.process_video_use_case.os.fdopen')
    def test_execute_save_temp_video_fails(
        self,
        mock_fdopen,
        mock_mkstemp,
        use_case, 
        mock_repository, 
        video_entity, 
        user_entity
    ):
        """Test execution when saving temp video fails"""
        mock_repository.get_video_with_user.return_value = (video_entity, user_entity)
        mock_repository.update_video_status.return_value = True
        mock_mkstemp.side_effect = Exception("File error")
        
        result = use_case.execute("test-video-123", b"content", "https://queue.url")
        
        assert result is False
        # Should update status to error (4)
        calls = mock_repository.update_video_status.call_args_list
        assert any(call_args[0][1] == 4 for call_args in calls)
    
    @patch('src.application.use_cases.process_video_use_case.tempfile.mkstemp')
    @patch('src.application.use_cases.process_video_use_case.os.fdopen')
    @patch('src.application.use_cases.process_video_use_case.os.path.exists')
    @patch('src.application.use_cases.process_video_use_case.os.remove')
    def test_execute_no_frames_extracted(
        self,
        mock_remove,
        mock_exists,
        mock_fdopen,
        mock_mkstemp,
        use_case, 
        mock_repository, 
        video_entity, 
        user_entity,
        mock_video_service
    ):
        """Test execution when no frames are extracted"""
        mock_repository.get_video_with_user.return_value = (video_entity, user_entity)
        mock_repository.update_video_status.return_value = True
        mock_mkstemp.return_value = (1, '/tmp/video.mp4')
        mock_fdopen.return_value.__enter__ = Mock()
        mock_fdopen.return_value.__exit__ = Mock()
        mock_fdopen.return_value.write = Mock()
        mock_exists.return_value = True
        mock_video_service.extract_frames.return_value = None
        
        result = use_case.execute("test-video-123", b"content", "https://queue.url")
        
        assert result is False
    
    @patch('src.application.use_cases.process_video_use_case.tempfile.mkstemp')
    @patch('src.application.use_cases.process_video_use_case.zipfile.ZipFile')
    @patch('src.application.use_cases.process_video_use_case.os.fdopen')
    @patch('src.application.use_cases.process_video_use_case.os.close')
    @patch('src.application.use_cases.process_video_use_case.os.path.exists')
    @patch('src.application.use_cases.process_video_use_case.os.remove')
    def test_execute_upload_fails(
        self,
        mock_remove,
        mock_exists,
        mock_close,
        mock_fdopen,
        mock_zipfile,
        mock_mkstemp,
        use_case, 
        mock_repository, 
        video_entity, 
        user_entity,
        mock_storage,
        mock_video_service
    ):
        """Test execution when S3 upload fails"""
        mock_repository.get_video_with_user.return_value = (video_entity, user_entity)
        mock_repository.update_video_status.return_value = True
        mock_mkstemp.side_effect = [(1, '/tmp/video.mp4'), (2, '/tmp/output.zip')]
        mock_fdopen.return_value.__enter__ = Mock()
        mock_fdopen.return_value.__exit__ = Mock()
        mock_fdopen.return_value.write = Mock()
        mock_exists.return_value = True
        mock_storage.upload_file.return_value = False
        mock_video_service.extract_frames.return_value = ['/tmp/frame1.jpg']
        
        # Mock zipfile
        mock_zip = MagicMock()
        mock_zipfile.return_value.__enter__.return_value = mock_zip
        
        result = use_case.execute("test-video-123", b"content", "https://queue.url")
        
        assert result is False
    
    @patch('src.application.use_cases.process_video_use_case.tempfile.mkstemp')
    @patch('src.application.use_cases.process_video_use_case.zipfile.ZipFile')
    @patch('src.application.use_cases.process_video_use_case.os.fdopen')
    @patch('src.application.use_cases.process_video_use_case.os.close')
    @patch('src.application.use_cases.process_video_use_case.os.path.exists')
    @patch('src.application.use_cases.process_video_use_case.os.remove')
    def test_execute_message_send_fails(
        self,
        mock_remove,
        mock_exists,
        mock_close,
        mock_fdopen,
        mock_zipfile,
        mock_mkstemp,
        use_case, 
        mock_repository, 
        video_entity, 
        user_entity,
        mock_storage,
        mock_message_producer,
        mock_video_service
    ):
        """Test execution when message send fails"""
        mock_repository.get_video_with_user.return_value = (video_entity, user_entity)
        mock_repository.update_video_status.return_value = True
        mock_mkstemp.side_effect = [(1, '/tmp/video.mp4'), (2, '/tmp/output.zip')]
        mock_fdopen.return_value.__enter__ = Mock()
        mock_fdopen.return_value.__exit__ = Mock()
        mock_fdopen.return_value.write = Mock()
        mock_exists.return_value = True
        mock_storage.upload_file.return_value = True
        mock_message_producer.send_message.return_value = False
        mock_video_service.extract_frames.return_value = ['/tmp/frame1.jpg']
        
        # Mock zipfile
        mock_zip = MagicMock()
        mock_zipfile.return_value.__enter__.return_value = mock_zip
        
        result = use_case.execute("test-video-123", b"content", "https://queue.url")
        
        assert result is False
    
    def test_get_zip_s3_key(self, use_case):
        """Test ZIP S3 key generation"""
        key = use_case._get_zip_s3_key("videos/test_video.mp4")
        assert key == "zip/test_video.zip"
        
        key = use_case._get_zip_s3_key("test.avi")
        assert key == "zip/test.zip"
    
    @patch('src.application.use_cases.process_video_use_case.os.path.exists')
    @patch('src.application.use_cases.process_video_use_case.os.remove')
    def test_cleanup_temp_files(self, mock_remove, mock_exists, use_case, mock_video_service):
        """Test cleanup of temporary files"""
        mock_exists.return_value = True
        
        use_case._cleanup_temp_files('/tmp/video.mp4', ['/tmp/frame1.jpg'], '/tmp/output.zip')
        
        # Should remove video and zip files
        assert mock_remove.call_count == 2
        # Should call video_service cleanup_files
        mock_video_service.cleanup_files.assert_called_once_with(['/tmp/frame1.jpg'])
