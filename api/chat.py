# POST /api/chat
import json
from http.server import BaseHTTPRequestHandler

try:
    from api._core import jarvis_reply, get_env
except ImportError:
    from _core import jarvis_reply, get_env


class handler(BaseHTTPRequestHandler):
    def do_POST(self):
        gemini_key = get_env("GEMINI_API_KEY")
        if not gemini_key:
            return self._send(500, {"error": "GEMINI_API_KEY is not configured. Add it in Vercel → Project → Settings → Environment Variables, then redeploy."})

        try:
            length = int(self.headers.get("Content-Length") or 0)
            body = json.loads(self.rfile.read(length) or b"{}")
        except (ValueError, json.JSONDecodeError):
            return self._send(400, {"error": "Invalid JSON body."})

        prompt = (body.get("prompt") or "").strip()[:4000]
        context = (body.get("context") or "telemetry unavailable").strip()[:2000]
        if not prompt:
            return self._send(400, {"error": "Missing 'prompt'."})

        try:
            reply = jarvis_reply(prompt, context, gemini_key)
        except Exception:
            reply = ("Telemetry bottleneck — rate limit reached. "
                     "Please allow ~30 seconds for the relay matrix to clear.")
        self._send(200, {"reply": reply})

    def _send(self, status, payload):
        body = json.dumps(payload).encode("utf-8")
        self.send_response(status)
        self.send_header("Content-Type", "application/json")
        self.send_header("Cache-Control", "no-store")
        self.send_header("Content-Length", str(len(body)))
        self.end_headers()
        self.wfile.write(body)
