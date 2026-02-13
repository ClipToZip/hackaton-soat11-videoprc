"""
Pytest configuration and fixtures
"""
import pytest
import os
from datetime import datetime
from unittest.mock import Mock, MagicMock

# Setup environment variables before any other imports
os.environ.setdefault('AWS_ACCESS_KEY_ID', 'test_access_key')
os.environ.setdefault('AWS_SECRET_ACCESS_KEY', 'test_secret_key')
os.environ.setdefault('AWS_REGION', 'us-east-1')
os.environ.setdefault('S3_BUCKET_NAME', 'test-bucket')
os.environ.setdefault('DB_HOST', 'localhost')
os.environ.setdefault('DB_PORT', '5432')
os.environ.setdefault('DB_NAME', 'testdb')
os.environ.setdefault('DB_USER', 'testuser')
os.environ.setdefault('DB_PASSWORD', 'testpass')
os.environ.setdefault('CLIPTOZIP_EVENTS_URL', 'https://sqs.us-east-1.amazonaws.com/123/events')
os.environ.setdefault('CLIPTOZIP_NOTIFICATIONS_URL', 'https://sqs.us-east-1.amazonaws.com/123/notifications')
os.environ.setdefault('LOG_LEVEL', 'INFO')
os.environ.setdefault('APP_NAME', 'test-app')
os.environ.setdefault('MAX_WORKERS', '3')

from src.domain.entities.video_entity import VideoEntity
from src.domain.entities.user_entity import UserEntity


@pytest.fixture
def sample_video_entity():
    """Sample video entity for testing"""
    return VideoEntity(
        video_id="test-video-123",
        user_id="test-user-456",
        data_video_up=datetime(2023, 1, 1, 12, 0, 0),
        status=1,
        video_name="test_video.mp4",
        zip_name=None,
        descricao="Test video description",
        titulo="Test Video Title",
        metadados={"duration": 120},
        path="videos/test_video.mp4"
    )


@pytest.fixture
def sample_user_entity():
    """Sample user entity for testing"""
    return UserEntity(
        user_id="test-user-456",
        name="Test User",
        email="testuser@example.com",
        password_hash="hashed_password_123",
        created_at=datetime(2023, 1, 1, 10, 0, 0)
    )


@pytest.fixture
def mock_storage():
    """Mock storage port"""
    storage = Mock()
    storage.download_file = Mock(return_value=True)
    storage.get_file_content = Mock(return_value=b"fake video content")
    storage.upload_file = Mock(return_value=True)
    storage.file_exists = Mock(return_value=True)
    return storage


@pytest.fixture
def mock_message_producer():
    """Mock message producer port"""
    producer = Mock()
    producer.send_message = Mock(return_value=True)
    return producer


@pytest.fixture
def mock_repository():
    """Mock video repository port"""
    repository = Mock()
    repository.get_video_with_user = Mock(return_value=None)
    repository.update_video_status = Mock(return_value=True)
    return repository


@pytest.fixture
def mock_db_connection():
    """Mock database connection"""
    connection = MagicMock()
    connection.autocommit = False
    connection.closed = False
    return connection


@pytest.fixture
def mock_s3_client():
    """Mock boto3 S3 client"""
    client = MagicMock()
    client.download_file = Mock(return_value=None)
    client.get_object = Mock(return_value={'Body': MagicMock()})
    client.upload_file = Mock(return_value=None)
    client.head_object = Mock(return_value={})
    return client


@pytest.fixture
def mock_sqs_client():
    """Mock boto3 SQS client"""
    client = MagicMock()
    client.send_message = Mock(return_value={'MessageId': 'test-message-id'})
    client.receive_message = Mock(return_value={'Messages': []})
    client.delete_message = Mock(return_value=None)
    return client


@pytest.fixture
def sample_video_content():
    """Sample video file content"""
    return b"fake video content data"


@pytest.fixture
def sample_sqs_message():
    """Sample SQS message"""
    return {
        'MessageId': 'test-message-id',
        'ReceiptHandle': 'test-receipt-handle',
        'Body': '{"video_id": "test-video-123", "path": "videos/test_video.mp4"}'
    }


@pytest.fixture(autouse=True)
def setup_env_vars(monkeypatch):
    """Setup environment variables for testing"""
    monkeypatch.setenv('AWS_ACCESS_KEY_ID', 'test_access_key')
    monkeypatch.setenv('AWS_SECRET_ACCESS_KEY', 'test_secret_key')
    monkeypatch.setenv('AWS_REGION', 'us-east-1')
    monkeypatch.setenv('S3_BUCKET_NAME', 'test-bucket')
    monkeypatch.setenv('DB_HOST', 'localhost')
    monkeypatch.setenv('DB_PORT', '5432')
    monkeypatch.setenv('DB_NAME', 'testdb')
    monkeypatch.setenv('DB_USER', 'testuser')
    monkeypatch.setenv('DB_PASSWORD', 'testpass')
    monkeypatch.setenv('CLIPTOZIP_EVENTS_URL', 'https://sqs.us-east-1.amazonaws.com/123/events')
    monkeypatch.setenv('CLIPTOZIP_NOTIFICATIONS_URL', 'https://sqs.us-east-1.amazonaws.com/123/notifications')
    monkeypatch.setenv('LOG_LEVEL', 'INFO')
    monkeypatch.setenv('APP_NAME', 'test-app')
    monkeypatch.setenv('MAX_WORKERS', '3')
