import asyncio, json, logging

from tcp_service.frameworks.command_sender import CommandSender
from tcp_service.use_cases.command_service import CommandService
from tcp_service.use_cases.sensor_service import SensorService
from tcp_service.frameworks.settings_proxy import SettingsProxy  # still read‑only

log = logging.getLogger("tcp_server")


async def _handle(reader: asyncio.StreamReader, writer: asyncio.StreamWriter):
    svc = SensorService(CommandService(CommandSender()), SettingsProxy())
    peer = writer.get_extra_info("peername")
    log.info("Client %s connected", peer)

    while not reader.at_eof():
        try:
            raw = await asyncio.wait_for(reader.readline(), timeout=30)
            if not raw:
                break
            await svc.process_incoming_json(raw.decode().strip(), "alice")
        except json.JSONDecodeError:
            log.warning("Bad JSON from %s", peer)
        except asyncio.TimeoutError:
            log.warning("Timeout from %s", peer)
        except Exception as e:
            log.exception("Unexpected: %s", e)

    writer.close()
    await writer.wait_closed()
    log.info("Client %s disconnected", peer)


async def run_server():
    server = await asyncio.start_server(_handle, "0.0.0.0", 9000)
    for s in server.sockets:
        log.info("TCP listening on %s", s.getsockname())
    async with server:
        await server.serve_forever()
