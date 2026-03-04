"""
Unit tests for DatabaseConnection
"""
import pytest
from unittest.mock import Mock, patch, MagicMock
from src.adapters.output.persistence.database_connection import DatabaseConnection


class TestDatabaseConnection:
    """Test cases for DatabaseConnection"""
    
    def test_initialization(self):
        """Test database connection initialization"""
        db_conn = DatabaseConnection()
        
        assert db_conn is not None
        assert db_conn.connection is None
    
    @patch('src.adapters.output.persistence.database_connection.psycopg2.connect')
    def test_connect_success(self, mock_connect):
        """Test successful database connection"""
        from src.config.settings import Settings
        mock_connection = MagicMock()
        mock_connect.return_value = mock_connection
        
        db_conn = DatabaseConnection()
        result = db_conn.connect()
        
        assert result == mock_connection
        assert db_conn.connection == mock_connection
        mock_connect.assert_called_once_with(
            host=Settings.DB_HOST,
            port=Settings.DB_PORT,
            database=Settings.DB_NAME,
            user=Settings.DB_USER,
            password=Settings.DB_PASSWORD
        )
    
    @patch('src.adapters.output.persistence.database_connection.psycopg2.connect')
    def test_connect_failure(self, mock_connect):
        """Test connection failure"""
        mock_connect.side_effect = Exception("Connection failed")
        
        db_conn = DatabaseConnection()
        
        with pytest.raises(Exception) as exc_info:
            db_conn.connect()
        
        assert "Connection failed" in str(exc_info.value)
    
    @patch('src.adapters.output.persistence.database_connection.psycopg2.connect')
    def test_close_connection(self, mock_connect):
        """Test closing connection"""
        mock_connection = MagicMock()
        mock_connect.return_value = mock_connection
        
        db_conn = DatabaseConnection()
        db_conn.connect()
        db_conn.close()
        
        mock_connection.close.assert_called_once()
    
    def test_close_when_no_connection(self):
        """Test closing when no connection exists"""
        db_conn = DatabaseConnection()
        
        # Should not raise exception
        db_conn.close()
    
    @patch('src.adapters.output.persistence.database_connection.psycopg2.connect')
    def test_rollback(self, mock_connect):
        """Test rollback transaction"""
        mock_connection = MagicMock()
        mock_connection.closed = False
        mock_connect.return_value = mock_connection
        
        db_conn = DatabaseConnection()
        db_conn.connect()
        db_conn.rollback()
        
        mock_connection.rollback.assert_called_once()
    
    @patch('src.adapters.output.persistence.database_connection.psycopg2.connect')
    def test_rollback_on_closed_connection(self, mock_connect):
        """Test rollback on closed connection"""
        mock_connection = MagicMock()
        mock_connection.closed = True
        mock_connect.return_value = mock_connection
        
        db_conn = DatabaseConnection()
        db_conn.connect()
        
        # Should not raise exception
        db_conn.rollback()
    
    def test_rollback_when_no_connection(self):
        """Test rollback when no connection exists"""
        db_conn = DatabaseConnection()
        
        # Should not raise exception
        db_conn.rollback()
    
    @patch('src.adapters.output.persistence.database_connection.psycopg2.connect')
    def test_rollback_with_error(self, mock_connect):
        """Test rollback with error"""
        mock_connection = MagicMock()
        mock_connection.closed = False
        mock_connection.rollback.side_effect = Exception("Rollback error")
        mock_connect.return_value = mock_connection
        
        db_conn = DatabaseConnection()
        db_conn.connect()
        
        # Should not raise exception, just log
        db_conn.rollback()
    
    @patch('src.adapters.output.persistence.database_connection.psycopg2.connect')
    def test_get_connection_when_exists(self, mock_connect):
        """Test get_connection when connection exists"""
        mock_connection = MagicMock()
        mock_connection.closed = False
        mock_connect.return_value = mock_connection
        
        db_conn = DatabaseConnection()
        db_conn.connect()
        
        result = db_conn.get_connection()
        
        assert result == mock_connection
        # Should not create new connection
        assert mock_connect.call_count == 1
    
    @patch('src.adapters.output.persistence.database_connection.psycopg2.connect')
    def test_get_connection_when_not_exists(self, mock_connect):
        """Test get_connection creates new connection if none exists"""
        mock_connection = MagicMock()
        mock_connect.return_value = mock_connection
        
        db_conn = DatabaseConnection()
        
        result = db_conn.get_connection()
        
        assert result == mock_connection
        mock_connect.assert_called_once()
    
    @patch('src.adapters.output.persistence.database_connection.psycopg2.connect')
    def test_get_connection_when_closed(self, mock_connect):
        """Test get_connection creates new connection if current is closed"""
        mock_connection = MagicMock()
        mock_connection.closed = True
        mock_connect.return_value = mock_connection
        
        db_conn = DatabaseConnection()
        db_conn.connection = mock_connection
        
        result = db_conn.get_connection()
        
        assert result == mock_connection
        # Should create new connection
        assert mock_connect.call_count == 1
