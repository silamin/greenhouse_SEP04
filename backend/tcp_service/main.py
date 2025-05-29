import asyncio
import logging
from frameworks.tcp_server import run_server

logging.basicConfig(level=logging.INFO)
if __name__ == "__main__":
    asyncio.run(run_server())
