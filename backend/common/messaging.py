import asyncio
import logging
import json

import nats
from nats.aio.client import Client as NATS
from nats.errors import NoServersError
from nats.js.api import StorageType, StreamConfig

# Logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

nc: NATS = None
js = None

STREAM_NAME = "SENSOR_READINGS"
SUBJECT = "SENSOR_READINGS"

async def wait_for_nats(
    url: str,
    retries: int = 5,
    timeout: float = 5.0,
    backoff_base: float = 1.0
) -> NATS:
    for attempt in range(1, retries + 1):
        try:
            return await nats.connect(
                servers=[url],
                connect_timeout=timeout,
                reconnect=False
            )
        except (NoServersError, asyncio.TimeoutError) as e:
            logger.warning(
                "NATS connect failed (attempt %d/%d): %s",
                attempt, retries, e
            )
            if attempt == retries:
                logger.error("All NATS connection attempts failed.")
                raise
            await asyncio.sleep(backoff_base * 2 ** (attempt - 1))

async def init_nats():
    global nc, js
    try:
        # ←—— LOCALHOST instead of ELB
        nc = await wait_for_nats("nats://127.0.0.1:4222")
        logger.info("Connected to NATS at %s", nc.connected_url)

        js = nc.jetstream()
        stream_cfg = StreamConfig(
            name=STREAM_NAME,
            subjects=[SUBJECT],
            max_age=7 * 24 * 60 * 60,
            storage=StorageType.FILE
        )

        try:
            info = await js.add_stream(stream_cfg)
            logger.info("Stream %s created: %s", STREAM_NAME, info.config.__dict__)
        except Exception:
            logger.debug("Stream %s already exists", STREAM_NAME)

        await js.subscribe(
            SUBJECT,
            durable="sensor_reader",
            cb=message_handler,
            manual_ack=True
        )
        logger.info("Subscribed to %s", SUBJECT)

    except Exception as e:
        logger.error("Failed to init NATS/JetStream: %s", e)
        raise

async def message_handler(msg):
    data = msg.data.decode()
    logger.info("Received on '%s': %s", msg.subject, data)
    await msg.ack()

def build_handler(persist_func):
    async def handler(msg):
        data = msg.data.decode()
        logger.info("Handling message: %s", data)
        try:
            payload = json.loads(data)
            await persist_func(payload)
        except json.JSONDecodeError as e:
            logger.error("JSON parse error: %s", e)
        await msg.ack()
    return handler

async def publish_reading(reading: dict):
    global nc, js
    if nc is None or js is None:
        await init_nats()
    try:
        await js.publish(SUBJECT, json.dumps(reading).encode())
        logger.info("Published reading: %s", reading)
    except Exception as e:
        logger.error("Publish failed: %s", e)

async def close_nats():
    global nc
    if nc:
        await nc.drain()
        logger.info("NATS connection closed")

# Example:
# asyncio.run(init_nats())
# asyncio.run(publish_reading({"temp":25.1}))
# asyncio.run(close_nats())
