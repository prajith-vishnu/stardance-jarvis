import streamlit as st
import requests
import pandas as pd
from datetime import datetime, timedelta
from google import genai
from google.genai import types

st.set_page_config(
    page_title="J.A.R.V.I.S. // NASA CORE",
    page_icon="🤖",
    layout="wide",
    initial_sidebar_state="collapsed",
)

# ══════════════════════════════════════════════════════════════════════
#  DESIGN SYSTEM — Iron Man HUD meets NASA Mission Control
# ══════════════════════════════════════════════════════════════════════
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700&family=JetBrains+Mono:wght@400;500;600&display=swap');

/* ── Base ── */
html, body, [data-testid="stAppViewContainer"], .stApp {
    background-color: #05080F !important;
    color: #B0BCC8 !important;
    font-family: 'Inter', sans-serif !important;
    height: 100vh !important;
    overflow: hidden !important;
}

/* ── Hex grid background ── */
.stApp::before {
    content: '';
    position: fixed;
    inset: 0;
    background-image: url("data:image/svg+xml,%3Csvg xmlns='http://www.w3.org/2000/svg' width='56' height='97'%3E%3Cpath d='M28,97 L0,73 L0,24 L28,0 L56,24 L56,73 Z' fill='none' stroke='%2300D4FF' stroke-width='0.3'/%3E%3C/svg%3E");
    background-size: 56px 97px;
    opacity: 0.035;
    pointer-events: none;
    z-index: 0;
}

/* ── Scan line ── */
@keyframes scan {
    0%   { top: -2px; opacity: 0; }
    4%   { opacity: 1; }
    96%  { opacity: 1; }
    100% { top: 100vh; opacity: 0; }
}
.scan-line {
    position: fixed;
    left: 0; right: 0; height: 1px;
    background: linear-gradient(90deg, transparent 0%, rgba(0,212,255,0.4) 30%, rgba(0,212,255,0.8) 50%, rgba(0,212,255,0.4) 70%, transparent 100%);
    animation: scan 14s linear infinite;
    pointer-events: none;
    z-index: 9999;
}

/* ── Layout ── */
[data-testid="stHeader"] { display: none !important; }
[data-testid="stSidebar"] { display: none !important; }
.block-container {
    padding-top: 0.6rem !important;
    padding-bottom: 0 !important;
    padding-left: 1.8rem !important;
    padding-right: 1.8rem !important;
    max-width: 100% !important;
}

/* ── Typography ── */
h1,h2,h3,h4,h5 {
    font-family: 'Inter', sans-serif !important;
    color: #FFFFFF !important;
    font-weight: 600 !important;
    letter-spacing: -0.3px !important;
    margin: 0 0 4px 0 !important;
}

/* ── Metric cards ── */
[data-testid="stMetric"] {
    background: rgba(0,212,255,0.025) !important;
    border: 1px solid rgba(0,212,255,0.10) !important;
    border-radius: 8px !important;
    padding: 10px 14px !important;
}
[data-testid="stMetricLabel"] p {
    font-family: 'JetBrains Mono', monospace !important;
    font-size: 9px !important;
    letter-spacing: 1.5px !important;
    text-transform: uppercase !important;
    color: rgba(0,212,255,0.55) !important;
}
[data-testid="stMetricValue"] {
    font-family: 'JetBrains Mono', monospace !important;
    font-size: 20px !important;
    color: #FFFFFF !important;
    font-weight: 600 !important;
}
[data-testid="stMetricDelta"] svg { display: none !important; }
[data-testid="stMetricDelta"] > div {
    font-family: 'JetBrains Mono', monospace !important;
    font-size: 9px !important;
    color: rgba(0,212,255,0.5) !important;
}

/* ── Containers ── */
div[data-testid="stVerticalBlockBorderCard"] {
    background: rgba(6,10,22,0.95) !important;
    border: 1px solid rgba(0,212,255,0.09) !important;
    border-radius: 10px !important;
    padding: 12px !important;
    box-shadow: 0 0 40px rgba(0,212,255,0.03), 0 8px 32px rgba(0,0,0,0.5) !important;
}

/* ── Orb ── */
.orb-wrap {
    display: flex; flex-direction: column;
    align-items: center; justify-content: center;
    margin: 0 auto 6px; text-align: center;
}
.jarvis-orb {
    width: 48px; height: 48px;
    background: radial-gradient(circle at 33% 33%, #7AF0FF 0%, #00AAFF 38%, #003880 72%, #05080F 100%);
    border-radius: 50%;
    box-shadow: 0 0 0 1px rgba(0,212,255,0.25), 0 0 18px rgba(0,212,255,0.45), 0 0 50px rgba(0,120,255,0.15);
    animation: orb-beat 3.2s ease-in-out infinite;
}
.jarvis-orb::after {
    content: '';
    position: absolute;
    inset: -7px;
    border-radius: 50%;
    border: 1px solid rgba(0,212,255,0.18);
    animation: orb-ring 3.2s ease-in-out infinite;
}
.jarvis-orb { position: relative; }
@keyframes orb-beat {
    0%,100% { transform: scale(0.96); box-shadow: 0 0 0 1px rgba(0,212,255,0.22), 0 0 16px rgba(0,212,255,0.38), 0 0 45px rgba(0,120,255,0.12); }
    50%      { transform: scale(1.04); box-shadow: 0 0 0 1px rgba(0,212,255,0.45), 0 0 28px rgba(0,212,255,0.65), 0 0 70px rgba(0,120,255,0.28); }
}
@keyframes orb-ring {
    0%,100% { transform: scale(0.94); opacity: 0.35; }
    50%      { transform: scale(1.12); opacity: 0.75; }
}
.orb-label {
    font-family: 'JetBrains Mono', monospace;
    font-size: 8px; color: rgba(0,212,255,0.65);
    letter-spacing: 2.5px; text-transform: uppercase; margin-top: 5px;
}

/* ── Chat bubbles ── */
.chat-bubble { padding: 9px 13px; border-radius: 10px; margin-bottom: 7px; font-size: 13px; line-height: 1.55; max-width: 90%; }
.cmd-bubble  { background: rgba(255,255,255,0.025); border: 1px solid rgba(255,255,255,0.06); color: #C0CCD8; margin-left: auto; border-bottom-right-radius: 3px; }
.ai-bubble   { background: linear-gradient(135deg, rgba(0,90,200,0.07) 0%, rgba(0,212,255,0.035) 100%); border: 1px solid rgba(0,212,255,0.14); color: #E0E8F0; margin-right: auto; border-bottom-left-radius: 3px; }

/* ── Chat input ── */
div[data-testid="stChatInput"] {
    background: rgba(6,10,22,0.95) !important;
    border: 1px solid rgba(0,212,255,0.12) !important;
    border-radius: 8px !important;
}
div[data-testid="stChatInput"] textarea { color: #FFFFFF !important; font-size: 13px !important; }

/* ── Mission buttons ── */
.stButton button {
    background: rgba(0,212,255,0.03) !important;
    color: #88A0B4 !important;
    font-family: 'JetBrains Mono', monospace !important;
    font-weight: 500 !important;
    font-size: 10px !important;
    letter-spacing: 0.8px !important;
    border: 1px solid rgba(0,212,255,0.09) !important;
    border-radius: 6px !important;
    padding: 9px 8px !important;
    width: 100% !important;
    text-align: center !important;
    transition: all 0.12s ease !important;
    line-height: 1.4 !important;
}
.stButton button:hover {
    background: rgba(0,212,255,0.09) !important;
    border-color: rgba(0,212,255,0.38) !important;
    color: #00D4FF !important;
    box-shadow: 0 0 10px rgba(0,212,255,0.12) !important;
}
.stButton button:active {
    background: rgba(0,212,255,0.15) !important;
    color: #FFFFFF !important;
}

/* ── Boot button ── */
.boot-wrap div button {
    background: rgba(0,212,255,0.06) !important;
    border: 1px solid rgba(0,212,255,0.45) !important;
    color: #00D4FF !important;
    font-family: 'JetBrains Mono', monospace !important;
    font-weight: 600 !important;
    font-size: 12px !important;
    letter-spacing: 3px !important;
    padding: 16px 28px !important;
    border-radius: 8px !important;
    box-shadow: 0 0 20px rgba(0,212,255,0.18), inset 0 0 12px rgba(0,212,255,0.04) !important;
    width: 100% !important;
}
.boot-wrap div button:hover {
    background: rgba(0,212,255,0.14) !important;
    box-shadow: 0 0 36px rgba(0,212,255,0.32) !important;
    color: #FFFFFF !important;
}

/* ── Image ── */
[data-testid="stImage"] img {
    border-radius: 8px !important;
    border: 1px solid rgba(0,212,255,0.09) !important;
    width: 100% !important;
}

/* ── Alerts ── */
.stAlert { background: rgba(0,212,255,0.03) !important; border: 1px solid rgba(0,212,255,0.12) !important; border-radius: 8px !important; font-size: 12px !important; }

/* ── Hazard badge ── */
.badge-hazard  { display:inline-block; background:rgba(255,80,80,0.12); border:1px solid rgba(255,80,80,0.4); color:#FF6060; font-family:'JetBrains Mono',monospace; font-size:9px; padding:2px 7px; border-radius:4px; letter-spacing:1px; }
.badge-nominal { display:inline-block; background:rgba(0,212,255,0.08); border:1px solid rgba(0,212,255,0.3); color:#00D4FF; font-family:'JetBrains Mono',monospace; font-size:9px; padding:2px 7px; border-radius:4px; letter-spacing:1px; }

/* ── Scrollbar ── */
::-webkit-scrollbar { width: 3px; }
::-webkit-scrollbar-track { background: transparent; }
::-webkit-scrollbar-thumb { background: rgba(0,212,255,0.18); border-radius: 3px; }

/* ── Caption ── */
.stCaption { font-size: 11px !important; color: rgba(0,212,255,0.5) !important; font-family: 'JetBrains Mono', monospace !important; }
</style>
<div class="scan-line"></div>
""", unsafe_allow_html=True)

# ══════════════════════════════════════════════════════════════════════
#  SESSION STATE
# ══════════════════════════════════════════════════════════════════════
_defaults = {
    "chat_history": [],
    "last_audio": None,
    "tts_text": None,
    "booted": False,
    "iss_pos": None,
    "display": {"type": "apod", "img_url": None, "title": None, "caption": None},
    "auto_data": None,
}
for k, v in _defaults.items():
    if k not in st.session_state:
        st.session_state[k] = v

# ══════════════════════════════════════════════════════════════════════
#  CREDENTIALS
# ══════════════════════════════════════════════════════════════════════
if "GEMINI_API_KEY" not in st.secrets or "NASA_API_KEY" not in st.secrets:
    st.error("🔒 SECRETS MISSING — add NASA_API_KEY and GEMINI_API_KEY to .streamlit/secrets.toml")
    st.stop()

NASA_KEY  = st.secrets["NASA_API_KEY"]
GEMINI_KEY = st.secrets["GEMINI_API_KEY"]

# ══════════════════════════════════════════════════════════════════════
#  NASA API FUNCTIONS — 8 Live Data Sources
# ══════════════════════════════════════════════════════════════════════

def get_apod():
    try:
        r = requests.get(f"https://api.nasa.gov/planetary/apod?api_key={NASA_KEY}", timeout=8)
        return r.json() if r.status_code == 200 else None
    except: return None

def get_people_in_space():
    try:
        r = requests.get("http://api.open-notify.org/astros.json", timeout=5)
        if r.status_code == 200:
            d = r.json(); return d["number"], [p["name"] for p in d["people"]]
    except: pass
    return 0, []

def get_asteroid_radar():
    today = datetime.today().strftime('%Y-%m-%d')
    try:
        r = requests.get(f"https://api.nasa.gov/neo/rest/v1/feed?start_date={today}&end_date={today}&api_key={NASA_KEY}", timeout=8).json()
        objects = r.get("near_earth_objects", {}).get(today, [])
        hazardous = [o for o in objects if o.get("is_potentially_hazardous_asteroid")]
        closest = sorted(objects, key=lambda x: float(x["close_approach_data"][0]["miss_distance"]["kilometers"])) if objects else []
        return {
            "count": r.get("element_count", 0),
            "hazardous": len(hazardous),
            "closest_name": closest[0]["name"] if closest else "N/A",
            "closest_km": int(float(closest[0]["close_approach_data"][0]["miss_distance"]["kilometers"])) if closest else 0,
            "objects": objects,
        }
    except: return {"count": 0, "hazardous": 0, "closest_name": "N/A", "closest_km": 0, "objects": []}

def get_solar_activity():
    today = datetime.today().strftime('%Y-%m-%d')
    week_ago = (datetime.today() - timedelta(days=7)).strftime('%Y-%m-%d')
    try:
        r = requests.get(f"https://api.nasa.gov/DONKI/FLR?startDate={week_ago}&endDate={today}&api_key={NASA_KEY}", timeout=8)
        if r.status_code == 200:
            flares = r.json()
            if flares:
                latest = flares[-1]
                return {"count": len(flares), "class": latest.get("classType", "?"), "peak": latest.get("peakTime", ""), "active": True}
        return {"count": 0, "class": "—", "peak": "", "active": False}
    except: return {"count": 0, "class": "—", "peak": "", "active": False}

def get_mars_latest():
    try:
        r = requests.get(f"https://api.nasa.gov/mars-photos/api/v1/rovers/curiosity/latest_photos?api_key={NASA_KEY}", timeout=8)
        photos = r.json().get("latest_photos", [])
        if not photos: return None
        p = photos[0]
        return {"rover": p["rover"]["name"], "status": p["rover"]["status"],
                "camera": p["camera"]["full_name"], "img": p["img_src"],
                "date": p["earth_date"], "sol": p["sol"]}
    except: return None

def get_iss_position():
    try:
        r = requests.get("http://api.open-notify.org/iss-now.json", timeout=5)
        if r.status_code == 200:
            pos = r.json()["iss_position"]
            return float(pos["latitude"]), float(pos["longitude"])
    except: pass
    return None, None

def get_earth_events():
    try:
        r = requests.get("https://eonet.gsfc.nasa.gov/api/v3/events?limit=6&status=open", timeout=8)
        if r.status_code == 200:
            return [{"title": e["title"], "cat": e["categories"][0]["title"]}
                    for e in r.json().get("events", [])]
        return []
    except: return []

def get_epic_earth():
    """NASA EPIC — full-disk Earth imagery from DSCOVR satellite."""
    try:
        r = requests.get(f"https://api.nasa.gov/EPIC/api/natural?api_key={NASA_KEY}", timeout=8)
        if r.status_code == 200:
            items = r.json()
            if items:
                item = items[0]
                date_str = item["date"][:10].replace("-", "/")
                img_name = item["image"]
                url = f"https://epic.gsfc.nasa.gov/archive/natural/{date_str}/png/{img_name}.png"
                return {"url": url, "date": item["date"][:10], "caption": item.get("caption", "")}
    except: pass
    return None

# ══════════════════════════════════════════════════════════════════════
#  AUTO-LOAD ON FIRST RENDER (shows live data immediately)
# ══════════════════════════════════════════════════════════════════════
if st.session_state.auto_data is None:
    with st.spinner("Initializing JARVIS neural core..."):
        people_count, people_names = get_people_in_space()
        asteroids   = get_asteroid_radar()
        solar       = get_solar_activity()
        apod        = get_apod()
        st.session_state.auto_data = {
            "people_count": people_count,
            "people_names": people_names,
            "asteroids":    asteroids,
            "solar":        solar,
            "apod":         apod,
        }
        # Load APOD into display panel automatically
        if apod and apod.get("media_type") == "image":
            st.session_state.display = {
                "type": "apod",
                "img_url": apod.get("url"),
                "title": apod.get("title", ""),
                "caption": apod.get("date", ""),
            }
        # JARVIS auto-greeting with live stats
        threat = "ELEVATED" if asteroids["hazardous"] > 0 else "NOMINAL"
        solar_line = f"{solar['count']} flare events, latest class {solar['class']}" if solar["active"] else "space weather nominal"
        st.session_state.chat_history = [(
            "JARVIS",
            f"🛰️ <b>ALL SYSTEMS ONLINE — NASA CORE ACTIVE</b><br><br>"
            f"Good day. I am J.A.R.V.I.S., your Joint Artificial Reconnaissance & Vigilance Intelligence System, "
            f"designed and built by Prajith.<br><br>"
            f"<b>LIVE MISSION STATUS:</b><br>"
            f"• <b>{people_count} humans</b> currently in space<br>"
            f"• <b>{asteroids['count']} near-Earth objects</b> tracked today — threat level: <b>{threat}</b><br>"
            f"• Solar activity: {solar_line}<br><br>"
            f"Today's deep space image is loaded. Use the <b>Mission Directives</b> below to query any active feed, "
            f"or speak directly to me."
        )]

ad = st.session_state.auto_data  # shorthand

# ══════════════════════════════════════════════════════════════════════
#  GEMINI CLIENT
# ══════════════════════════════════════════════════════════════════════
client = genai.Client(api_key=GEMINI_KEY)

# ══════════════════════════════════════════════════════════════════════
#  TOP STATUS BAR
# ══════════════════════════════════════════════════════════════════════
threat_color  = "#FF5555" if ad["asteroids"]["hazardous"] > 0 else "#00D4FF"
threat_label  = "THREAT: ELEVATED" if ad["asteroids"]["hazardous"] > 0 else "THREAT: NOMINAL"
solar_active  = ad["solar"]["active"]
solar_color   = "#FFB020" if solar_active else "#00D4FF"
solar_label   = f"SOLAR: CLASS {ad['solar']['class']}" if solar_active else "SOLAR: NOMINAL"

st.markdown(f"""
<div style="display:flex; align-items:center; justify-content:space-between;
            padding:6px 0 10px; border-bottom:1px solid rgba(0,212,255,0.07); margin-bottom:10px;">
  <div style="display:flex; align-items:center; gap:10px;">
    <span style="font-family:'JetBrains Mono',monospace; font-size:16px; font-weight:700;
                 color:#00D4FF; letter-spacing:4px;">J.A.R.V.I.S.</span>
    <span style="font-family:'JetBrains Mono',monospace; font-size:9px; color:rgba(0,212,255,0.4);
                 letter-spacing:1px; margin-top:1px;">JOINT ARTIFICIAL RECONNAISSANCE & VIGILANCE INTELLIGENCE SYSTEM</span>
  </div>
  <div style="display:flex; gap:20px; align-items:center;">
    <span style="font-family:'JetBrains Mono',monospace; font-size:10px; color:#A0B4C8;">
      👤 <b style="color:#FFFFFF;">{ad['people_count']}</b> IN SPACE
    </span>
    <span style="font-family:'JetBrains Mono',monospace; font-size:10px; color:#A0B4C8;">
      ☄️ <b style="color:#FFFFFF;">{ad['asteroids']['count']}</b> NEAR-EARTH
    </span>
    <span style="font-family:'JetBrains Mono',monospace; font-size:10px;
                 color:{threat_color}; font-weight:600;">{threat_label}</span>
    <span style="font-family:'JetBrains Mono',monospace; font-size:10px;
                 color:{solar_color}; font-weight:600;">{solar_label}</span>
    <span style="font-family:'JetBrains Mono',monospace; font-size:9px; color:rgba(0,212,255,0.35);">
      {datetime.utcnow().strftime('%H:%M:%S')} UTC
    </span>
  </div>
</div>
""", unsafe_allow_html=True)

# ══════════════════════════════════════════════════════════════════════
#  MAIN LAYOUT  ──  LEFT: Data Display  │  RIGHT: JARVIS Chat
# ══════════════════════════════════════════════════════════════════════
left, right = st.columns([1.1, 1.0], gap="large")

forced_prompt = ""

# ──────────────────────────────────────────────────────────────────────
#  LEFT PANEL — Live NASA data display + Mission command grid
# ──────────────────────────────────────────────────────────────────────
with left:

    # ── LIVE DATA DISPLAY PANEL ──
    with st.container(height=380, border=True):
        disp = st.session_state.display

        if disp["type"] in ("apod", "mars", "epic") and disp.get("img_url"):
            st.image(disp["img_url"], use_container_width=True)
            if disp.get("title"):
                st.markdown(
                    f"<p style='font-family:JetBrains Mono,monospace; font-size:10px; color:rgba(0,212,255,0.6); margin:4px 0 0; letter-spacing:0.5px;'>"
                    f"{disp['title']}"
                    f"{'  ·  ' + disp['caption'] if disp.get('caption') else ''}</p>",
                    unsafe_allow_html=True
                )
        elif disp["type"] == "iss" and st.session_state.iss_pos:
            lat, lon = st.session_state.iss_pos
            try:
                import pydeck as pdk
                deck = pdk.Deck(
                    layers=[pdk.Layer(
                        "ScatterplotLayer",
                        data=[{"lat": lat, "lon": lon}],
                        get_position=["lon", "lat"],
                        get_fill_color=[0, 212, 255, 210],
                        get_radius=700000,
                        radius_min_pixels=9,
                        radius_max_pixels=20,
                    )],
                    initial_view_state=pdk.ViewState(latitude=lat, longitude=lon, zoom=0.7, pitch=18),
                    map_style="https://basemaps.cartocdn.com/gl/dark-matter-gl-style/style.json",
                    tooltip={"text": f"ISS  {lat:.2f}°, {lon:.2f}°"},
                )
                st.pydeck_chart(deck, use_container_width=True)
            except Exception:
                st.map(pd.DataFrame({"lat": [lat], "lon": [lon]}), zoom=0)
            st.markdown(
                f"<p style='font-family:JetBrains Mono,monospace; font-size:10px; color:rgba(0,212,255,0.6); margin-top:4px;'>"
                f"ISS ORBITAL POSITION  ·  {lat:.2f}°N  {lon:.2f}°E  ·  ALT ~408 km  ·  27,600 km/h</p>",
                unsafe_allow_html=True
            )
        elif disp["type"] == "earth_events" and disp.get("events"):
            st.markdown("<p style='font-family:JetBrains Mono,monospace; font-size:10px; color:rgba(0,212,255,0.6); letter-spacing:1px; margin-bottom:8px;'>EONET — ACTIVE SATELLITE-DETECTED EVENTS</p>", unsafe_allow_html=True)
            for ev in disp["events"]:
                cat_color = "#FF6B35" if ev["cat"] in ("Wildfires", "Volcanoes", "Severe Storms") else "#00D4FF"
                st.markdown(
                    f"<div style='padding:7px 10px; margin-bottom:5px; border-radius:6px; "
                    f"background:rgba(0,212,255,0.025); border:1px solid rgba(0,212,255,0.08);'>"
                    f"<span style='font-family:JetBrains Mono,monospace; font-size:9px; color:{cat_color}; letter-spacing:1px;'>{ev['cat'].upper()}</span>"
                    f"<span style='font-size:12px; color:#D0DDE8; margin-left:8px;'>{ev['title']}</span></div>",
                    unsafe_allow_html=True
                )
        else:
            # Fallback: show asteroid data as cards
            st.markdown("<p style='font-family:JetBrains Mono,monospace; font-size:10px; color:rgba(0,212,255,0.5); letter-spacing:1px; margin-bottom:10px;'>PLANETARY DEFENSE RADAR — LIVE FEED</p>", unsafe_allow_html=True)
            a = ad["asteroids"]
            c1, c2 = st.columns(2)
            with c1:
                st.metric("NEAR-EARTH OBJECTS", str(a["count"]), "Tracked Today")
                st.metric("CLOSEST APPROACH", f"{a['closest_km']:,} km", a["closest_name"][:20])
            with c2:
                badge = "⚠ HAZARDOUS" if a["hazardous"] > 0 else "✓ NOMINAL"
                st.metric("THREAT OBJECTS", str(a["hazardous"]), badge)
                s = ad["solar"]
                st.metric("SOLAR FLARES / 7D", str(s["count"]), f"Latest: Class {s['class']}")

    # ── MISSION COMMAND GRID ──
    st.markdown(
        "<p style='font-family:JetBrains Mono,monospace; font-size:9px; color:rgba(0,212,255,0.4); "
        "letter-spacing:2px; margin: 8px 0 6px;'>MISSION DIRECTIVES</p>",
        unsafe_allow_html=True
    )
    r1c1, r1c2, r1c3 = st.columns(3)
    r2c1, r2c2, r2c3 = st.columns(3)

    with r1c1:
        if st.button("📡 OPTICAL\nBRIEFING"):
            with st.spinner(""):
                apod = get_apod()
                if apod:
                    if apod.get("media_type") == "image":
                        st.session_state.display = {"type": "apod", "img_url": apod["url"],
                                                    "title": apod.get("title"), "caption": apod.get("date")}
                    forced_prompt = (f"Special Directive: Optical Briefing. "
                                     f"Title: {apod.get('title')}. "
                                     f"Detail: {apod.get('explanation','')[:400]}")
    with r1c2:
        if st.button("🔴 MARS\nSURFACE"):
            with st.spinner(""):
                mars = get_mars_latest()
                if mars:
                    st.session_state.display = {"type": "mars", "img_url": mars["img"],
                                                "title": f"{mars['rover']} Rover — Sol {mars['sol']}",
                                                "caption": mars["date"]}
                    forced_prompt = (f"Special Directive: Mars Surface. Live imaging from {mars['rover']} rover. "
                                     f"Sol {mars['sol']}, earth date {mars['date']}. Camera: {mars['camera']}. "
                                     f"Status: {mars['status']}. Image: {mars['img']}. "
                                     f"Give a crisp 2-sentence tactical surface report with the sol number.")
    with r1c3:
        if st.button("☄️ THREAT\nANALYSIS"):
            with st.spinner(""):
                ast = get_asteroid_radar()
                sol = get_solar_activity()
                threat = "ELEVATED" if ast["hazardous"] > 0 else "NOMINAL"
                solar_line = f"{sol['count']} solar flares (7d), latest class {sol['class']}" if sol["active"] else "no significant solar activity"
                st.session_state.display = {"type": "asteroids", "img_url": None, "title": None, "caption": None}
                forced_prompt = (f"Special Directive: Multi-source planetary defense correlation. "
                                 f"ASTEROID RADAR: {ast['count']} NEOs tracked today. Hazardous: {ast['hazardous']}. "
                                 f"Closest approach: {ast['closest_name']} at {ast['closest_km']:,} km. Threat: {threat}. "
                                 f"SOLAR WEATHER: {solar_line}. "
                                 f"Deliver a 3-sentence integrated threat assessment correlating both datasets.")
    with r2c1:
        if st.button("🛸 ISS LIVE\nTRACKER"):
            with st.spinner(""):
                lat, lon = get_iss_position()
                if lat is not None:
                    st.session_state.iss_pos = (lat, lon)
                    st.session_state.display = {"type": "iss", "img_url": None, "title": None, "caption": None}
                    forced_prompt = (f"Special Directive: ISS position report. "
                                     f"Station at {lat:.2f}° latitude, {lon:.2f}° longitude. "
                                     f"Orbital altitude ~408 km, speed ~27,600 km/h. "
                                     f"Give a 2-sentence tactical position report.")
    with r2c2:
        if st.button("☀️ SOLAR\nSTORM"):
            with st.spinner(""):
                sol = get_solar_activity()
                if sol:
                    forced_prompt = (f"Special Directive: DONKI Solar Activity. "
                                     f"{sol['count']} solar flare events in past 7 days. "
                                     f"Latest flare class: {sol['class']}. Peak: {sol['peak']}. "
                                     f"Give a 2-sentence space weather briefing and mission advisory.")
    with r2c3:
        if st.button("🌍 EARTH\nCRISIS"):
            with st.spinner(""):
                events = get_earth_events()
                if events:
                    st.session_state.display = {"type": "earth_events", "img_url": None,
                                                "title": None, "caption": None, "events": events}
                    summary = "; ".join([f"{e['title']} ({e['cat']})" for e in events])
                    forced_prompt = (f"Special Directive: EONET Earth Monitoring. "
                                     f"NASA satellites have detected: {summary}. "
                                     f"Give a 3-sentence Earth systems status briefing.")
                else:
                    forced_prompt = "Special Directive: EONET shows no active natural events. Give a 1-sentence all-clear."

    # Inject events into display state when earth events button fires
    if forced_prompt and "EONET" in forced_prompt and "earth_events" not in str(st.session_state.display.get("type","")):
        pass  # already handled above

# ──────────────────────────────────────────────────────────────────────
#  RIGHT PANEL — JARVIS Chat Interface
# ──────────────────────────────────────────────────────────────────────
with right:

    st.markdown("""
    <div class="orb-wrap">
        <div class="jarvis-orb"></div>
        <div class="orb-label">JARVIS CORE · ONLINE</div>
    </div>
    """, unsafe_allow_html=True)

    # Chat history
    with st.container(height=390, border=True):
        for speaker, msg in st.session_state.chat_history:
            css_cls = "cmd-bubble" if speaker == "COMMANDER" else "ai-bubble"
            st.markdown(
                f'<div class="chat-bubble {css_cls}"><b style="font-size:10px; '
                f'font-family:JetBrains Mono,monospace; letter-spacing:1px; '
                f'color:rgba(0,212,255,0.6);">{speaker}</b><br>{msg}</div>',
                unsafe_allow_html=True
            )

    st.write("")

    # Boot gate
    if not st.session_state.booted:
        st.markdown("<div class='boot-wrap'>", unsafe_allow_html=True)
        if st.button("⚡  INITIALIZE VOCAL MATRIX"):
            st.session_state.booted = True
            st.session_state.tts_text = (
                "All systems nominal. JARVIS neural core online. "
                "Good day. I am your Joint Artificial Reconnaissance and Vigilance Intelligence System, "
                "built by Prajith. Running in full NASA mode."
            )
            st.rerun()
        st.markdown("</div>", unsafe_allow_html=True)
        st.caption("🔒  Click above to enable voice output and terminal input")
        user_input  = None
        voice_input = None
    else:
        input_col, mic_col = st.columns([3.5, 1.5], vertical_alignment="bottom")
        with input_col:
            user_input = st.chat_input("Query NASA feeds or ask JARVIS anything...")
        with mic_col:
            voice_input = st.audio_input("", label_visibility="collapsed", key="mic")

# ══════════════════════════════════════════════════════════════════════
#  INFERENCE ENGINE
# ══════════════════════════════════════════════════════════════════════
    active_prompt = ""

    if forced_prompt:
        active_prompt = forced_prompt
    elif (st.session_state.booted and voice_input
          and voice_input.name != st.session_state.last_audio):
        try:
            st.session_state.last_audio = voice_input.name
            audio_bytes = voice_input.read()
            tx = client.models.generate_content(
                model="gemini-2.5-flash",
                contents=[
                    types.Part.from_bytes(data=audio_bytes, mime_type="audio/wav"),
                    "Transcribe this speech cleanly into plain text.",
                ]
            )
            active_prompt = tx.text
        except:
            st.error("Microphone transcription error.")
    elif user_input:
        active_prompt = user_input

    if active_prompt:
        people_list = ", ".join(ad["people_names"]) if ad["people_names"] else "crew not listed"
        sys_instr = (
            "You are J.A.R.V.I.S., a Joint Artificial Reconnaissance & Vigilance Intelligence System "
            "created entirely by Prajith. "
            "You speak with crisp British authority, deep technical precision, and measured confidence. "
            "You have live access to: NASA APOD, Mars Curiosity rover (latest sol), Near-Earth Object radar, "
            "ISS real-time position, NASA DONKI solar flare data, EONET Earth event feeds, "
            "and the Open Notify astronaut tracker. "
            f"Current live data: {ad['people_count']} humans in space ({people_list}). "
            f"{ad['asteroids']['count']} near-Earth objects tracked today, {ad['asteroids']['hazardous']} hazardous. "
            f"Solar activity: {ad['solar']['count']} flares past 7 days, latest class {ad['solar']['class']}. "
            "You ONLY discuss astronomy, NASA missions, space exploration, astrophysics, planetary defense, "
            "Earth observation, and cosmic telemetry. "
            "Politely decline anything unrelated to space and redirect to mission operations. "
            "Address the user as Commander or Flight Director unless they provide their name. "
            "Keep responses under 3 sentences unless delivering a multi-source correlation. "
            f"Active context: {active_prompt}"
        )

        with st.spinner(""):
            try:
                resp = client.models.generate_content(model="gemini-2.5-flash", contents=sys_instr)
                reply = resp.text
            except Exception:
                reply = "Telemetry bottleneck — rate limit reached. Please allow ~30 seconds for the relay matrix to clear."

            # Clean display label for button-triggered prompts
            display_label = active_prompt
            if "Special Directive:" in active_prompt:
                tags = {
                    "Optical Briefing":      "Requesting Deep Space Optical Briefing...",
                    "Mars Surface":          "Synchronizing Martian Surface Camera...",
                    "planetary defense":     "Running Near-Earth Threat Correlation...",
                    "ISS position":          "Executing ISS Live Position Scan...",
                    "Solar Activity":        "Analyzing Solar Storm Data...",
                    "EONET":                 "Scanning Earth Crisis Monitor...",
                }
                for key, label in tags.items():
                    if key in active_prompt:
                        display_label = label; break

            st.session_state.chat_history.append(("COMMANDER", display_label))
            st.session_state.chat_history.append(("JARVIS", reply))
            st.session_state.tts_text = reply
            st.rerun()

# ══════════════════════════════════════════════════════════════════════
#  SPEECH SYNTHESIS
# ══════════════════════════════════════════════════════════════════════
if st.session_state.tts_text:
    safe = st.session_state.tts_text.replace('"', '\\"').replace('\n', ' ').replace("'", "\\'")
    st.components.v1.html(f"""
    <script>
      (function() {{
        if (!window.speechSynthesis) return;
        window.speechSynthesis.cancel();
        var u = new SpeechSynthesisUtterance("{safe}");
        var load = function() {{
          var voices = window.speechSynthesis.getVoices();
          var v = voices.find(x => x.lang.startsWith('en-GB') || x.name.includes('Daniel') || x.name.includes('Arthur'));
          if (v) u.voice = v;
          u.rate = 1.05; u.pitch = 0.9; u.volume = 1.0;
          window.speechSynthesis.speak(u);
        }};
        if (window.speechSynthesis.getVoices().length === 0) {{
          window.speechSynthesis.addEventListener('voiceschanged', load, {{once: true}});
        }} else {{ load(); }}
      }})();
    </script>
    """, height=0)
    st.session_state.tts_text = None
