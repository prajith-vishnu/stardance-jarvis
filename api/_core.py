# shared logic for the api functions, stdlib only so vercel has nothing to install
import json
import os
import urllib.request
from datetime import datetime, timedelta, timezone

NASA_BASE = "https://api.nasa.gov"
GEMINI_URL = "https://generativelanguage.googleapis.com/v1beta/models/gemini-2.5-flash:generateContent"


def _get_json(url, timeout=20):
    req = urllib.request.Request(url, headers={"User-Agent": "JARVIS-NASA-CORE/2.0"})
    with urllib.request.urlopen(req, timeout=timeout) as r:
        return json.loads(r.read().decode("utf-8"))


def _post_json(url, body, headers, timeout=25):
    data = json.dumps(body).encode("utf-8")
    req = urllib.request.Request(
        url, data=data, method="POST",
        headers={"Content-Type": "application/json", **headers},
    )
    with urllib.request.urlopen(req, timeout=timeout) as r:
        return json.loads(r.read().decode("utf-8"))


def _today():
    return datetime.now(timezone.utc).strftime("%Y-%m-%d")


def _days_ago(n):
    return (datetime.now(timezone.utc) - timedelta(days=n)).strftime("%Y-%m-%d")


def feed_apod(key):
    d = _get_json(f"{NASA_BASE}/planetary/apod?api_key={key}")
    return {
        "media_type": d.get("media_type"),
        "url": d.get("url"),
        "title": d.get("title", ""),
        "date": d.get("date", ""),
        "explanation": (d.get("explanation") or "")[:400],
    }


def feed_astros(_key):
    d = _get_json("http://api.open-notify.org/astros.json", timeout=5)
    return {"number": d.get("number", 0), "people": [p["name"] for p in d.get("people", [])]}


def feed_neo(key):
    today = _today()
    d = _get_json(f"{NASA_BASE}/neo/rest/v1/feed?start_date={today}&end_date={today}&api_key={key}")
    objects = d.get("near_earth_objects", {}).get(today, [])
    digest = []
    for o in objects:
        try:
            approach = o["close_approach_data"][0]
            digest.append({
                "name": o.get("name", "Unknown").strip("()").strip(),
                "dist_km": int(float(approach["miss_distance"]["kilometers"])),
                "speed_kph": int(float(approach["relative_velocity"]["kilometers_per_hour"])),
                "hazardous": bool(o.get("is_potentially_hazardous_asteroid")),
            })
        except (KeyError, IndexError, ValueError):
            continue
    digest.sort(key=lambda x: x["dist_km"])
    return {
        "count": d.get("element_count", len(objects)),
        "hazardous": sum(1 for o in digest if o["hazardous"]),
        "closest_name": digest[0]["name"] if digest else "N/A",
        "closest_km": digest[0]["dist_km"] if digest else 0,
        "objects": digest[:5],
    }


def feed_neo_trend(key):
    d = _get_json(f"{NASA_BASE}/neo/rest/v1/feed?start_date={_days_ago(6)}&end_date={_today()}&api_key={key}")
    counts = [len(v) for v in d.get("near_earth_objects", {}).values()]
    return {"avg": round(sum(counts) / len(counts), 1) if counts else None}


def feed_solar(key):
    # DONKI sometimes returns plain text errors instead of json, fall back to quiet sun
    base = {"count": 0, "class": "—", "strongest": "—", "threat": "NOMINAL", "peak": "", "active": False}
    try:
        flares = _get_json(f"{NASA_BASE}/DONKI/FLR?startDate={_days_ago(7)}&endDate={_today()}&api_key={key}")
    except Exception:
        return base
    if not isinstance(flares, list) or not flares:
        return base
    latest = flares[-1]
    rank = lambda c: {"X": 4, "M": 3, "C": 2, "B": 1}.get((c or " ")[0], 0)
    strongest = max((f.get("classType") or "" for f in flares), key=rank, default="")
    threat = "HIGH" if strongest.startswith("X") else "ELEVATED" if strongest.startswith("M") else "NOMINAL"
    return {"count": len(flares), "class": latest.get("classType", "?"),
            "strongest": strongest or "?", "threat": threat,
            "peak": latest.get("peakTime", ""), "active": True}


def feed_mars(key):
    d = _get_json(f"{NASA_BASE}/mars-photos/api/v1/rovers/curiosity/latest_photos?api_key={key}")
    photos = d.get("latest_photos", [])
    if not photos:
        return None
    p = photos[0]
    return {"rover": p["rover"]["name"], "status": p["rover"]["status"],
            "camera": p["camera"]["full_name"], "img": p["img_src"],
            "date": p["earth_date"], "sol": p["sol"]}


def feed_iss(_key):
    d = _get_json("http://api.open-notify.org/iss-now.json", timeout=5)
    pos = d["iss_position"]
    return {"lat": float(pos["latitude"]), "lon": float(pos["longitude"])}


def feed_earth_events(_key):
    d = _get_json("https://eonet.gsfc.nasa.gov/api/v3/events?limit=6&status=open")
    return [{"title": e["title"], "cat": e["categories"][0]["title"]} for e in d.get("events", [])]


def feed_epic(key):
    items = _get_json(f"{NASA_BASE}/EPIC/api/natural?api_key={key}")
    if not items:
        return None
    item = items[0]
    date_path = item["date"][:10].replace("-", "/")
    return {"url": f"https://epic.gsfc.nasa.gov/archive/natural/{date_path}/png/{item['image']}.png",
            "date": item["date"][:10], "caption": item.get("caption", "")}


FEEDS = {
    "apod": (feed_apod, 3600),
    "astros": (feed_astros, 600),
    "neo": (feed_neo, 600),
    "neo_trend": (feed_neo_trend, 3600),
    "solar": (feed_solar, 600),
    "mars": (feed_mars, 3600),
    "iss": (feed_iss, 0),
    "earth_events": (feed_earth_events, 600),
    "epic": (feed_epic, 3600),
}


def jarvis_reply(prompt, context, gemini_key):
    sys_instr = (
        "You are J.A.R.V.I.S., a Joint Artificial Reconnaissance & Vigilance Intelligence System "
        "created entirely by Prajith. "
        "You speak with crisp British authority, deep technical precision, and measured confidence. "
        "You have live access to: NASA APOD, Mars Curiosity rover (latest sol), Near-Earth Object radar, "
        "ISS real-time position, NASA DONKI solar flare data, EONET Earth event feeds, "
        "and the Open Notify astronaut tracker. "
        f"Current live data: {context} "
        "You ONLY discuss astronomy, NASA missions, space exploration, astrophysics, planetary defense, "
        "Earth observation, and cosmic telemetry. "
        "Politely decline anything unrelated to space and redirect to mission operations. "
        "Address the user as Commander or Flight Director unless they provide their name. "
        "Keep responses under 3 sentences unless delivering a multi-source correlation. "
        "Respond in plain text only — no markdown formatting."
    )
    body = {
        "system_instruction": {"parts": [{"text": sys_instr}]},
        "contents": [{"role": "user", "parts": [{"text": prompt}]}],
        # thinking tokens count against the output cap and can truncate replies, so turn thinking off
        "generationConfig": {"temperature": 0.7, "maxOutputTokens": 1024, "thinkingConfig": {"thinkingBudget": 0}},
    }
    out = _post_json(GEMINI_URL, body, {"x-goog-api-key": gemini_key})
    return out["candidates"][0]["content"]["parts"][0]["text"]


def get_env(name):
    return (os.environ.get(name) or "").strip()
