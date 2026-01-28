"""
Port for message producer operations (Kafka)
"""
from abc import ABC, abstractmethod
from typing import Dict, Any


class MessageProducerPort(ABC):
    """Interface for message producer operations"""
    
    @abstractmethod
    def send_message(self, topic: str, message: Dict[str, Any]) -> bool:
        """
        Send a message to a topic
        
        Args:
            topic: Topic name
            message: Message data as dictionary
            
        Returns:
            True if message was sent successfully, False otherwise
        """
        pass
