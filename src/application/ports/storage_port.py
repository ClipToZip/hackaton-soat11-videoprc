"""
Port for storage operations (S3)
"""
from abc import ABC, abstractmethod
from typing import Optional


class StoragePort(ABC):
    """Interface for storage operations"""
    
    @abstractmethod
    def download_file(self, key: str, local_path: str) -> bool:
        """Download a file from storage"""
        pass
    
    @abstractmethod
    def get_file_content(self, key: str) -> Optional[bytes]:
        """Get file content from storage"""
        pass
    
    @abstractmethod
    def upload_file(self, local_path: str, key: str) -> bool:
        """Upload a file to storage"""
        pass
    
    @abstractmethod
    def file_exists(self, key: str) -> bool:
        """Check if file exists in storage"""
        pass
