from __future__ import annotations

import json
import os
from http import HTTPStatus
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from urllib.parse import parse_qs, urlparse

from uv_service import (
    PostcodeNotFoundError,
    get_citywise_uv,
    get_hourly_forecast,
    get_realtime_uv,
    get_weekly_forecast,
)


class UVRequestHandler(BaseHTTPRequestHandler):
    server_version = "UVAPI/1.0"

    def do_GET(self) -> None:
        parsed = urlparse(self.path)
        query = parse_qs(parsed.query)
        postcode = query.get("postcode", [None])[0]

        try:
            if parsed.path == "/api/health":
                self._send_json(HTTPStatus.OK, {"status": "ok"})
                return
            if parsed.path == "/api/uv/realtime":
                self._send_json(HTTPStatus.OK, get_realtime_uv(postcode=postcode))
                return
            if parsed.path == "/api/uv/hourly":
                self._send_json(HTTPStatus.OK, get_hourly_forecast(postcode=postcode))
                return
            if parsed.path == "/api/uv/weekly":
                self._send_json(HTTPStatus.OK, get_weekly_forecast(postcode=postcode))
                return
            if parsed.path == "/api/uv/citywise":
                self._send_json(HTTPStatus.OK, get_citywise_uv())
                return
            self._send_json(HTTPStatus.NOT_FOUND, {"error": "Route not found."})
        except PostcodeNotFoundError as exc:
            self._send_json(HTTPStatus.NOT_FOUND, {"error": str(exc)})
        except ValueError as exc:
            self._send_json(HTTPStatus.BAD_REQUEST, {"error": str(exc)})
        except Exception as exc:  # pragma: no cover
            self._send_json(HTTPStatus.INTERNAL_SERVER_ERROR, {"error": str(exc)})

    def log_message(self, format: str, *args) -> None:
        return

    def _send_json(self, status: HTTPStatus, payload: object) -> None:
        body = json.dumps(payload, ensure_ascii=True).encode("utf-8")
        self.send_response(status.value)
        self.send_header("Content-Type", "application/json; charset=utf-8")
        self.send_header("Content-Length", str(len(body)))
        self.send_header("Access-Control-Allow-Origin", "*")
        self.end_headers()
        self.wfile.write(body)


def run() -> None:
    port = int(os.getenv("PORT", "8000"))
    server = ThreadingHTTPServer(("0.0.0.0", port), UVRequestHandler)
    print(f"UV API server listening on http://127.0.0.1:{port}")
    server.serve_forever()


if __name__ == "__main__":
    run()
