import json
from datetime import datetime

from domain.entities import SensorReading, DeviceCommand, GreenhouseSettings
from adapters.api_client import APIClient
from use_cases.command_service import CommandService

class SensorService:
    def __init__(self, cmd_svc: CommandService, api_client: APIClient):
        self.cmd_svc = cmd_svc
        self.api = api_client

    async def process_incoming_json(self, raw: str, owner: str):
        d = json.loads(raw)
        acc = d.get("acc", [0, 0, 0])

        reading = SensorReading(
            timestamp=datetime.utcnow(),
            temp=d["temp"],
            hum=d["hum"],
            soil=d["soil"],
            light=d["light"],
            dist=d["dist"],
            motion=d.get("motion", False),
            acc_x=acc[0],
            acc_y=acc[1],
            acc_z=acc[2],
        )

        # 1) send sensor reading to API
        await self.api.send_reading(reading)

        # 2) fetch settings via API & apply threshold logic
        settings = await self.api.get_settings(owner)
        if settings:
            self._check_thresholds(reading, settings)

        return reading

    def _check_thresholds(self, r: SensorReading, s: GreenhouseSettings):
        # Overheat
        if r.temp > s.temp_max:
            for _ in range(2):
                self.cmd_svc.send_command(DeviceCommand("LED", "1 TOGGLE"))
            self.cmd_svc.send_command(DeviceCommand("BUZZER", "BEEP"))
        # Freezing
        elif r.temp < s.temp_min:
            self.cmd_svc.send_command(DeviceCommand("BUZZER", "BEEP"))

        # Humidity
        if r.hum < s.hum_min:
            self.cmd_svc.send_command(DeviceCommand("BUZZER", "BEEP"))
            self.cmd_svc.send_command(DeviceCommand("LED", "1 ON"))
        elif r.hum > s.hum_max:
            self.cmd_svc.send_command(DeviceCommand("LED", "1 TOGGLE"))

        # Soil
        if r.soil < s.soil_min:
            self.cmd_svc.send_command(DeviceCommand("SERVO", "0"))
        elif r.soil > s.soil_min + 100:
            self.cmd_svc.send_command(DeviceCommand("SERVO", "90"))

        # Light
        if r.light < s.light_min:
            self.cmd_svc.send_command(DeviceCommand("LED", "2 ON"))
        elif r.light > s.light_max:
            self.cmd_svc.send_command(DeviceCommand("LED", "2 OFF"))

        # Motion
        if r.motion:
            self.cmd_svc.send_command(DeviceCommand("BUZZER", "BEEP"))
            self.cmd_svc.send_command(DeviceCommand("LED", "3 TOGGLE"))

        # Always display the current temperature
        self.cmd_svc.send_command(DeviceCommand("DISPLAY", str(int(r.temp))))
