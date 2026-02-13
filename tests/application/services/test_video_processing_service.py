"""
Unit tests for VideoProcessingService
"""
import pytest
import os
import tempfile
from unittest.mock import Mock, patch, MagicMock
from src.application.services.video_processing_service import VideoProcessingService


class TestVideoProcessingService:
    """Test cases for VideoProcessingService"""
    
    @pytest.fixture
    def video_service(self):
        """Create video processing service instance"""
        return VideoProcessingService()
    
    @pytest.fixture
    def mock_video_capture(self):
        """Mock cv2.VideoCapture"""
        import cv2
        mock = MagicMock()
        mock.isOpened.return_value = True
        mock.get.side_effect = lambda prop: {
            cv2.CAP_PROP_FRAME_COUNT: 100,
            cv2.CAP_PROP_FPS: 30.0
        }.get(prop, 0)
        mock.read.return_value = (True, MagicMock())
        return mock
    
    def test_service_initialization(self, video_service):
        """Test service initialization"""
        assert video_service is not None
    
    @patch('src.application.services.video_processing_service.cv2.VideoCapture')
    @patch('src.application.services.video_processing_service.cv2.imwrite')
    def test_extract_frames_success(self, mock_imwrite, mock_video_capture_class, video_service, mock_video_capture):
        """Test successful frame extraction"""
        mock_video_capture_class.return_value = mock_video_capture
        mock_imwrite.return_value = True
        
        # Create a temporary video file
        with tempfile.NamedTemporaryFile(suffix='.mp4', delete=False) as tmp:
            video_path = tmp.name
        
        try:
            frame_paths = video_service.extract_frames(video_path, num_frames=4)
            
            assert frame_paths is not None
            assert len(frame_paths) == 4
            assert all(path.endswith('.jpg') for path in frame_paths)
            
            # Verify cv2 methods were called
            mock_video_capture.isOpened.assert_called()
            mock_video_capture.get.assert_called()
            assert mock_video_capture.read.call_count >= 4
        finally:
            if os.path.exists(video_path):
                os.remove(video_path)
    
    @patch('src.application.services.video_processing_service.cv2.VideoCapture')
    def test_extract_frames_video_not_opened(self, mock_video_capture_class, video_service):
        """Test frame extraction when video cannot be opened"""
        mock_capture = MagicMock()
        mock_capture.isOpened.return_value = False
        mock_video_capture_class.return_value = mock_capture
        
        with tempfile.NamedTemporaryFile(suffix='.mp4', delete=False) as tmp:
            video_path = tmp.name
        
        try:
            frame_paths = video_service.extract_frames(video_path, num_frames=4)
            
            assert frame_paths is None
        finally:
            if os.path.exists(video_path):
                os.remove(video_path)
    
    @patch('src.application.services.video_processing_service.cv2.VideoCapture')
    @patch('src.application.services.video_processing_service.cv2.imwrite')
    def test_extract_frames_fewer_frames_than_requested(self, mock_imwrite, mock_video_capture_class, video_service):
        """Test frame extraction when video has fewer frames than requested"""
        import cv2
        mock_capture = MagicMock()
        mock_capture.isOpened.return_value = True
        mock_capture.get.side_effect = lambda prop: {
            cv2.CAP_PROP_FRAME_COUNT: 2,  # Only 2 frames
            cv2.CAP_PROP_FPS: 30.0
        }.get(prop, 0)
        mock_capture.read.return_value = (True, MagicMock())
        mock_video_capture_class.return_value = mock_capture
        mock_imwrite.return_value = True
        
        with tempfile.NamedTemporaryFile(suffix='.mp4', delete=False) as tmp:
            video_path = tmp.name
        
        try:
            frame_paths = video_service.extract_frames(video_path, num_frames=4)
            
            assert frame_paths is not None
            assert len(frame_paths) == 2  # Should extract only 2 frames
        finally:
            if os.path.exists(video_path):
                os.remove(video_path)
    
    @patch('src.application.services.video_processing_service.cv2.VideoCapture')
    @patch('src.application.services.video_processing_service.cv2.imwrite')
    def test_extract_single_frame(self, mock_imwrite, mock_video_capture_class, video_service, mock_video_capture):
        """Test extracting single frame"""
        mock_video_capture_class.return_value = mock_video_capture
        mock_imwrite.return_value = True
        
        with tempfile.NamedTemporaryFile(suffix='.mp4', delete=False) as tmp:
            video_path = tmp.name
        
        try:
            frame_paths = video_service.extract_frames(video_path, num_frames=1)
            
            assert frame_paths is not None
            assert len(frame_paths) == 1
        finally:
            if os.path.exists(video_path):
                os.remove(video_path)
    
    @patch('src.application.services.video_processing_service.cv2.VideoCapture')
    @patch('src.application.services.video_processing_service.cv2.imwrite')
    def test_extract_frames_read_failure(self, mock_imwrite, mock_video_capture_class, video_service):
        """Test frame extraction when frame read fails"""
        import cv2
        mock_capture = MagicMock()
        mock_capture.isOpened.return_value = True
        mock_capture.get.side_effect = lambda prop: {
            cv2.CAP_PROP_FRAME_COUNT: 100,
            cv2.CAP_PROP_FPS: 30.0
        }.get(prop, 0)
        mock_capture.read.return_value = (False, None)  # Read fails
        mock_video_capture_class.return_value = mock_capture
        
        with tempfile.NamedTemporaryFile(suffix='.mp4', delete=False) as tmp:
            video_path = tmp.name
        
        try:
            frame_paths = video_service.extract_frames(video_path, num_frames=4)
            
            # Should return empty list or None, not crash
            assert frame_paths is not None
            assert len(frame_paths) == 0
        finally:
            if os.path.exists(video_path):
                os.remove(video_path)
    
    @patch('src.application.services.video_processing_service.cv2.VideoCapture')
    def test_extract_frames_exception(self, mock_video_capture_class, video_service):
        """Test frame extraction handles exceptions"""
        mock_video_capture_class.side_effect = Exception("Video error")
        
        with tempfile.NamedTemporaryFile(suffix='.mp4', delete=False) as tmp:
            video_path = tmp.name
        
        try:
            frame_paths = video_service.extract_frames(video_path, num_frames=4)
            
            assert frame_paths is None
        finally:
            if os.path.exists(video_path):
                os.remove(video_path)
    
    def test_cleanup_files_success(self, video_service):
        """Test successful file cleanup"""
        # Create temporary files
        temp_files = []
        for i in range(3):
            with tempfile.NamedTemporaryFile(delete=False) as tmp:
                temp_files.append(tmp.name)
        
        # Cleanup files
        video_service.cleanup_files(temp_files)
        
        # Verify files are deleted
        for file_path in temp_files:
            assert not os.path.exists(file_path)
    
    def test_cleanup_files_nonexistent(self, video_service):
        """Test cleanup with nonexistent files"""
        # Should not raise exception
        video_service.cleanup_files(['/path/to/nonexistent/file.jpg'])
    
    def test_cleanup_files_empty_list(self, video_service):
        """Test cleanup with empty list"""
        # Should not raise exception
        video_service.cleanup_files([])
    
    @patch('src.application.services.video_processing_service.os.path.exists')
    @patch('src.application.services.video_processing_service.os.remove')
    def test_cleanup_files_with_error(self, mock_remove, mock_exists, video_service):
        """Test cleanup continues even if error occurs"""
        mock_exists.return_value = True
        mock_remove.side_effect = Exception("Remove error")
        
        # Should not raise exception, just log warning
        video_service.cleanup_files(['/some/file.jpg'])
        
        mock_exists.assert_called_once_with('/some/file.jpg')
        mock_remove.assert_called_once_with('/some/file.jpg')
