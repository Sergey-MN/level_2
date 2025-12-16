import asyncio
import json
import logging
from random import randint

from aio_pika import connect_robust, IncomingMessage

from app_project.consumer.consumer_repository import ConsumerRepository
from app_project.models.models import Tasks, Status
from app_project.rabbit_config import mq_settings
from app_project.database import session_context

logger = logging.getLogger(__name__)


class TaskCancelled(Exception):
    pass


async def process_task(task_data: dict) -> bool:
    repo = ConsumerRepository()

    try:
        task_id = task_data.get("id")
        data = task_data.get("description", "")

        async with session_context() as session:

            task = await session.get(Tasks, task_id)
            if task.status == Status.CANCELLED:
                raise TaskCancelled(f"Task {task_id} cancelled")

            await repo.update_to_in_progress(session, task_id)

            await asyncio.sleep(randint(1, 7))

            await repo.update_to_completed(session, task_id)

        return True

    except TaskCancelled:
        raise

    except Exception as e:
        logger.error(f"Unexpected error: {e}")

        await repo.update_to_failed(task_data.get("id"), e)

        return False


class RabbitMQConsumer:
    def __init__(self):
        self.queue_name = mq_settings.RABBITMQ_QUEUE
        self.connection = None
        self.channel = None
        self.queue = None
        self.is_consuming = False

    async def connect(self):
        self.connection = await connect_robust(
            host=mq_settings.RABBITMQ_HOST,
            port=mq_settings.RABBITMQ_PORT,
            login=mq_settings.RABBITMQ_USER,
            password=mq_settings.RABBITMQ_PASSWORD,
            virtualhost="/"
        )

        self.channel = await self.connection.channel()

        await self.channel.set_qos(prefetch_count=1)

    async def setup_queue(self):
        self.queue = await self.channel.declare_queue(
            self.queue_name,
            durable=True
        )

    async def process_message(self, message: IncomingMessage):
        async with message.process():
            try:
                task_data = json.loads(message.body.decode())
                success = await process_task(task_data)

            except TaskCancelled as e:
                logger.info(f"Task cancelled: {e}")

            except json.JSONDecodeError as e:
                logger.error(f"Message is not JSON: {e}")

            except Exception as e:
                logger.error(f"Unexpected error: {e}")

                repo = ConsumerRepository()
                await repo.update_to_failed(task_data.get("id"), e)

                raise

    async def start_consuming(self):
        if not self.connection:
            await self.connect()
        if not self.queue:
            await self.setup_queue()

        self.is_consuming = True

        try:
            await self.queue.consume(self.process_message)

            await asyncio.Future()

        except KeyboardInterrupt:
            logger.info("Consumer stopped")

        except Exception as e:
            logger.error(f"Unexpected error: {e}")
            raise

        finally:
            self.is_consuming = False
            await self.close()

    async def close(self):
        if self.connection and not self.connection.is_closed:
            await self.connection.close()


async def start_consumer():
    consumer = RabbitMQConsumer()
    await consumer.start_consuming()


if __name__ == "__main__":
    asyncio.run(start_consumer())
