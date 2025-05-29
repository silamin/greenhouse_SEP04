import os, socket

HOST = os.getenv("DEVICE_HOST", "127.0.0.1")
PORT = int(os.getenv("DEVICE_PORT", 1234))

class CommandSender:
    def __init__(self):
        self._connect()

    def _connect(self):
        self.sock = socket.create_connection((HOST, PORT), timeout=5)
        self.sock.settimeout(2)

    def send(self, payload: str):
        try:
            self.sock.sendall(payload.encode())
        except Exception:
            self.sock.close()
            self._connect()
            self.sock.sendall(payload.encode())
