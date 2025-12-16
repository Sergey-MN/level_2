import asyncio
import pika
import json
import logging

from app_project.models.models import Status
from app_project.database import session_context
from app_project.rabbit_config import mq_settings
from app_project.producer.producer_repository import ProducerRepository

logger = logging.getLogger(__name__)


class RabbitMQProducer:
    def __init__(self):
        self.connection = None
        self.channel = None
        self.queue_name = mq_settings.RABBITMQ_QUEUE

    def connect(self):
        credentials = pika.PlainCredentials(
            mq_settings.RABBITMQ_USER,
            mq_settings.RABBITMQ_PASSWORD
        )
        parameters = pika.ConnectionParameters(
            host=mq_settings.RABBITMQ_HOST,
            port=mq_settings.RABBITMQ_PORT,
            credentials=credentials,
            heartbeat=600,
            blocked_connection_timeout=300
        )

        self.connection = pika.BlockingConnection(parameters)

        self.channel = self.connection.channel()

        self.channel.exchange_declare(
            exchange=mq_settings.RABBITMQ_EXCHANGE,
            exchange_type='direct',
            durable=True
        )

        self.channel.queue_declare(queue=self.queue_name, durable=True)

        self.channel.queue_bind(
            exchange=mq_settings.RABBITMQ_EXCHANGE,
            queue=self.queue_name,
            routing_key=self.queue_name
        )

    def publish_message(self, message: dict):
        if not self.connection or self.connection.is_closed:
            self.connect()

        try:
            self.channel.basic_publish(
                exchange=mq_settings.RABBITMQ_EXCHANGE,
                routing_key=self.queue_name,
                body=json.dumps(message),
                properties=pika.BasicProperties(delivery_mode=2)
            )

            return True
        except Exception as e:
            logger.error(f"Unexpected error: {e}")
            self.reconnect()
            return False

    def reconnect(self):
        if self.connection:
            self.connection.close()
        self.connect()

    def close(self):
        if self.connection and not self.connection.is_closed:
            self.connection.close()


async def producer_worker():
    producer = RabbitMQProducer()
    producer.connect()
    repo = ProducerRepository()

    try:
        while True:
            async with session_context() as session:
                try:
                    tasks = await repo.get_new_tasks(session)

                    if tasks:
                        task_ids = []
                        for task in tasks:
                            if task.status == Status.CANCELLED:
                                continue

                            message = {
                                "id": task.id,
                                "title": task.title,
                                "description": task.description,
                                "priority": task.priority,
                                "status": task.status,
                            }

                            if producer.publish_message(message):
                                task_ids.append(task.id)

                        if task_ids:
                            await repo.update_status_to_pending(session, task_ids)

                except Exception as e:
                    logger.error(f"Unexpected error: {e}")
                    await session.rollback()

            await asyncio.sleep(mq_settings.PRODUCER_INTERVAL)

    except KeyboardInterrupt:
        logger.info("Producer stopped")
    except Exception as e:
        logger.error(f"Unexpected error: {e}")
    finally:
        producer.close()


if __name__ == "__main__":
    asyncio.run(producer_worker())
