"""Handle incoming packets → publish to NATS and handle local alarms."""
import json
from datetime import datetime
from dataclasses import asdict

from common.messaging import publish_reading
from common.models import SensorReading, DeviceCommand
from tcp_service.use_cases.command_service import CommandService


class SensorService:
    def __init__(self, cmd_svc: CommandService, settings_proxy):
        self.cmd_svc = cmd_svc
        self.set_proxy = settings_proxy  # read‑only → still shared DB is fine

    # ---------------------------------------------------------------------
    # processing chain
    # ---------------------------------------------------------------------
    async def process_incoming_json(self, raw: str, owner: str):
        """Validate JSON, raise on errors, publish to stream, trigger alarms."""
        d = json.loads(raw)
        acc = d.get("acc", [0, 0, 0])

        r = SensorReading(
            id=None,
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

        # ① publish to NATS
        await publish_reading(asdict(r) | {"owner": owner})

        # ② evaluate thresholds and respond
        self._check_thresholds(r, owner)
        return r

    # ---------------------------------------------------------------------
    # threshold logic: LED, buzzer, servo, display
    # ---------------------------------------------------------------------
    def _check_thresholds(self, saved: SensorReading, owner: str):
        s = self.set_proxy.get(owner)
        if not s:
            return

        # --- Overheat alert
        if saved.temp > s.temp_max:
            for _ in range(2):
                self.cmd_svc.send_command(DeviceCommand("LED", "1 TOGGLE"))
            self.cmd_svc.send_command(DeviceCommand("BUZZER", "BEEP"))

        # --- Freezing alert
        elif saved.temp < s.temp_min:
            self.cmd_svc.send_command(DeviceCommand("BUZZER", "BEEP"))

        # --- Humidity too low or too high
        if saved.hum < s.hum_min:
            self.cmd_svc.send_command(DeviceCommand("BUZZER", "BEEP"))
            self.cmd_svc.send_command(DeviceCommand("LED", "1 ON"))  # use LED 1 for warning
        elif saved.hum > s.hum_max:
            self.cmd_svc.send_command(DeviceCommand("LED", "1 TOGGLE"))

        # --- Soil too dry → open valve via servo
        if saved.soil < s.soil_min:
            self.cmd_svc.send_command(DeviceCommand("SERVO", "0"))  # fully open valve
        elif saved.soil > s.soil_min + 100:  # add hysteresis
            self.cmd_svc.send_command(DeviceCommand("SERVO", "90"))  # neutral (close valve)

        # --- Too dark → turn on LED 2
        if saved.light < s.light_min:
            self.cmd_svc.send_command(DeviceCommand("LED", "2 ON"))
        elif saved.light > s.light_max:
            self.cmd_svc.send_command(DeviceCommand("LED", "2 OFF"))

        # --- Motion detected → beep + LED alert
        if saved.motion:
            self.cmd_svc.send_command(DeviceCommand("BUZZER", "BEEP"))
            self.cmd_svc.send_command(DeviceCommand("LED", "3 TOGGLE"))

        # --- Show temperature on display (rounded)
        self.cmd_svc.send_command(DeviceCommand("DISPLAY", str(int(saved.temp))))
