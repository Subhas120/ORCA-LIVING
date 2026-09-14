"""
ORCA M2 HTTP API

Thin HTTP adapter around the existing M2 Ocean Agent.

This file does NOT implement new ocean science or
decision logic. It only converts HTTP JSON requests
into AgentRequest objects and returns the existing
AgentResponse as JSON for M3.

Run from the repository root:

    python -m backend.api.server

Endpoint:

    POST http://127.0.0.1:8000/api/ocean

Health:

    GET http://127.0.0.1:8000/api/health
"""

import json
from http.server import BaseHTTPRequestHandler
from http.server import ThreadingHTTPServer

from agents.common.agent_contract import AgentRequest
from agents.ocean.ocean_agent import handle_ocean


HOST = "127.0.0.1"
PORT = 8000


class OrcaAPIHandler(BaseHTTPRequestHandler):
    """HTTP adapter for the existing M2 Ocean Agent."""

    def _send_json(self, status_code, payload):
        body = json.dumps(payload).encode("utf-8")

        self.send_response(status_code)

        self.send_header(
            "Content-Type",
            "application/json",
        )

        self.send_header(
            "Content-Length",
            str(len(body)),
        )

        self.send_header(
            "Access-Control-Allow-Origin",
            "http://localhost:5173",
        )

        self.send_header(
            "Access-Control-Allow-Methods",
            "GET, POST, OPTIONS",
        )

        self.send_header(
            "Access-Control-Allow-Headers",
            "Content-Type",
        )

        self.end_headers()

        self.wfile.write(body)

    def do_OPTIONS(self):
        self._send_json(204, {})

    def do_GET(self):

        if self.path == "/api/health":

            self._send_json(
                200,
                {
                    "status": "ok",
                    "service": "orca-m2-ocean",
                },
            )

            return

        self._send_json(
            404,
            {
                "status": "error",
                "error": "Endpoint not found",
            },
        )

    def do_POST(self):

        if self.path != "/api/ocean":

            self._send_json(
                404,
                {
                    "status": "error",
                    "error": "Endpoint not found",
                },
            )

            return

        try:

            content_length = int(
                self.headers.get(
                    "Content-Length",
                    "0",
                )
            )

            raw_body = self.rfile.read(
                content_length
            )

            payload = json.loads(
                raw_body or b"{}"
            )

            if not isinstance(
                payload,
                dict,
            ):
                raise ValueError(
                    "Request body must be a JSON object"
                )

            request = AgentRequest(
                query=payload.get(
                    "query",
                    "",
                ),
                location=payload.get(
                    "location"
                ),
                destination=payload.get(
                    "destination"
                ),
                date=payload.get(
                    "date"
                ),
                time=payload.get(
                    "time"
                ),
                activity=payload.get(
                    "activity"
                ),
            )

            response = handle_ocean(
                request
            )

            self._send_json(
                200,
                {
                    "agent": response.agent,
                    "status": response.status,
                    "data": response.data,
                    "source": response.source,
                    "timestamp": response.timestamp,
                    "location": response.location,
                    "confidence": response.confidence,
                    "error": response.error,
                },
            )

        except json.JSONDecodeError:

            self._send_json(
                400,
                {
                    "status": "error",
                    "error": "Invalid JSON request body",
                },
            )

        except (
            TypeError,
            ValueError,
        ) as exc:

            self._send_json(
                400,
                {
                    "status": "error",
                    "error": str(exc),
                },
            )

        except Exception as exc:

            self._send_json(
                500,
                {
                    "status": "error",
                    "error": str(exc),
                },
            )

    def log_message(
        self,
        format_string,
        *args,
    ):
        """Keep server logs compact and readable."""

        print(
            f"[{self.address_string()}] "
            f"{format_string % args}"
        )


def main():

    server = ThreadingHTTPServer(
        (
            HOST,
            PORT,
        ),
        OrcaAPIHandler,
    )

    print(
        "ORCA M2 API running at "
        f"http://{HOST}:{PORT}"
    )

    print(
        "POST /api/ocean"
    )

    print(
        "GET  /api/health"
    )

    try:

        server.serve_forever()

    except KeyboardInterrupt:

        print(
            "\nStopping ORCA M2 API..."
        )

    finally:

        server.server_close()


if __name__ == "__main__":

    main()