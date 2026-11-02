import json
import os
import threading
from collections.abc import Callable
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer


class HealthServer(ThreadingHTTPServer):
    daemon_threads = True

    def __init__(self, port: int, connected: Callable[[], bool]) -> None:
        self.connected = connected
        super().__init__(("127.0.0.1", port), _HealthHandler)
        self.thread = threading.Thread(target=self.serve_forever, daemon=True)
        self.thread.start()

    def stop(self) -> None:
        self.shutdown()
        self.server_close()
        self.thread.join(timeout=5)


class _HealthHandler(BaseHTTPRequestHandler):
    def do_GET(self) -> None:
        if self.path != "/healthz":
            self.send_response(404)
            self.end_headers()
            return
        ok = bool(self.server.connected())
        body = json.dumps({"ok": ok, "socket": ok}).encode()
        self.send_response(200 if ok else 503)
        self.send_header("Content-Type", "application/json")
        self.send_header("Content-Length", str(len(body)))
        self.end_headers()
        self.wfile.write(body)

    def log_message(self, format: str, *args: object) -> None:
        pass


def start_from_env(connected: Callable[[], bool]) -> None:
    port = os.environ.get("BOT_HEALTH_PORT", "").strip()
    if not port:
        return
    HealthServer(int(port), connected)
