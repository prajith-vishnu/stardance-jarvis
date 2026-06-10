import streamlit as st
import requests
import pandas as pd
from datetime import datetime, timedelta
from google import genai
from google.genai import types

st.set_page_config(
    page_title="J.A.R.V.I.S. // NASA CORE",
    page_icon="🚀",
    layout="wide",
    initial_sidebar_state="collapsed",
)

st.markdown("""<style>
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700;800&family=JetBrains+Mono:wght@400;500;600&display=swap');

*,*::before,*::after{box-sizing:border-box;}

html,body,[data-testid="stAppViewContainer"],.stApp{
    background:#060A15!important;color:#94A3B8!important;
    font-family:'Inter',-apple-system,sans-serif!important;
}
[data-testid="stHeader"]{display:none!important;}
[data-testid="stSidebar"]{display:none!important;}
.block-container{
    padding-top:20px!important;padding-bottom:8px!important;
    padding-left:28px!important;padding-right:28px!important;
    max-width:100%!important;
}

.stApp::before{
    content:'';position:fixed;top:-220px;left:50%;transform:translateX(-50%);
    width:900px;height:440px;
    background:radial-gradient(ellipse,rgba(14,165,233,.05)0%,transparent 65%);
    pointer-events:none;z-index:0;
}

h1,h2,h3,h4,h5{
    font-family:'Inter',sans-serif!important;color:#F1F5F9!important;
    font-weight:600!important;letter-spacing:-0.3px!important;
}

.slbl{
    font-family:'JetBrains Mono',monospace;font-size:9px;font-weight:600;
    color:rgba(14,165,233,.4);letter-spacing:2.5px;text-transform:uppercase;
    display:block;margin:10px 0 8px;
}

/* Arc Reactor */
.orb-wrap{display:flex;flex-direction:column;align-items:center;padding:8px 0 4px;}
.arc-r{position:relative;width:72px;height:72px;display:flex;align-items:center;justify-content:center;}
.arc-core{
    width:20px;height:20px;
    background:radial-gradient(circle at 35% 30%,#BAE6FD 0%,#0EA5E9 50%,#0369A1 100%);
    border-radius:50%;
    box-shadow:0 0 10px #0EA5E9,0 0 25px rgba(14,165,233,.6),0 0 50px rgba(14,165,233,.2);
    animation:cpulse 2.8s ease-in-out infinite;z-index:4;position:relative;
}
.arc-hex{
    position:absolute;width:30px;height:30px;
    border:1px solid rgba(14,165,233,.45);transform:rotate(45deg);z-index:3;
}
.arc-ring1{
    position:absolute;width:46px;height:46px;border-radius:50%;
    border:1.5px solid rgba(14,165,233,.28);animation:rspin 5s linear infinite;z-index:2;
}
.arc-ring1::before{
    content:'';position:absolute;top:-3px;left:calc(50% - 3px);
    width:6px;height:6px;background:#0EA5E9;border-radius:50%;box-shadow:0 0 8px #0EA5E9;
}
.arc-ring2{
    position:absolute;width:64px;height:64px;border-radius:50%;
    border:1px solid rgba(14,165,233,.09);animation:rspin 11s linear infinite reverse;z-index:1;
}
.arc-ring2::before{
    content:'';position:absolute;top:-2px;left:calc(50% - 2px);
    width:4px;height:4px;background:rgba(14,165,233,.35);border-radius:50%;
}
@keyframes cpulse{
    0%,100%{transform:scale(.95);box-shadow:0 0 8px #0EA5E9,0 0 20px rgba(14,165,233,.5),0 0 40px rgba(14,165,233,.15);}
    50%{transform:scale(1.06);box-shadow:0 0 14px #0EA5E9,0 0 35px rgba(14,165,233,.7),0 0 65px rgba(14,165,233,.25);}
}
@keyframes rspin{from{transform:rotate(0deg);}to{transform:rotate(360deg);}}
.orb-lbl{
    font-family:'JetBrains Mono',monospace;font-size:8px;letter-spacing:3px;
    color:rgba(14,165,233,.4);text-transform:uppercase;
    margin-top:9px;display:flex;align-items:center;gap:5px;
}
.sdot{
    width:5px;height:5px;background:#10B981;border-radius:50%;
    box-shadow:0 0 5px #10B981;animation:dblink 2s ease-in-out infinite;
}
@keyframes dblink{0%,100%{opacity:1;}50%{opacity:.25;}}

/* Header */
.hbar{
    display:flex;align-items:center;justify-content:space-between;
    padding-bottom:14px;border-bottom:1px solid rgba(255,255,255,.05);
    margin-bottom:16px;
}
.brand{display:flex;flex-direction:column;gap:2px;}
.bname{font-family:'Inter',sans-serif;font-size:21px;font-weight:800;color:#F1F5F9;letter-spacing:-0.8px;line-height:1;}
.bname .a{color:#0EA5E9;}
.bsub{font-family:'JetBrains Mono',monospace;font-size:7px;color:rgba(148,163,184,.3);letter-spacing:2.5px;text-transform:uppercase;}
.pills{display:flex;align-items:center;gap:6px;flex-wrap:wrap;}
.pill{
    display:inline-flex;align-items:center;gap:5px;
    font-family:'JetBrains Mono',monospace;font-size:9px;font-weight:500;
    padding:4px 10px 4px 7px;border-radius:6px;border:1px solid;white-space:nowrap;
}
.pd{width:5px;height:5px;border-radius:50%;flex-shrink:0;}
.pb{background:rgba(14,165,233,.07);border-color:rgba(14,165,233,.2);color:#7DD3FC;}
.pr{background:rgba(239,68,68,.08);border-color:rgba(239,68,68,.25);color:#FCA5A5;}
.pa{background:rgba(245,158,11,.08);border-color:rgba(245,158,11,.25);color:#FCD34D;}
.pg{background:rgba(16,185,129,.07);border-color:rgba(16,185,129,.2);color:#6EE7B7;}
.px{background:rgba(255,255,255,.02);border-color:rgba(255,255,255,.07);color:#475569;}
.db{background:#0EA5E9;box-shadow:0 0 4px #0EA5E9;}
.dr{background:#EF4444;box-shadow:0 0 4px #EF4444;}
.da{background:#F59E0B;box-shadow:0 0 4px #F59E0B;}
.dg{background:#10B981;box-shadow:0 0 4px #10B981;}
.dx{background:#475569;}
.psep{width:1px;height:16px;background:rgba(255,255,255,.06);}

/* Containers */
[data-testid="stVerticalBlockBorderCard"]{
    background:rgba(255,255,255,.018)!important;
    border:1px solid rgba(255,255,255,.06)!important;
    border-radius:12px!important;box-shadow:0 4px 32px rgba(0,0,0,.35)!important;
}

/* Metrics */
[data-testid="stMetric"]{
    background:rgba(255,255,255,.022)!important;
    border:1px solid rgba(255,255,255,.05)!important;
    border-radius:8px!important;padding:12px 14px!important;
}
[data-testid="stMetricLabel"] p{
    font-family:'JetBrains Mono',monospace!important;font-size:8px!important;
    letter-spacing:1.8px!important;text-transform:uppercase!important;
    color:rgba(148,163,184,.45)!important;
}
[data-testid="stMetricValue"]{
    font-family:'JetBrains Mono',monospace!important;font-size:22px!important;
    color:#F1F5F9!important;font-weight:600!important;
}
[data-testid="stMetricDelta"] svg{display:none!important;}
[data-testid="stMetricDelta"]>div{
    font-family:'JetBrains Mono',monospace!important;
    font-size:9px!important;color:rgba(14,165,233,.45)!important;
}

/* Buttons */
.stButton>button{
    background:rgba(255,255,255,.02)!important;color:#475569!important;
    font-family:'JetBrains Mono',monospace!important;font-weight:500!important;
    font-size:9px!important;letter-spacing:.8px!important;
    border:1px solid rgba(255,255,255,.06)!important;border-radius:8px!important;
    padding:10px 6px!important;width:100%!important;text-align:center!important;
    transition:all .15s cubic-bezier(.4,0,.2,1)!important;line-height:1.5!important;
}
.stButton>button:hover{
    background:rgba(14,165,233,.05)!important;border-color:rgba(14,165,233,.22)!important;
    color:#7DD3FC!important;
    box-shadow:0 0 16px rgba(14,165,233,.07),0 2px 8px rgba(0,0,0,.2)!important;
    transform:translateY(-1px)!important;
}
.stButton>button:active{transform:translateY(0)!important;}

/* Boot button */
.boot-wrap div button{
    background:rgba(14,165,233,.04)!important;
    border:1px solid rgba(14,165,233,.28)!important;color:#0EA5E9!important;
    font-size:11px!important;font-weight:600!important;letter-spacing:3px!important;
    padding:14px 24px!important;border-radius:8px!important;
    box-shadow:0 0 28px rgba(14,165,233,.08),inset 0 0 16px rgba(14,165,233,.02)!important;
    width:100%!important;
}
.boot-wrap div button:hover{
    background:rgba(14,165,233,.09)!important;
    box-shadow:0 0 45px rgba(14,165,233,.18),inset 0 0 16px rgba(14,165,233,.04)!important;
    color:#BAE6FD!important;
}

/* Chat */
.chat-row{margin-bottom:9px;}
.chat-sndr{
    font-family:'JetBrains Mono',monospace;font-size:8px;font-weight:600;
    letter-spacing:1.5px;text-transform:uppercase;margin-bottom:3px;padding:0 3px;
}
.su{color:rgba(148,163,184,.35);text-align:right;}
.sj{color:rgba(14,165,233,.5);}
.chat-bbl{padding:10px 14px;border-radius:12px;font-size:13px;line-height:1.65;font-family:'Inter',sans-serif;}
.cbu{
    background:rgba(255,255,255,.03);border:1px solid rgba(255,255,255,.07);
    color:#CBD5E1;margin-left:18%;border-bottom-right-radius:4px;
}
.cbj{
    background:rgba(14,165,233,.05);border:1px solid rgba(14,165,233,.1);
    color:#E2E8F0;margin-right:18%;border-bottom-left-radius:4px;
}

/* Chat input */
div[data-testid="stChatInput"]{
    background:rgba(255,255,255,.025)!important;
    border:1px solid rgba(255,255,255,.08)!important;border-radius:10px!important;
}
div[data-testid="stChatInput"]:focus-within{
    border-color:rgba(14,165,233,.28)!important;
    box-shadow:0 0 0 3px rgba(14,165,233,.05)!important;
}
div[data-testid="stChatInput"] textarea{
    color:#E2E8F0!important;font-size:13px!important;font-family:'Inter',sans-serif!important;
}

[data-testid="stImage"] img{border-radius:10px!important;border:1px solid rgba(255,255,255,.06)!important;}

/* Events */
.ev-card{
    padding:10px 14px;margin-bottom:6px;border-radius:8px;
    background:rgba(255,255,255,.02);border:1px solid rgba(255,255,255,.05);
    display:flex;align-items:center;gap:10px;
}
.ev-cat{
    font-family:'JetBrains Mono',monospace;font-size:8px;font-weight:600;
    letter-spacing:1px;text-transform:uppercase;padding:3px 8px;border-radius:4px;flex-shrink:0;
}
.ec-fire{background:rgba(239,68,68,.1);color:#FCA5A5;border:1px solid rgba(239,68,68,.2);}
.ec-storm{background:rgba(99,102,241,.1);color:#C7D2FE;border:1px solid rgba(99,102,241,.2);}
.ec-vol{background:rgba(245,158,11,.1);color:#FCD34D;border:1px solid rgba(245,158,11,.2);}
.ec-def{background:rgba(14,165,233,.08);color:#7DD3FC;border:1px solid rgba(14,165,233,.18);}
.ev-ttl{font-size:12px;color:#CBD5E1;font-family:'Inter',sans-serif;}

.dcapt{
    font-family:'JetBrains Mono',monospace;font-size:9px;
    color:rgba(148,163,184,.4);letter-spacing:.5px;margin-top:7px;line-height:1.5;
}

.stAlert{background:rgba(255,255,255,.02)!important;border:1px solid rgba(255,255,255,.07)!important;border-radius:8px!important;font-size:12px!important;}
.stCaption p{font-family:'JetBrains Mono',monospace!important;font-size:9px!important;color:rgba(148,163,184,.38)!important;}
[data-testid="stAudioInput"]{background:rgba(255,255,255,.02)!important;border:1px solid rgba(255,255,255,.07)!important;border-radius:10px!important;}
.stSpinner>div{border-top-color:#0EA5E9!important;}
::-webkit-scrollbar{width:3px;}
::-webkit-scrollbar-track{background:transparent;}
::-webkit-scrollbar-thumb{background:rgba(255,255,255,.07);border-radius:3px;}
::-webkit-scrollbar-thumb:hover{background:rgba(14,165,233,.2);}
</style>""", unsafe_allow_html=True)

# ── Session State ──
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

# ── Credentials ──
if "GEMINI_API_KEY" not in st.secrets or "NASA_API_KEY" not in st.secrets:
    st.error("SECRETS MISSING — add NASA_API_KEY and GEMINI_API_KEY to .streamlit/secrets.toml")
    st.stop()

NASA_KEY   = st.secrets["NASA_API_KEY"]
GEMINI_KEY = st.secrets["GEMINI_API_KEY"]

# ── NASA API Functions ──
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

# ── Auto-load on first render ──
if st.session_state.auto_data is None:
    with st.spinner("Initializing JARVIS neural core..."):
        people_count, people_names = get_people_in_space()
        asteroids = get_asteroid_radar()
        solar     = get_solar_activity()
        apod      = get_apod()
        st.session_state.auto_data = {
            "people_count": people_count,
            "people_names": people_names,
            "asteroids":    asteroids,
            "solar":        solar,
            "apod":         apod,
        }
        if apod and apod.get("media_type") == "image":
            st.session_state.display = {
                "type": "apod",
                "img_url": apod.get("url"),
                "title": apod.get("title", ""),
                "caption": apod.get("date", ""),
            }
        threat = "ELEVATED" if asteroids["hazardous"] > 0 else "NOMINAL"
        solar_line = f"{solar['count']} flare events, latest class {solar['class']}" if solar["active"] else "space weather nominal"
        st.session_state.chat_history = [(
            "JARVIS",
            f"<b>ALL SYSTEMS ONLINE — NASA CORE ACTIVE</b><br><br>"
            f"Good day. I am J.A.R.V.I.S., your Joint Artificial Reconnaissance & Vigilance Intelligence System, "
            f"designed and built by Prajith.<br><br>"
            f"<b>LIVE MISSION STATUS</b><br>"
            f"· <b>{people_count} humans</b> currently in space<br>"
            f"· <b>{asteroids['count']} near-Earth objects</b> tracked today — threat level: <b>{threat}</b><br>"
            f"· Solar activity: {solar_line}<br><br>"
            f"Today's deep space image is loaded in the display panel. Use the mission directives to query any active feed."
        )]

ad = st.session_state.auto_data

# ── Gemini ──
client = genai.Client(api_key=GEMINI_KEY)

# ── Header ──
threat_pill = "pr" if ad["asteroids"]["hazardous"] > 0 else "pg"
threat_dot  = "dr" if ad["asteroids"]["hazardous"] > 0 else "dg"
threat_txt  = f"THREAT ELEVATED · {ad['asteroids']['hazardous']} HAZARDOUS" if ad["asteroids"]["hazardous"] > 0 else "THREAT NOMINAL"
solar_pill  = "pa" if ad["solar"]["active"] else "pb"
solar_dot   = "da" if ad["solar"]["active"] else "db"
solar_txt   = f"SOLAR CLASS {ad['solar']['class']}" if ad["solar"]["active"] else "SOLAR NOMINAL"

st.markdown(f"""
<div class="hbar">
  <div class="brand">
    <div class="bname">J<span class="a">.</span>A<span class="a">.</span>R<span class="a">.</span>V<span class="a">.</span>I<span class="a">.</span>S<span class="a">.</span></div>
    <div class="bsub">Joint Artificial Reconnaissance &amp; Vigilance Intelligence System</div>
  </div>
  <div class="pills">
    <span class="pill pb"><span class="pd db"></span>{ad['people_count']} HUMANS IN SPACE</span>
    <span class="pill pb"><span class="pd db"></span>{ad['asteroids']['count']} NEAR-EARTH OBJECTS</span>
    <span class="pill {threat_pill}"><span class="pd {threat_dot}"></span>{threat_txt}</span>
    <span class="pill {solar_pill}"><span class="pd {solar_dot}"></span>{solar_txt}</span>
    <div class="psep"></div>
    <span class="pill px">{datetime.utcnow().strftime('%H:%M UTC')}</span>
  </div>
</div>
""", unsafe_allow_html=True)

# ── Layout ──
left, right = st.columns([1.15, 1.0], gap="large")
forced_prompt = ""

# ── LEFT PANEL ──
with left:
    with st.container(height=370, border=True):
        disp = st.session_state.display

        if disp["type"] in ("apod", "mars", "epic") and disp.get("img_url"):
            type_label = {"apod": "NASA ASTRONOMY PICTURE OF THE DAY", "mars": "MARS CURIOSITY ROVER — LIVE SURFACE", "epic": "DSCOVR EPIC — FULL DISK EARTH"}.get(disp["type"], "LIVE IMAGE FEED")
            st.markdown(f"<span class='slbl'>{type_label}</span>", unsafe_allow_html=True)
            st.image(disp["img_url"], use_container_width=True)
            if disp.get("title"):
                caption = disp["title"]
                if disp.get("caption"):
                    caption += f"  ·  {disp['caption']}"
                st.markdown(f"<p class='dcapt'>{caption}</p>", unsafe_allow_html=True)

        elif disp["type"] == "iss" and st.session_state.iss_pos:
            lat, lon = st.session_state.iss_pos
            st.markdown("<span class='slbl'>ISS ORBITAL TRACKER — REAL-TIME POSITION</span>", unsafe_allow_html=True)
            try:
                import pydeck as pdk
                deck = pdk.Deck(
                    layers=[pdk.Layer(
                        "ScatterplotLayer",
                        data=[{"lat": lat, "lon": lon}],
                        get_position=["lon", "lat"],
                        get_fill_color=[14, 165, 233, 220],
                        get_radius=700000,
                        radius_min_pixels=8,
                        radius_max_pixels=18,
                    )],
                    initial_view_state=pdk.ViewState(latitude=lat, longitude=lon, zoom=0.7, pitch=18),
                    map_style="https://basemaps.cartocdn.com/gl/dark-matter-gl-style/style.json",
                    tooltip={"text": f"ISS  {lat:.2f}°, {lon:.2f}°"},
                )
                st.pydeck_chart(deck, use_container_width=True)
            except Exception:
                st.map(pd.DataFrame({"lat": [lat], "lon": [lon]}), zoom=0)
            st.markdown(
                f"<p class='dcapt'>ISS POSITION  ·  {lat:.2f}°N  {lon:.2f}°E  ·  ALTITUDE ~408 km  ·  27,600 km/h</p>",
                unsafe_allow_html=True
            )

        elif disp["type"] == "earth_events" and disp.get("events"):
            st.markdown("<span class='slbl'>EONET — NASA ACTIVE EARTH EVENTS</span>", unsafe_allow_html=True)
            cat_map = {"Wildfires": "ec-fire", "Severe Storms": "ec-storm", "Volcanoes": "ec-vol"}
            for ev in disp["events"]:
                css = cat_map.get(ev["cat"], "ec-def")
                st.markdown(
                    f'<div class="ev-card">'
                    f'<span class="ev-cat {css}">{ev["cat"]}</span>'
                    f'<span class="ev-ttl">{ev["title"]}</span>'
                    f'</div>',
                    unsafe_allow_html=True
                )

        else:
            st.markdown("<span class='slbl'>PLANETARY DEFENSE — LIVE RADAR</span>", unsafe_allow_html=True)
            a = ad["asteroids"]
            c1, c2 = st.columns(2)
            with c1:
                st.metric("NEAR-EARTH OBJECTS", str(a["count"]), "Tracked Today")
                st.metric("CLOSEST APPROACH", f"{a['closest_km']:,} km", a["closest_name"][:20])
            with c2:
                badge = "HAZARDOUS DETECTED" if a["hazardous"] > 0 else "ALL NOMINAL"
                st.metric("THREAT OBJECTS", str(a["hazardous"]), badge)
                s = ad["solar"]
                st.metric("SOLAR FLARES / 7D", str(s["count"]), f"Latest class {s['class']}")

    st.markdown("<span class='slbl'>MISSION DIRECTIVES</span>", unsafe_allow_html=True)
    r1c1, r1c2, r1c3 = st.columns(3)
    r2c1, r2c2, r2c3 = st.columns(3)

    with r1c1:
        if st.button("📡 DEEP SPACE\nOPTICS"):
            with st.spinner(""):
                apod = get_apod()
                if apod and apod.get("media_type") == "image":
                    st.session_state.display = {"type": "apod", "img_url": apod["url"],
                                                "title": apod.get("title"), "caption": apod.get("date")}
                    forced_prompt = (f"Special Directive: Optical Briefing. "
                                     f"Title: {apod.get('title')}. "
                                     f"Detail: {apod.get('explanation','')[:400]}")
    with r1c2:
        if st.button("🔴 MARS ROVER\nSURFACE"):
            with st.spinner(""):
                mars = get_mars_latest()
                if mars:
                    st.session_state.display = {"type": "mars", "img_url": mars["img"],
                                                "title": f"{mars['rover']} — Sol {mars['sol']}",
                                                "caption": mars["date"]}
                    forced_prompt = (f"Special Directive: Mars Surface. Live imaging from {mars['rover']} rover. "
                                     f"Sol {mars['sol']}, earth date {mars['date']}. Camera: {mars['camera']}. "
                                     f"Status: {mars['status']}. Give a crisp 2-sentence tactical surface report.")
    with r1c3:
        if st.button("☄️ THREAT\nANALYSIS"):
            with st.spinner(""):
                ast = get_asteroid_radar()
                sol = get_solar_activity()
                threat = "ELEVATED" if ast["hazardous"] > 0 else "NOMINAL"
                solar_line = f"{sol['count']} solar flares (7d), latest class {sol['class']}" if sol["active"] else "no significant solar activity"
                st.session_state.display = {"type": "asteroids", "img_url": None, "title": None, "caption": None}
                forced_prompt = (f"Special Directive: Multi-source planetary defense correlation. "
                                 f"ASTEROID RADAR: {ast['count']} NEOs today. Hazardous: {ast['hazardous']}. "
                                 f"Closest: {ast['closest_name']} at {ast['closest_km']:,} km. Threat: {threat}. "
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
        if st.button("☀️ SOLAR\nACTIVITY"):
            with st.spinner(""):
                sol = get_solar_activity()
                if sol:
                    forced_prompt = (f"Special Directive: DONKI Solar Activity. "
                                     f"{sol['count']} solar flare events past 7 days. "
                                     f"Latest class: {sol['class']}. Peak: {sol['peak']}. "
                                     f"Give a 2-sentence space weather briefing and mission advisory.")
    with r2c3:
        if st.button("🌍 EARTH\nEVENTS"):
            with st.spinner(""):
                events = get_earth_events()
                if events:
                    st.session_state.display = {"type": "earth_events", "img_url": None,
                                                "title": None, "caption": None, "events": events}
                    summary = "; ".join([f"{e['title']} ({e['cat']})" for e in events])
                    forced_prompt = (f"Special Directive: EONET Earth Monitoring. "
                                     f"NASA satellites detected: {summary}. "
                                     f"Give a 3-sentence Earth systems status briefing.")
                else:
                    forced_prompt = "Special Directive: EONET shows no active natural events. Give a 1-sentence all-clear."

# ── RIGHT PANEL ──
with right:
    st.markdown("""
    <div class="orb-wrap">
      <div class="arc-r">
        <div class="arc-ring2"></div>
        <div class="arc-ring1"></div>
        <div class="arc-hex"></div>
        <div class="arc-core"></div>
      </div>
      <div class="orb-lbl"><span class="sdot"></span>JARVIS CORE · ONLINE</div>
    </div>
    """, unsafe_allow_html=True)

    with st.container(height=385, border=True):
        for speaker, msg in st.session_state.chat_history:
            if speaker == "COMMANDER":
                st.markdown(
                    f'<div class="chat-row">'
                    f'<div class="chat-sndr su">COMMANDER</div>'
                    f'<div class="chat-bbl cbu">{msg}</div>'
                    f'</div>',
                    unsafe_allow_html=True
                )
            else:
                st.markdown(
                    f'<div class="chat-row">'
                    f'<div class="chat-sndr sj">J.A.R.V.I.S.</div>'
                    f'<div class="chat-bbl cbj">{msg}</div>'
                    f'</div>',
                    unsafe_allow_html=True
                )

    st.write("")

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
        st.caption("Click above to enable voice output and terminal input")
        user_input  = None
        voice_input = None
    else:
        input_col, mic_col = st.columns([3.5, 1.5], vertical_alignment="bottom")
        with input_col:
            user_input = st.chat_input("Query NASA feeds or ask JARVIS anything...")
        with mic_col:
            voice_input = st.audio_input("", label_visibility="collapsed", key="mic")

# ── Inference Engine ──
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

            display_label = active_prompt
            if "Special Directive:" in active_prompt:
                tags = {
                    "Optical Briefing":  "Requesting Deep Space Optical Briefing...",
                    "Mars Surface":      "Synchronizing Martian Surface Camera...",
                    "planetary defense": "Running Near-Earth Threat Correlation...",
                    "ISS position":      "Executing ISS Live Position Scan...",
                    "Solar Activity":    "Analyzing Solar Activity Data...",
                    "EONET":             "Scanning Earth Events Monitor...",
                }
                for key, label in tags.items():
                    if key in active_prompt:
                        display_label = label; break

            st.session_state.chat_history.append(("COMMANDER", display_label))
            st.session_state.chat_history.append(("JARVIS", reply))
            st.session_state.tts_text = reply
            st.rerun()

# ── Speech Synthesis ──
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
