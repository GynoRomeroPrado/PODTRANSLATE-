"""Queue utilities and worker base classes."""

import pika
import json
import logging
from typing import Callable, Dict, Any

logger = logging.getLogger(__name__)


class QueuePublisher:
    """Publisher for sending jobs to RabbitMQ queues."""

    def __init__(self, rabbitmq_url: str):
        """
        Initialize publisher.

        Args:
            rabbitmq_url: RabbitMQ connection URL
        """
        self.rabbitmq_url = rabbitmq_url
        self.connection = None
        self.channel = None

    def connect(self):
        """Connect to RabbitMQ."""
        try:
            parameters = pika.URLParameters(self.rabbitmq_url)
            self.connection = pika.BlockingConnection(parameters)
            self.channel = self.connection.channel()
            logger.info("Publisher connected to RabbitMQ")
        except Exception as e:
            logger.error(f"Failed to connect to RabbitMQ: {e}")
            raise

    def publish(self, queue_name: str, message: Dict[Any, Any]):
        """
        Publish a message to a queue.

        Args:
            queue_name: Name of the queue
            message: Message data (will be JSON encoded)
        """
        if not self.channel:
            self.connect()

        try:
            # Declare queue
            self.channel.queue_declare(queue=queue_name, durable=True)

            # Publish message
            self.channel.basic_publish(
                exchange='',
                routing_key=queue_name,
                body=json.dumps(message),
                properties=pika.BasicProperties(
                    delivery_mode=2,  # Make message persistent
                )
            )

            logger.info(f"Published message to {queue_name}")

        except Exception as e:
            logger.error(f"Failed to publish message: {e}")
            raise

    def close(self):
        """Close connection."""
        if self.connection:
            self.connection.close()
            logger.info("Publisher connection closed")


class BaseWorker:
    """Base class for queue workers."""

    def __init__(self, rabbitmq_url: str, queue_name: str):
        """
        Initialize worker.

        Args:
            rabbitmq_url: RabbitMQ connection URL
            queue_name: Queue to consume from
        """
        self.rabbitmq_url = rabbitmq_url
        self.queue_name = queue_name
        self.connection = None
        self.channel = None

    def connect(self):
        """Connect to RabbitMQ."""
        try:
            parameters = pika.URLParameters(self.rabbitmq_url)
            self.connection = pika.BlockingConnection(parameters)
            self.channel = self.connection.channel()

            # Declare queue
            self.channel.queue_declare(queue=self.queue_name, durable=True)

            # Set QoS
            self.channel.basic_qos(prefetch_count=1)

            logger.info(f"Worker connected to queue: {self.queue_name}")

        except Exception as e:
            logger.error(f"Failed to connect to RabbitMQ: {e}")
            raise

    def process_message(self, message: Dict[Any, Any]) -> Dict[Any, Any]:
        """
        Process a message (to be implemented by subclasses).

        Args:
            message: Message data

        Returns:
            Processing result
        """
        raise NotImplementedError("Subclasses must implement process_message")

    def callback(self, ch, method, properties, body):
        """Message callback."""
        try:
            message = json.loads(body)
            logger.info(f"Received message: {message}")

            # Process message
            result = self.process_message(message)

            # Acknowledge
            ch.basic_ack(delivery_tag=method.delivery_tag)

            logger.info(f"Message processed: {result}")

        except Exception as e:
            logger.error(f"Error processing message: {e}", exc_info=True)
            # Reject and requeue
            ch.basic_nack(delivery_tag=method.delivery_tag, requeue=True)

    def start(self):
        """Start consuming messages."""
        if not self.channel:
            self.connect()

        logger.info(f"Worker started for queue: {self.queue_name}")

        self.channel.basic_consume(
            queue=self.queue_name,
            on_message_callback=self.callback
        )

        try:
            self.channel.start_consuming()
        except KeyboardInterrupt:
            logger.info("Worker stopped by user")
            self.channel.stop_consuming()
        finally:
            if self.connection:
                self.connection.close()
