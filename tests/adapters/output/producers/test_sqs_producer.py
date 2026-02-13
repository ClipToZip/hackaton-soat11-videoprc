"""
Unit tests for SQSProducer
"""
import pytest
import json
from unittest.mock import Mock, patch, MagicMock
from botocore.exceptions import ClientError
from src.adapters.output.producers.sqs_producer import SQSProducer


class TestSQSProducer:
    """Test cases for SQSProducer"""
    
    @patch('src.adapters.output.producers.sqs_producer.boto3.client')
    def test_producer_initialization(self, mock_boto_client):
        """Test producer initialization"""
        from src.config.settings import Settings
        producer = SQSProducer()
        
        assert producer is not None
        # Verify boto3 client was created with correct parameters
        call_kwargs = mock_boto_client.call_args[1]
        assert call_kwargs['region_name'] == Settings.AWS_REGION
    
    @patch('src.adapters.output.producers.sqs_producer.boto3.client')
    def test_send_message_success(self, mock_boto_client, mock_sqs_client):
        """Test successful message sending"""
        mock_sqs_client.send_message.return_value = {'MessageId': 'test-message-id-123'}
        mock_boto_client.return_value = mock_sqs_client
        
        producer = SQSProducer()
        
        message = {
            "titulo": "Test Video",
            "status": "Finalizado",
            "emailUsuario": "test@example.com"
        }
        
        result = producer.send_message("https://queue.url", message)
        
        assert result is True
        mock_sqs_client.send_message.assert_called_once()
        
        # Verify the message was JSON encoded
        call_args = mock_sqs_client.send_message.call_args
        assert call_args[1]['QueueUrl'] == "https://queue.url"
        assert json.loads(call_args[1]['MessageBody']) == message
    
    @patch('src.adapters.output.producers.sqs_producer.boto3.client')
    def test_send_message_with_complex_data(self, mock_boto_client, mock_sqs_client):
        """Test sending message with complex data"""
        mock_sqs_client.send_message.return_value = {'MessageId': 'test-id'}
        mock_boto_client.return_value = mock_sqs_client
        
        producer = SQSProducer()
        
        message = {
            "titulo": "Test Video",
            "status": "Finalizado",
            "emailUsuario": "test@example.com",
            "metadata": {
                "duration": 120,
                "format": "mp4",
                "tags": ["test", "video"]
            }
        }
        
        result = producer.send_message("https://queue.url", message)
        
        assert result is True
    
    @patch('src.adapters.output.producers.sqs_producer.boto3.client')
    def test_send_message_client_error(self, mock_boto_client, mock_sqs_client):
        """Test send message with ClientError"""
        mock_sqs_client.send_message.side_effect = ClientError(
            {'Error': {'Code': 'TestError', 'Message': 'Test error message'}},
            'send_message'
        )
        mock_boto_client.return_value = mock_sqs_client
        
        producer = SQSProducer()
        
        message = {"test": "data"}
        result = producer.send_message("https://queue.url", message)
        
        assert result is False
    
    @patch('src.adapters.output.producers.sqs_producer.boto3.client')
    def test_send_message_generic_exception(self, mock_boto_client, mock_sqs_client):
        """Test send message with generic exception"""
        mock_sqs_client.send_message.side_effect = Exception("Unexpected error")
        mock_boto_client.return_value = mock_sqs_client
        
        producer = SQSProducer()
        
        message = {"test": "data"}
        result = producer.send_message("https://queue.url", message)
        
        assert result is False
    
    @patch('src.adapters.output.producers.sqs_producer.boto3.client')
    def test_send_message_empty_message(self, mock_boto_client, mock_sqs_client):
        """Test sending empty message"""
        mock_sqs_client.send_message.return_value = {'MessageId': 'test-id'}
        mock_boto_client.return_value = mock_sqs_client
        
        producer = SQSProducer()
        
        result = producer.send_message("https://queue.url", {})
        
        assert result is True
        
        call_args = mock_sqs_client.send_message.call_args
        assert json.loads(call_args[1]['MessageBody']) == {}
    
    @patch('src.adapters.output.producers.sqs_producer.boto3.client')
    def test_close_producer(self, mock_boto_client):
        """Test closing producer"""
        producer = SQSProducer()
        
        # Should not raise exception
        producer.close()
    
    @patch('src.adapters.output.producers.sqs_producer.boto3.client')
    def test_send_multiple_messages(self, mock_boto_client, mock_sqs_client):
        """Test sending multiple messages"""
        mock_sqs_client.send_message.return_value = {'MessageId': 'test-id'}
        mock_boto_client.return_value = mock_sqs_client
        
        producer = SQSProducer()
        
        messages = [
            {"id": 1, "data": "message 1"},
            {"id": 2, "data": "message 2"},
            {"id": 3, "data": "message 3"}
        ]
        
        for msg in messages:
            result = producer.send_message("https://queue.url", msg)
            assert result is True
        
        assert mock_sqs_client.send_message.call_count == 3
