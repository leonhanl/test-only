"""A tiny web application for learning GitHub Actions and containers."""

import json
import os
from functools import partial
from html import escape
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
from urllib.parse import urlsplit


class Handler(BaseHTTPRequestHandler):
    def __init__(self, *args, config, **kwargs):
        self.config = config
        super().__init__(*args, **kwargs)

    def do_GET(self):
        path = urlsplit(self.path).path
        if path == "/":
            message = escape(self.config["message"])
            body = (
                '<!doctype html><html lang="en"><meta charset="utf-8">'
                '<title>Python CI Demo</title>'
                f"<h1>{message}</h1><p>Built with GitHub Actions.</p></html>"
            ).encode("utf-8")
            content_type = "text/html; charset=utf-8"
            status = 200
        elif path == "/health":
            body = b'{"status": "ok"}'
            content_type = "application/json"
            status = 200
        else:
            body = b"Not found\n"
            content_type = "text/plain; charset=utf-8"
            status = 404

        self.send_response(status)
        self.send_header("Content-Type", content_type)
        self.send_header("Content-Length", str(len(body)))
        self.end_headers()
        self.wfile.write(body)


def create_server(host="0.0.0.0", port=8000, config_path=None):
    path = Path(config_path) if config_path else Path(__file__).parent / "config/app.json"
    config = json.loads(path.read_text(encoding="utf-8"))
    return ThreadingHTTPServer((host, port), partial(Handler, config=config))


if __name__ == "__main__":
    with create_server(config_path=os.environ.get("APP_CONFIG")) as server:
        print("Listening on http://0.0.0.0:8000", flush=True)
        try:
            server.serve_forever()
        except KeyboardInterrupt:
            pass
