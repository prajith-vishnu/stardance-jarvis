# GET /api/feeds?feed=<name>
import json
from http.server import BaseHTTPRequestHandler
from urllib.parse import urlparse, parse_qs

try:
    from api._core import FEEDS, get_env
except ImportError:
    from _core import FEEDS, get_env


class handler(BaseHTTPRequestHandler):
    def do_GET(self):
        query = parse_qs(urlparse(self.path).query)
        name = (query.get("feed") or [""])[0]

        if name not in FEEDS:
            return self._send(400, {"error": f"Unknown feed '{name}'. Valid: {sorted(FEEDS)}"})

        nasa_key = get_env("NASA_API_KEY")
        if not nasa_key:
            return self._send(500, {"error": "NASA_API_KEY is not configured. Add it in Vercel → Project → Settings → Environment Variables, then redeploy."})

        fetch, max_age = FEEDS[name]
        try:
            data = fetch(nasa_key)
        except Exception as e:
            return self._send(502, {"error": f"Upstream feed '{name}' failed: {type(e).__name__}"})

        cache = f"s-maxage={max_age}, stale-while-revalidate={max_age * 2}" if max_age else "no-store"
        self._send(200, {"feed": name, "data": data}, cache)

    def _send(self, status, payload, cache="no-store"):
        body = json.dumps(payload).encode("utf-8")
        self.send_response(status)
        self.send_header("Content-Type", "application/json")
        self.send_header("Cache-Control", cache)
        self.send_header("Content-Length", str(len(body)))
        self.end_headers()
        self.wfile.write(body)
