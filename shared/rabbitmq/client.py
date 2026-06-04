# =============================================================================
# shared/rabbitmq/client.py
# =============================================================================
# Shared RabbitMQ connection manager used by all microservices.
#
# Handles:
#   - Robust connection (auto-reconnects on drop)
#   - Exchange declaration (idempotent)
#   - Channel management
#   - Clean shutdown
#
# Usage (in any service):
#   from shared.rabbitmq.client import (
#       init_rabbitmq, close_rabbitmq,
#       get_exchange, get_channel
#   )
#
#   # Startup:
#   await init_rabbitmq()
#
#   # Publishing:
#   exchange = get_exchange()
#   await exchange.publish(message, routing_key="video.ingested")
#
#   # Consuming:
#   channel = get_channel()
#   queue = await channel.declare_queue("my.queue", durable=True)
#   await queue.bind(get_exchange(), routing_key="video.ingested")
#   await queue.consume(my_handler)
#
#   # Shutdown:
#   await close_rabbitmq()
# =============================================================================

import aio_pika
import os
import logging

logger = logging.getLogger(__name__)

EXCHANGE_NAME = "sfn.events"

_connection: aio_pika.RobustConnection = None
_channel: aio_pika.Channel = None
_exchange: aio_pika.Exchange = None


async def init_rabbitmq(prefetch_count: int = 1):
    """
    Connect to RabbitMQ and declare the sfn.events exchange.
    Called once at service startup from main.py lifespan.

    Uses connect_robust which automatically reconnects if the
    connection drops — essential for long-running services.

    Args:
        prefetch_count: max unacked messages per consumer (default 1)
                        set higher for publisher-only services
    """
    global _connection, _channel, _exchange

    url = os.getenv("RABBITMQ_URL", "amqp://sfn:sfn_pass@localhost:5672/")

    _connection = await aio_pika.connect_robust(url)
    _channel = await _connection.channel()

    # Limit unacked messages — prevents one slow worker hoarding the queue
    await _channel.set_qos(prefetch_count=prefetch_count)

    # Declare the exchange — idempotent, safe to call on every startup
    # All services share the same exchange — different routing keys
    _exchange = await _channel.declare_exchange(
        EXCHANGE_NAME,
        aio_pika.ExchangeType.TOPIC,
        durable=True,   # survives RabbitMQ restarts
    )

    logger.info(
        f"RabbitMQ connected — "
        f"exchange={EXCHANGE_NAME}"
    )


async def close_rabbitmq():
    """
    Close RabbitMQ connection gracefully on service shutdown.
    Waits for in-flight messages to complete before closing.
    """
    global _connection, _channel, _exchange
    if _connection and not _connection.is_closed:
        await _connection.close()
        _connection = None
        _channel = None
        _exchange = None
        logger.info("RabbitMQ connection closed")


def get_exchange() -> aio_pika.Exchange:
    """
    Get the declared sfn.events exchange for publishing.
    Call init_rabbitmq() before using this.
    """
    if _exchange is None:
        raise RuntimeError(
            "RabbitMQ not initialised — call init_rabbitmq() first"
        )
    return _exchange


def get_channel() -> aio_pika.Channel:
    """
    Get the active channel for queue declaration and consuming.
    Call init_rabbitmq() before using this.
    """
    if _channel is None:
        raise RuntimeError(
            "RabbitMQ not initialised — call init_rabbitmq() first"
        )
    return _channel


async def publish(routing_key: str, body: bytes):
    """
    Convenience method to publish a persistent message.

    Args:
        routing_key : e.g. "video.ingested", "angle.extracted"
        body        : JSON-encoded bytes e.g. event.model_dump_json().encode()
    """
    exchange = get_exchange()
    message = aio_pika.Message(
        body=body,
        content_type="application/json",
        delivery_mode=aio_pika.DeliveryMode.PERSISTENT,
    )
    await exchange.publish(message, routing_key=routing_key)
    logger.debug(f"Published to {routing_key}")
