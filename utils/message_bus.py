"""
Message Bus implementation for agent communication.

This module provides a publish-subscribe message bus that enables asynchronous
communication between agents in the simulation.
"""

from queue import Queue
from typing import Dict, List, Callable
from collections import defaultdict


# Message topic constants
TOPIC_TASK_ASSIGNED = "task.assigned"
TOPIC_STATUS_UPDATE = "status.update"
TOPIC_ALERT_DISEASE = "alert.disease"
TOPIC_ALERT_OBSTACLE = "alert.obstacle"
TOPIC_TASK_COMPLETED = "task.completed"


class MessageBus:
    """
    Publish-subscribe message bus for agent communication.
    
    Enables decoupled asynchronous communication between agents by routing
    messages through topics. Agents can publish messages to topics and
    subscribe to receive messages from specific topics.
    """
    
    def __init__(self):
        """Initialize the message bus with empty subscribers and message queue."""
        self.subscribers: Dict[str, List[Callable]] = defaultdict(list)
        self.message_queue: Queue = Queue()
    
    def publish(self, topic: str, message):
        """
        Publish a message to a specific topic.
        
        Messages are queued for asynchronous delivery to all subscribers
        of the specified topic.
        
        Args:
            topic: The topic/channel to publish to
            message: The Message object to publish
        """
        self.message_queue.put((topic, message))
    
    def subscribe(self, topic: str, callback: Callable):
        """
        Subscribe to messages on a specific topic.
        
        The callback function will be invoked with the message object
        whenever a message is published to the specified topic.
        
        Args:
            topic: The topic/channel to subscribe to
            callback: Function to call when messages arrive (receives message as argument)
        """
        if callback not in self.subscribers[topic]:
            self.subscribers[topic].append(callback)
    
    def unsubscribe(self, topic: str, callback: Callable):
        """
        Unsubscribe from messages on a specific topic.
        
        Args:
            topic: The topic/channel to unsubscribe from
            callback: The callback function to remove
        """
        if callback in self.subscribers[topic]:
            self.subscribers[topic].remove(callback)
    
    def process_messages(self):
        """
        Process all queued messages and deliver to subscribers.
        
        This method should be called once per simulation step to deliver
        all pending messages to their subscribers. Messages are delivered
        synchronously within this call but were queued asynchronously.
        """
        while not self.message_queue.empty():
            topic, message = self.message_queue.get()
            
            # Deliver message to all subscribers of this topic
            if topic in self.subscribers:
                for callback in self.subscribers[topic]:
                    try:
                        callback(message)
                    except Exception as e:
                        # Log error but continue processing other messages
                        print(f"Error delivering message to subscriber: {e}")
    
    def clear(self):
        """Clear all subscribers and pending messages."""
        self.subscribers.clear()
        while not self.message_queue.empty():
            self.message_queue.get()
