from datetime import datetime

from common.models import DeviceCommand


class CommandService:
    def __init__(self, sender): self.sender = sender

    def send_command(self, cmd: DeviceCommand):
        cmd.timestamp = datetime.utcnow()
        self.sender.send(f"{cmd.device} {cmd.action}\n")
        return cmd
