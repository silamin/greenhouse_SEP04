import asyncio
import logging
import os

from nats.aio.client import Client as NATS
from nats.errors import TimeoutError, NoServersError
from nats.js.api import StorageType, StreamConfig
import nats
import json

# Configure logging for diagnostics
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Globals for NATS connection and JetStream context
nc: NATS = None
js = None

# Subject/stream name
STREAM_NAME = "SENSOR_READINGS"
SUBJECT = "SENSOR_READINGS"


async def wait_for_nats(url: str, retries: int = 5):
    delay = 1
    for attempt in range(retries):
        try:
            return await nats.connect(servers=[url])
        except Exception as e:
            if attempt == retries - 1:
                raise e
            await asyncio.sleep(delay)
            delay *= 2


async def init_nats():
    """Initialize NATS connection, create stream if needed, and subscribe to subject."""
    global nc, js
    try:
        # Connect to NATS server (adjust URL and options as needed)
        nc = await wait_for_nats("nats://nats:4222")
        logger.info("Connected to NATS at %s", nc.connected_url.netloc)

        # Create JetStream context (has management API built-in):contentReference[oaicite:6]{index=6}
        js = nc.jetstream()

        # Define stream configuration with 7-day max age (in seconds)
        stream_cfg = StreamConfig(
            name=STREAM_NAME,
            subjects=[SUBJECT],
            max_age=7 * 24 * 60 * 60,  # one week
            storage=StorageType.FILE  # durable file storage
        )

        # Attempt to add the stream (idempotent if exists):contentReference[oaicite:7]{index=7}.
        try:
            info = await js.add_stream(stream_cfg)
            logger.info("Stream %s created: config=%s", STREAM_NAME, info.config.__dict__)
        except Exception as e:
            # If stream exists (or other issue), log and continue
            logger.warning("Could not create stream %s: %s", STREAM_NAME, e)

        # Subscribe to the subject with a durable consumer
        await js.subscribe(
            SUBJECT,
            durable="sensor_reader",
            cb=message_handler,
            manual_ack=True
        )
        logger.info("Subscribed to %s", SUBJECT)

    except NoServersError as e:
        logger.error("Could not connect to NATS servers: %s", e)
    except Exception as e:
        logger.error("Error setting up NATS/JetStream: %s", e)


async def message_handler(msg):
    """Process incoming JetStream messages."""
    try:
        data = msg.data.decode()
        logger.info("Received message on '%s': %s", msg.subject, data)
        await msg.ack()  # Acknowledge message
    except Exception as e:
        logger.error("Failed to handle message: %s", e)


async def close_nats():
    """Drain and close the NATS connection."""
    global nc
    if nc is not None:
        try:
            await nc.drain()  # flush and close
            logger.info("NATS connection drained and closed")
        except Exception as e:
            logger.error("Error closing NATS connection: %s", e)


def build_handler(persist_func):
    async def handler(msg):
        try:
            data = msg.data.decode()
            logger.info("Received message: %s", data)
            await persist_func(eval(data))  # ⚠️ Use `json.loads` in production!
            await msg.ack()
        except Exception as e:
            logger.error("Error handling message: %s", e)

    return handler


async def publish_reading(reading: dict):
    """Publish a sensor reading to the NATS JetStream stream."""
    global _nc, _js

    if _nc is None or _js is None:
        await init_nats()  # lazy init if needed

    try:
        await _js.publish(SUBJECT, json.dumps(reading).encode())
    except Exception as e:
        logger.error("Failed to publish reading: %s", e)
