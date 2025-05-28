import asyncio
import logging
import json
from nats.aio.client import Client as NATS
from nats.errors import NoServersError
from nats.js.api import StorageType, StreamConfig
import nats

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
            logger.warning("NATS connect failed (attempt %d): %s", attempt + 1, e)
            await asyncio.sleep(delay)
            delay *= 2

async def init_nats():
    """Initialize NATS connection, create stream if needed, and subscribe to subject."""
    global nc, js
    try:
        # CORRECTED: use nats:// and single colon before port
        nc = await wait_for_nats("nats://api-tg-1598256574.eu-north-1.elb.amazonaws.com:4222")
        logger.info("Connected to NATS at %s", nc.connected_url)

        # Create JetStream context
        js = nc.jetstream()

        # Define stream configuration with 7-day max age
        stream_cfg = StreamConfig(
            name=STREAM_NAME,
            subjects=[SUBJECT],
            max_age=7 * 24 * 60 * 60,  # one week
            storage=StorageType.FILE
        )

        # Attempt to add the stream (idempotent)
        try:
            info = await js.add_stream(stream_cfg)
            logger.info("Stream %s created: %s", STREAM_NAME, info.config.__dict__)
        except Exception as e:
            logger.warning("Could not create stream %s (maybe exists): %s", STREAM_NAME, e)

        # Subscribe with a durable consumer
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
        await msg.ack()
    except Exception as e:
        logger.error("Failed to handle message: %s", e)

def build_handler(persist_func):
    async def handler(msg):
        try:
            data = msg.data.decode()
            logger.info("Received message: %s", data)
            # SAFE PARSING instead of eval
            payload = json.loads(data)
            await persist_func(payload)
            await msg.ack()
        except Exception as e:
            logger.error("Error handling message: %s", e)
    return handler

async def publish_reading(reading: dict):
    """Publish a sensor reading to the NATS JetStream stream."""
    global nc, js
    if nc is None or js is None:
        await init_nats()  # lazy init if needed

    try:
        await js.publish(SUBJECT, json.dumps(reading).encode())
        logger.info("Published reading to %s: %s", SUBJECT, reading)
    except Exception as e:
        logger.error("Failed to publish reading: %s", e)

async def close_nats():
    """Drain and close the NATS connection."""
    global nc
    if nc is not None:
        try:
            await nc.drain()
            logger.info("NATS connection drained and closed")
        except Exception as e:
            logger.error("Error closing NATS connection: %s", e)

# Example usage:
# asyncio.run(init_nats())
# asyncio.run(publish_reading({"temperature": 22.5, "humidity": 55}))
# asyncio.run(close_nats())
