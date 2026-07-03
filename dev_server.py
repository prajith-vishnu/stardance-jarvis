import json
import os
import sys
from http.server import HTTPServer, SimpleHTTPRequestHandler
from urllib.parse import urlparse, parse_qs

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from api._core import FEEDS, jarvis_reply

env_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), ".env")
if os.path.exists(env_path):
    with open(env_path) as f:
        for line in f:
            line = line.strip()
            if line and not line.startswith("#") and "=" in line:
                k, _, v = line.partition("=")
                os.environ.setdefault(k.strip(), v.strip().strip('"').strip("'"))


class DevHandler(SimpleHTTPRequestHandler):
    def _json(self, status, payload):
        body = json.dumps(payload).encode()
        self.send_response(status)
        self.send_header("Content-Type", "application/json")
        self.send_header("Content-Length", str(len(body)))
        self.end_headers()
        self.wfile.write(body)

    def do_GET(self):
        parsed = urlparse(self.path)
        if parsed.path == "/api/feeds":
            name = (parse_qs(parsed.query).get("feed") or [""])[0]
            if name not in FEEDS:
                return self._json(400, {"error": f"Unknown feed '{name}'"})
            key = os.environ.get("NASA_API_KEY", "")
            if not key:
                return self._json(500, {"error": "NASA_API_KEY missing in .env"})
            try:
                return self._json(200, {"feed": name, "data": FEEDS[name][0](key)})
            except Exception as e:
                return self._json(502, {"error": f"{name} failed: {type(e).__name__}: {e}"})
        return super().do_GET()

    def do_POST(self):
        if urlparse(self.path).path == "/api/chat":
            key = os.environ.get("GEMINI_API_KEY", "")
            if not key:
                return self._json(500, {"error": "GEMINI_API_KEY missing in .env"})
            length = int(self.headers.get("Content-Length") or 0)
            body = json.loads(self.rfile.read(length) or b"{}")
            try:
                reply = jarvis_reply(body.get("prompt", ""), body.get("context", ""), key)
                return self._json(200, {"reply": reply})
            except Exception as e:
                return self._json(502, {"error": f"chat failed: {type(e).__name__}: {e}"})
        return self._json(404, {"error": "not found"})


if __name__ == "__main__":
    port = int(sys.argv[1]) if len(sys.argv) > 1 else 8899
    print(f"JARVIS dev server on http://localhost:{port}")
    HTTPServer(("127.0.0.1", port), DevHandler).serve_forever()
