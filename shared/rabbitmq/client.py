import aio_pika
import os

RABBITMQ_URL = os.getenv("RABBITMQ_URL", "amqp://sfn:sfn_pass@localhost:5672/")


async def get_connection():
    return await aio_pika.connect_robust(RABBITMQ_URL)


async def get_channel(connection):
    return await connection.channel()
