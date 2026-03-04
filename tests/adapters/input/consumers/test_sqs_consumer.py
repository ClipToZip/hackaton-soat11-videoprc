"""
Unit tests for SQSConsumer
"""
import pytest
import json
from unittest.mock import Mock, patch, MagicMock
from botocore.exceptions import ClientError
from src.adapters.input.consumers.sqs_consumer import SQSConsumer


class TestSQSConsumer:
    """Test cases for SQSConsumer"""
    
    @pytest.fixture
    def mock_handler(self):
        """Mock message handler"""
        return Mock()
    
    @patch('src.adapters.input.consumers.sqs_consumer.boto3.client')
    @patch('src.adapters.input.consumers.sqs_consumer.S3Client')
    def test_consumer_initialization(self, mock_s3_class, mock_boto_client, mock_handler):
        """Test consumer initialization"""
        from src.config.settings import Settings
        consumer = SQSConsumer(message_handler=mock_handler)
        
        assert consumer is not None
        assert consumer.message_handler == mock_handler
        assert consumer.queue_url == Settings.CLIPTOZIP_EVENTS_URL
        assert consumer.running is False
        mock_boto_client.assert_called_once()
    
    @patch('src.adapters.input.consumers.sqs_consumer.boto3.client')
    @patch('src.adapters.input.consumers.sqs_consumer.S3Client')
    def test_consumer_initialization_without_handler(self, mock_s3_class, mock_boto_client):
        """Test consumer initialization without custom handler"""
        consumer = SQSConsumer()
        
        assert consumer.message_handler is None
    
    @patch('src.adapters.input.consumers.sqs_consumer.boto3.client')
    @patch('src.adapters.input.consumers.sqs_consumer.S3Client')
    def test_process_message_success(self, mock_s3_class, mock_boto_client, mock_handler, sample_sqs_message):
        """Test successful message processing"""
        # Setup
        consumer = SQSConsumer(message_handler=mock_handler)
        
        mock_s3_instance = MagicMock()
        mock_s3_instance.get_file_content.return_value = b"video content"
        mock_s3_class.return_value = mock_s3_instance
        consumer.s3_client = mock_s3_instance
        
        # Execute
        result = consumer.process_message(sample_sqs_message)
        
        # Assertions
        assert result is True
        mock_s3_instance.get_file_content.assert_called_once_with("videos/test_video.mp4")
        mock_handler.assert_called_once_with("test-video-123", b"video content")
    
    @patch('src.adapters.input.consumers.sqs_consumer.boto3.client')
    @patch('src.adapters.input.consumers.sqs_consumer.S3Client')
    def test_process_message_missing_video_id(self, mock_s3_class, mock_boto_client):
        """Test processing message without video_id"""
        consumer = SQSConsumer()
        
        message = {
            'MessageId': 'test-id',
            'Body': json.dumps({"path": "videos/test.mp4"})
        }
        
        result = consumer.process_message(message)
        
        assert result is False
    
    @patch('src.adapters.input.consumers.sqs_consumer.boto3.client')
    @patch('src.adapters.input.consumers.sqs_consumer.S3Client')
    def test_process_message_missing_path(self, mock_s3_class, mock_boto_client):
        """Test processing message without path"""
        consumer = SQSConsumer()
        
        message = {
            'MessageId': 'test-id',
            'Body': json.dumps({"video_id": "test-123"})
        }
        
        result = consumer.process_message(message)
        
        assert result is False
    
    @patch('src.adapters.input.consumers.sqs_consumer.boto3.client')
    @patch('src.adapters.input.consumers.sqs_consumer.S3Client')
    def test_process_message_invalid_json(self, mock_s3_class, mock_boto_client):
        """Test processing message with invalid JSON"""
        consumer = SQSConsumer()
        
        message = {
            'MessageId': 'test-id',
            'Body': 'invalid json{'
        }
        
        result = consumer.process_message(message)
        
        assert result is False
    
    @patch('src.adapters.input.consumers.sqs_consumer.boto3.client')
    @patch('src.adapters.input.consumers.sqs_consumer.S3Client')
    def test_process_message_s3_error(self, mock_s3_class, mock_boto_client, sample_sqs_message):
        """Test processing message when S3 get fails"""
        consumer = SQSConsumer()
        
        mock_s3_instance = MagicMock()
        mock_s3_instance.get_file_content.return_value = None
        consumer.s3_client = mock_s3_instance
        
        result = consumer.process_message(sample_sqs_message)
        
        assert result is False
    
    @patch('src.adapters.input.consumers.sqs_consumer.boto3.client')
    @patch('src.adapters.input.consumers.sqs_consumer.S3Client')
    def test_delete_message_success(self, mock_s3_class, mock_boto_client, mock_sqs_client):
        """Test successful message deletion"""
        mock_boto_client.return_value = mock_sqs_client
        consumer = SQSConsumer()
        
        consumer.delete_message("test-receipt-handle")
        
        mock_sqs_client.delete_message.assert_called_once_with(
            QueueUrl=consumer.queue_url,
            ReceiptHandle="test-receipt-handle"
        )
    
    @patch('src.adapters.input.consumers.sqs_consumer.boto3.client')
    @patch('src.adapters.input.consumers.sqs_consumer.S3Client')
    def test_delete_message_error(self, mock_s3_class, mock_boto_client, mock_sqs_client):
        """Test message deletion with error"""
        mock_sqs_client.delete_message.side_effect = ClientError(
            {'Error': {'Code': 'TestError', 'Message': 'Test error'}},
            'delete_message'
        )
        mock_boto_client.return_value = mock_sqs_client
        consumer = SQSConsumer()
        
        # Should not raise exception
        consumer.delete_message("test-receipt-handle")
    
    @patch('src.adapters.input.consumers.sqs_consumer.boto3.client')
    @patch('src.adapters.input.consumers.sqs_consumer.S3Client')
    def test_stop_consumer(self, mock_s3_class, mock_boto_client):
        """Test stopping consumer"""
        consumer = SQSConsumer()
        consumer.running = True
        
        consumer.stop()
        
        assert consumer.running is False
    
    @patch('src.adapters.input.consumers.sqs_consumer.boto3.client')
    @patch('src.adapters.input.consumers.sqs_consumer.S3Client')
    def test_default_message_handler(self, mock_s3_class, mock_boto_client):
        """Test default message handler"""
        consumer = SQSConsumer()
        
        # Should not raise exception
        consumer._default_message_handler("test-video-id", b"content")
    
    @patch('src.adapters.input.consumers.sqs_consumer.boto3.client')
    @patch('src.adapters.input.consumers.sqs_consumer.S3Client')
    def test_start_consumer_with_messages(self, mock_s3_class, mock_boto_client, mock_sqs_client, sample_sqs_message):
        """Test starting consumer and processing messages"""
        # Setup
        mock_sqs_client.receive_message.side_effect = [
            {'Messages': [sample_sqs_message]},
            KeyboardInterrupt()  # Stop after one iteration
        ]
        mock_boto_client.return_value = mock_sqs_client
        
        mock_s3_instance = MagicMock()
        mock_s3_instance.get_file_content.return_value = b"content"
        mock_s3_class.return_value = mock_s3_instance
        
        consumer = SQSConsumer()
        consumer.s3_client = mock_s3_instance
        
        # Execute (will be interrupted after first iteration)
        try:
            consumer.start()
        except KeyboardInterrupt:
            pass
        
        # Assertions
        assert consumer.running is False
        mock_sqs_client.receive_message.assert_called()
    
    @patch('src.adapters.input.consumers.sqs_consumer.boto3.client')
    @patch('src.adapters.input.consumers.sqs_consumer.S3Client')
    def test_start_consumer_no_messages(self, mock_s3_class, mock_boto_client, mock_sqs_client):
        """Test starting consumer with no messages"""
        # Setup
        mock_sqs_client.receive_message.side_effect = [
            {'Messages': []},
            KeyboardInterrupt()
        ]
        mock_boto_client.return_value = mock_sqs_client
        
        consumer = SQSConsumer()
        
        # Execute
        try:
            consumer.start()
        except KeyboardInterrupt:
            pass
        
        assert consumer.running is False
