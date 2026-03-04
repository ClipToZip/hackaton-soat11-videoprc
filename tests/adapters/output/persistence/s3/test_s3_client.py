"""
Unit tests for S3Client
"""
import pytest
from unittest.mock import Mock, patch, MagicMock
from botocore.exceptions import ClientError
from src.adapters.output.persistence.s3.s3_client import S3Client


class TestS3Client:
    """Test cases for S3Client"""
    
    @patch('src.adapters.output.persistence.s3.s3_client.boto3.client')
    def test_client_initialization(self, mock_boto_client):
        """Test S3 client initialization"""
        from src.config.settings import Settings
        s3_client = S3Client()
        
        assert s3_client is not None
        assert s3_client.bucket_name == Settings.S3_BUCKET_NAME
        mock_boto_client.assert_called_once()
    
    @patch('src.adapters.output.persistence.s3.s3_client.boto3.client')
    def test_download_file_success(self, mock_boto_client, mock_s3_client):
        """Test successful file download"""
        mock_boto_client.return_value = mock_s3_client
        
        s3_client = S3Client()
        result = s3_client.download_file("videos/test.mp4", "/tmp/test.mp4")
        
        assert result is True
        # Verify it was called with correct parameters (bucket name from settings)
        assert mock_s3_client.download_file.call_count == 1
        call_args = mock_s3_client.download_file.call_args[0]
        assert call_args[1] == 'videos/test.mp4'
        assert call_args[2] == '/tmp/test.mp4'
    
    @patch('src.adapters.output.persistence.s3.s3_client.boto3.client')
    def test_download_file_client_error(self, mock_boto_client, mock_s3_client):
        """Test download file with ClientError"""
        mock_s3_client.download_file.side_effect = ClientError(
            {'Error': {'Code': 'NoSuchKey', 'Message': 'Key not found'}},
            'download_file'
        )
        mock_boto_client.return_value = mock_s3_client
        
        s3_client = S3Client()
        result = s3_client.download_file("videos/nonexistent.mp4", "/tmp/test.mp4")
        
        assert result is False
    
    @patch('src.adapters.output.persistence.s3.s3_client.boto3.client')
    def test_download_file_generic_exception(self, mock_boto_client, mock_s3_client):
        """Test download file with generic exception"""
        mock_s3_client.download_file.side_effect = Exception("Download error")
        mock_boto_client.return_value = mock_s3_client
        
        s3_client = S3Client()
        result = s3_client.download_file("videos/test.mp4", "/tmp/test.mp4")
        
        assert result is False
    
    @patch('src.adapters.output.persistence.s3.s3_client.boto3.client')
    def test_get_file_content_success(self, mock_boto_client, mock_s3_client):
        """Test successful get file content"""
        mock_body = MagicMock()
        mock_body.read.return_value = b"file content data"
        mock_s3_client.get_object.return_value = {'Body': mock_body}
        mock_boto_client.return_value = mock_s3_client
        
        s3_client = S3Client()
        content = s3_client.get_file_content("test.mp4")
        
        assert content == b"file content data"
        # Verify the call was made
        assert mock_s3_client.get_object.call_count == 1
        call_kwargs = mock_s3_client.get_object.call_args[1]
        assert call_kwargs['Key'] == 'videos/test.mp4'
    
    @patch('src.adapters.output.persistence.s3.s3_client.boto3.client')
    def test_get_file_content_client_error(self, mock_boto_client, mock_s3_client):
        """Test get file content with ClientError"""
        mock_s3_client.get_object.side_effect = ClientError(
            {'Error': {'Code': 'NoSuchKey', 'Message': 'Key not found'}},
            'get_object'
        )
        mock_boto_client.return_value = mock_s3_client
        
        s3_client = S3Client()
        content = s3_client.get_file_content("nonexistent.mp4")
        
        assert content is None
    
    @patch('src.adapters.output.persistence.s3.s3_client.boto3.client')
    def test_get_file_content_generic_exception(self, mock_boto_client, mock_s3_client):
        """Test get file content with generic exception"""
        mock_s3_client.get_object.side_effect = Exception("Read error")
        mock_boto_client.return_value = mock_s3_client
        
        s3_client = S3Client()
        content = s3_client.get_file_content("test.mp4")
        
        assert content is None
    
    @patch('src.adapters.output.persistence.s3.s3_client.boto3.client')
    def test_file_exists_true(self, mock_boto_client, mock_s3_client):
        """Test file_exists returns True when file exists"""
        mock_s3_client.head_object.return_value = {'ContentLength': 1024}
        mock_boto_client.return_value = mock_s3_client
        
        s3_client = S3Client()
        result = s3_client.file_exists("videos/test.mp4")
        
        assert result is True
        # Verify the call was made
        assert mock_s3_client.head_object.call_count == 1
        call_kwargs = mock_s3_client.head_object.call_args[1]
        assert call_kwargs['Key'] == 'videos/test.mp4'
    
    @patch('src.adapters.output.persistence.s3.s3_client.boto3.client')
    def test_file_exists_false(self, mock_boto_client, mock_s3_client):
        """Test file_exists returns False when file doesn't exist"""
        mock_s3_client.head_object.side_effect = ClientError(
            {'Error': {'Code': '404', 'Message': 'Not found'}},
            'head_object'
        )
        mock_boto_client.return_value = mock_s3_client
        
        s3_client = S3Client()
        result = s3_client.file_exists("videos/nonexistent.mp4")
        
        assert result is False
    
    @patch('src.adapters.output.persistence.s3.s3_client.boto3.client')
    def test_upload_file_success(self, mock_boto_client, mock_s3_client):
        """Test successful file upload"""
        mock_boto_client.return_value = mock_s3_client
        
        s3_client = S3Client()
        result = s3_client.upload_file("/tmp/test.zip", "zip/test.zip")
        
        assert result is True
        # Verify the call was made
        assert mock_s3_client.upload_file.call_count == 1
        call_args = mock_s3_client.upload_file.call_args[0]
        assert call_args[0] == '/tmp/test.zip'
        assert call_args[2] == 'zip/test.zip'
    
    @patch('src.adapters.output.persistence.s3.s3_client.boto3.client')
    def test_upload_file_client_error(self, mock_boto_client, mock_s3_client):
        """Test upload file with ClientError"""
        mock_s3_client.upload_file.side_effect = ClientError(
            {'Error': {'Code': 'AccessDenied', 'Message': 'Access denied'}},
            'upload_file'
        )
        mock_boto_client.return_value = mock_s3_client
        
        s3_client = S3Client()
        result = s3_client.upload_file("/tmp/test.zip", "zip/test.zip")
        
        assert result is False
    
    @patch('src.adapters.output.persistence.s3.s3_client.boto3.client')
    def test_upload_file_generic_exception(self, mock_boto_client, mock_s3_client):
        """Test upload file with generic exception"""
        mock_s3_client.upload_file.side_effect = Exception("Upload error")
        mock_boto_client.return_value = mock_s3_client
        
        s3_client = S3Client()
        result = s3_client.upload_file("/tmp/test.zip", "zip/test.zip")
        
        assert result is False
