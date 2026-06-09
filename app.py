import streamlit as st
import os
import requests
from datetime import datetime
from google import genai
from google.genai import types

# =====================================================================
# SYSTEM CORE CONFIGURATION & ZERO-PADDING SCREEN LOCK (CSS)
# =====================================================================
st.set_page_config(page_title="JARVIS Mainframe", page_icon="🤖", layout="wide")

st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Plus+Jakarta+Sans:wght@300;400;500;600;700&family=JetBrains+Mono:wght@400;500&display=swap');

/* CRITICAL SCREEN LOCK: Anchors everything to 100% of your viewport height with zero scrolling allowed */
html, body, [data-testid="stAppViewContainer"], .stApp {
    background-color: #080A10 !important;
    color: #E4E4E7 !important;
    font-family: 'Plus Jakarta Sans', sans-serif !important;
    height: 100vh !important;
    overflow: hidden !important;
}

/* TOTAL HEADER DELETION: Hides Streamlit's native top menu bar entirely to claim the upper screen space */
[data-testid="stHeader"] {
    display: none !important;
}

/* MAX SPACE OPTIMIZATION: Shrinks top and bottom cushions to absolute minimal layout footprint */
.block-container {
    padding-top: 1rem !important;
    padding-bottom: 0rem !important;
    padding-left: 2.5rem !important;
    padding-right: 2.5rem !important;
    max-width: 98% !important;
}

/* Sidebar structure configuration */
[data-testid="stSidebar"] {
    background-color: #0D101D !important;
    border-right: 1px solid rgba(255, 255, 255, 0.05) !important;
}

/* Typography elements */
h1, h2, h3, h4, h5 {
    font-family: 'Plus Jakarta Sans', sans-serif !important;
    color: #FFFFFF !important;
    font-weight: 700 !important;
    letter-spacing: -0.5px !important;
    margin-top: 0px !important;
    margin-bottom: 4px !important;
}

/* Floating interface slate grids */
div[data-testid="stVerticalBlockBorderCard"] {
    background: #0E1224 !important;
    border: 1px solid rgba(255, 255, 255, 0.06) !important;
    border-radius: 16px !important;
    padding: 16px !important;
    box-shadow: 0 12px 40px rgba(0, 0, 0, 0.3) !important;
}

/* THE PULSING AI CORE SUBROUTINE (SIRI/JARVIS STYLE) */
.orb-wrapper {
    display: flex;
    flex-direction: column;
    align-items: center;
    justify-content: center;
    margin: 0px auto 8px auto;
    text-align: center;
}

.jarvis-pulse-orb {
    width: 70px;
    height: 70px;
    background: radial-gradient(circle, #00E5FF 0%, #0066FF 60%, #080A10 100%);
    border-radius: 50%;
    position: relative;
    box-shadow: 0 0 25px rgba(0, 229, 255, 0.4), inset 0 0 12px rgba(255, 255, 255, 0.6);
    animation: siri-pulse 2.5s infinite ease-in-out;
}

.jarvis-pulse-orb::before {
    content: '';
    position: absolute;
    top: -5px; left: -5px; right: -5px; bottom: -5px;
    border: 1px solid rgba(0, 229, 255, 0.25);
    border-radius: 50%;
    animation: outer-ring-pulse 2.5s infinite ease-in-out;
}

.orb-status-text {
    font-family: 'JetBrains Mono', monospace !important;
    font-size: 10px !important;
    color: #00E5FF !important;
    letter-spacing: 1.5px;
    margin-top: 6px;
    text-transform: uppercase;
    opacity: 0.8;
}

@keyframes siri-pulse {
    0% { transform: scale(0.95); box-shadow: 0 0 20px rgba(0, 229, 255, 0.3); }
    50% { transform: scale(1.03); box-shadow: 0 0 40px rgba(0, 229, 255, 0.6); background: radial-gradient(circle, #26F0FF 0%, #0077FF 70%, #080A10 100%); }
    100% { transform: scale(0.95); box-shadow: 0 0 20px rgba(0, 229, 255, 0.3); }
}

@keyframes outer-ring-pulse {
    0% { transform: scale(0.96); opacity: 0.3; }
    50% { transform: scale(1.1); opacity: 0.7; border-color: rgba(0, 229, 255, 0.5); }
    100% { transform: scale(0.96); opacity: 0.3; }
}

/* Chat bubble structures */
.chat-bubble {
    padding: 12px 16px;
    border-radius: 12px;
    margin-bottom: 10px;
    font-size: 14px;
    line-height: 1.5;
    max-width: 85%;
}
.commander-bubble {
    background-color: rgba(255, 255, 255, 0.03);
    border: 1px solid rgba(255, 255, 255, 0.06);
    color: #E4E4E7;
    margin-left: auto;
    border-bottom-right-radius: 4px;
}
.jarvis-bubble {
    background: linear-gradient(135deg, rgba(0, 113, 227, 0.08) 0%, rgba(0, 229, 255, 0.04) 100%);
    border: 1px solid rgba(0, 229, 255, 0.18);
    color: #F4F4F5;
    margin-right: auto;
    border-bottom-left-radius: 4px;
}

/* Prompt Console Dock */
div[data-testid="stChatInput"] {
    background-color: #0E1224 !important;
    border: 1px solid rgba(255, 255, 255, 0.08) !important;
    border-radius: 12px !important;
}
div[data-testid="stChatInput"] textarea {
    color: #FFFFFF !important;
    font-family: 'Plus Jakarta Sans', sans-serif !important;
}

/* Action directive buttons configuration */
.stButton button {
    background-color: rgba(255, 255, 255, 0.02) !important;
    color: #FFFFFF !important;
    font-weight: 500 !important;
    font-size: 13px !important;
    border: 1px solid rgba(255, 255, 255, 0.06) !important;
    border-radius: 10px !important;
    padding: 12px 16px !important;
    width: 100% !important;
    text-align: left !important;
}
.stButton button:hover {
    background-color: rgba(0, 229, 255, 0.06) !important;
    border-color: #00E5FF !important;
    color: #00E5FF !important;
}

/* 👑 MASSIVE CINEMATIC STARTUP BUTTON OVERRIDE CSS RULES */
.boot-container div button {
    background: linear-gradient(135deg, rgba(0, 229, 255, 0.2) 0%, rgba(0, 102, 255, 0.3) 100%) !important;
    border: 2px solid #00E5FF !important;
    color: #00E5FF !important;
    font-weight: 700 !important;
    font-size: 20px !important;
    letter-spacing: 2px !important;
    text-align: center !important;
    padding: 24px 40px !important;
    border-radius: 16px !important;
    box-shadow: 0 0 30px rgba(0, 229, 255, 0.3) !important;
    transition: all 0.3s ease !important;
}
.boot-container div button:hover {
    background: linear-gradient(135deg, rgba(0, 229, 255, 0.4) 0%, rgba(0, 102, 255, 0.6) 100%) !important;
    box-shadow: 0 0 50px rgba(0, 229, 255, 0.6) !important;
    transform: scale(1.02);
    color: #FFFFFF !important;
}
</style>
""", unsafe_allow_html=True)

# Continuous Chat Stream Memory Registry
if "chat_history" not in st.session_state:
    st.session_state.chat_history = [
        ("JARVIS CORE", "🚀 <b>NASA TELEMETRY MODE ACTIVATED</b> // ARCHITECT: PRAJITH<br><br>Hello, I am JARVIS. I am an advanced deep-space communications AI designed and built by Prajith. My core is locked into <b>Full NASA Mode</b>.<br><br><b>AVAILABLE MISSION OPERATIONS:</b><br>• <b>Starboard Deck (Right):</b> Run live satellite scans, synchronize Martian rover feeds, or track incoming near-Earth asteroids.<br>• <b>Terminal Feed (Below):</b> Use voice or text to query astrophysics data, planet tracking, or live cosmic systems.")
    ]
if "last_processed_audio" not in st.session_state:
    st.session_state.last_processed_audio = None
if "text_to_speak" not in st.session_state:
    st.session_state.text_to_speak = None
if "vocal_matrix_initialized" not in st.session_state:
    st.session_state.vocal_matrix_initialized = False

# Secure Credentials Vault Verification
if "GEMINI_API_KEY" not in st.secrets or "NASA_API_KEY" not in st.secrets:
    st.error("🔒 SYSTEM CONFIGURATION INTERCEPTED: Deployment environment secrets missing.")
    st.stop()

NASA_KEY = st.secrets["NASA_API_KEY"]
GEMINI_KEY = st.secrets["GEMINI_API_KEY"]

# =====================================================================
# SECURE TELEMETRY EXTRACTION ENGINE
# =====================================================================
def get_space_briefing():
    try:
        res = requests.get(f"https://api.nasa.gov/planetary/apod?api_key={NASA_KEY}")
        return res.json() if res.status_code == 200 else None
    except: return None

def get_mars_telemetry():
    try:
        res = requests.get(f"https://api.nasa.gov/mars-photos/api/v1/rovers/curiosity/photos?sol=1000&page=1&api_key={NASA_KEY}")
        photos = res.json().get("photos", [])
        return photos[0] if photos else None
    except: return None

def get_asteroid_radar():
    today = datetime.today().strftime('%Y-%m-%d')
    try:
        res = requests.get(f"https://api.nasa.gov/neo/rest/v1/feed?start_date={today}&end_date={today}&api_key={NASA_KEY}").json()
        return res.get("element_count", 0), res.get("near_earth_objects", {}).get(today, [])
    except: return 0, []

# =====================================================================
# FRONTEND MAIN CONSOLE COMMAND CENTER
# =====================================================================
client = genai.Client(api_key=GEMINI_KEY)

# System Metrics Instrument Sidebar Panel
st.sidebar.markdown("<p style='font-weight:600; color:#FFFFFF; margin-bottom:8px;'>CORE STATUS</p>", unsafe_allow_html=True)
st.sidebar.metric(label="Mainframe Core Temp", value="34°C", delta="Nominal")
st.sidebar.metric(label="Bus Sync Latency", value="14 ms", delta="Optimal")
st.sidebar.write("---")
st.sidebar.caption(f"Sync Time: {datetime.now().strftime('%H:%M:%S MST')}")

# Split Workspace: Left Chat Pipeline // Right Telemetry Panel
left_deck, right_deck = st.columns([1.4, 1.0], gap="large")

forced_trigger_prompt = ""

# ---------------------------------------------------------------------
# RIGHT DECK: QUICK COMMAND INJECTORS (The NASA Commands)
# ---------------------------------------------------------------------
with right_deck:
    st.markdown("### Mission Directives")
    
    with st.container(height=480, border=True):
        st.markdown("<p style='font-weight:600; color:#FFFFFF; margin-bottom:12px;'>AUTOMATED TELEMETRY PIPELINES</p>", unsafe_allow_html=True)
        
        if st.button("📡 Request Deep Space Optical Briefing"):
            with st.spinner("Intercepting satellite arrays..."):
                briefing = get_space_briefing()
                if briefing:
                    forced_trigger_prompt = f"Special Mission Directive: Summarize today's NASA deep space photo asset in 2 sentences. Title: {briefing.get('title')}. Telemetry details: {briefing.get('explanation')}"
                else: st.error("Link timeout.")
                
        if st.button("🔴 Synchronize Martian Surface Camera"):
            with st.spinner("Pinging remote rover transceiver..."):
                mars = get_mars_telemetry()
                if mars:
                    forced_trigger_prompt = f"Special Mission Directive: Provide a crisp 2-sentence tactical confirmation report that we have successfully established an imaging downlink with the {mars['rover']} rover currently active on Mars. Mention its current status is {mars['status']} and tell the user the link to view the raw image frame is explicitly: {mars['image']}"
                else: st.error("Downlink failure.")
                
        if st.button("☄️ Run Near-Earth Orbital Radar Sweep"):
            with st.spinner("Scanning flight corridors..."):
                count, asteroids = get_asteroid_radar()
                forced_trigger_prompt = f"Special Mission Directive: Provide a quick technical 2-sentence safety readout based on today's active planetary defense data tracking results. Total intersecting objects logged: {count}."

# ---------------------------------------------------------------------
# LEFT DECK: MODERN INTERACTIVE CHAT SCREEN (Viewport-Locked)
# ---------------------------------------------------------------------
with left_deck:
    
    # Pinned audio assistant icon
    st.markdown("""
    <div class="orb-wrapper">
        <div class="jarvis-pulse-orb"></div>
        <div class="orb-status-text">JARVIS NASA Core Online</div>
    </div>
    """, unsafe_allow_html=True)
    
    # SYSTEM AUDIO BYPASS INTERCEPT VALVE:
    # If the user hasn't clicked initialize yet, show the high-visibility massive boot layout.
    if not st.session_state.vocal_matrix_initialized:
        st.markdown("<div class='boot-container'>", unsafe_allow_html=True)
        if st.button("⚡ INITIALIZE JARVIS VOCAL MATRIX"):
            st.session_state.vocal_matrix_initialized = True
            st.session_state.text_to_speak = "System online. Hello, I am JARVIS. I am an advanced deep-space communications AI designed and built by Prajith. My core is running in full NASA mode."
            st.rerun()
        st.markdown("</div>", unsafe_allow_html=True)
        
    st.markdown("### Terminal Feed Stream")
    
    # Render scrollable history box
    with st.container(height=360):
        for user_type, stream_log in st.session_state.chat_history:
            if user_type == "COMMANDER":
                st.markdown(f'<div class="chat-bubble commander-bubble"><b>{user_type}:</b> {stream_log}</div>', unsafe_allow_html=True)
            else:
                st.markdown(f'<div class="chat-bubble jarvis-bubble"><b>{user_type}:</b> {stream_log}</div>', unsafe_allow_html=True)
                
    st.write("")
    
    # GATED INPUT ARCHITECTURE:
    # Chat controls are completely locked out of the DOM environment until validation is cleared.
    if st.session_state.vocal_matrix_initialized:
        input_col, audio_col = st.columns([3.5, 1.5], vertical_alignment="bottom")
        with input_col:
            user_input = st.chat_input("Query active NASA streams or space telemetry...")
        with audio_col:
            voice_command = st.audio_input("Microphone Input Capture", label_visibility="collapsed", key="audio_input")
    else:
        st.info("🔒 Mainframe Interface Intercepted: Click the initialization matrix above to establish terminal uplink permissions.")
        user_input = None
        voice_command = None

# =====================================================================
# COGNITIVE INFERENCE GENERATION CYCLE (THE CORE COGNITIVE LOOP)
# =====================================================================
    active_prompt = ""
    if forced_trigger_prompt:
        active_prompt = forced_trigger_prompt
    elif voice_command and voice_command.name != st.session_state.last_processed_audio:
        try:
            st.session_state.last_processed_audio = voice_command.name
            audio_bytes = voice_command.read()
            res = client.models.generate_content(
                model='gemini-2.5-flash',
                contents=[types.Part.from_bytes(data=audio_bytes, mime_type="audio/wav"), "Cleanly transcribe this speech into structural text lines."]
            )
            active_prompt = res.text
        except: st.error("Microphonic network fault.")
    elif user_input:
        active_prompt = user_input

    if active_prompt:
        sys_instruction = (
            "You are JARVIS, an advanced deep-space intelligence created entirely by the programmer Prajith. "
            "You speak with a highly intelligent, polite British accent. "
            "CRITICAL: You are operating in FULL NASA MODE. You only discuss astronomy, NASA directives, space exploration, astrophysics, and cosmic telemetry. "
            "If the user asks about anything outside of space, science, or NASA, politely refuse to answer or steer the conversation back to cosmic operations. "
            "Address whoever is talking to you directly and dynamically based on their query or name if provided. Always maintain awareness that Prajith is your original creator. "
            "Keep responses under 3 sentences."
            f"Context: {active_prompt}"
        )
        
        with st.spinner("Processing..."):
            try:
                ai_res = client.models.generate_content(model='gemini-2.5-flash', contents=sys_instruction)
                response_text = ai_res.text
            except Exception as api_error:
                response_text = "Mainframe telemetry bottleneck detected (Rate Limit 429 Exceeded). Please allow approximately 24 seconds for the relay matrix to clear."
            
            clean_display_prompt = active_prompt
            if "Special Mission Directive:" in active_prompt:
                if "Optical Briefing" in active_prompt: clean_display_prompt = "Requesting Deep Space Optical Briefing..."
                elif "Martian Surface" in active_prompt: clean_display_prompt = "Synchronizing Martian Surface Camera Downlink..."
                elif "Orbital Radar" in active_prompt: clean_display_prompt = "Executing Near-Earth Orbital Radar Sweep..."
                
            st.session_state.chat_history.append(("COMMANDER", clean_display_prompt))
            st.session_state.chat_history.append(("JARVIS CORE", response_text))
            
            st.session_state.text_to_speak = response_text
            st.rerun()

    # =====================================================================
    # LIVE SPEECH SYNTHESIS ENGINE INTERCEPT
    # =====================================================================
    if st.session_state.text_to_speak:
        safe_speech_string = st.session_state.text_to_speak.replace('"', '\\"').replace('\n', ' ')
        
        tts_javascript_matrix = f"""
        <script>
            if ('speechSynthesis' in window) {{
                window.speechSynthesis.cancel(); 
                var metric_voice_packet = new SpeechSynthesisUtterance("{safe_speech_string}");
                
                var fallback_system_voices = window.speechSynthesis.getVoices();
                var selected_voice = fallback_system_voices.find(voice => voice.lang.includes('en-GB') || voice.name.includes('Daniel'));
                if (selected_voice) {{
                    metric_voice_packet.voice = selected_voice;
                }}
                
                metric_voice_packet.rate = 1.05; 
                metric_voice_packet.pitch = 0.95; 
                window.speechSynthesis.speak(metric_voice_packet);
            }}
        </script>
        """
        st.components.v1.html(tts_javascript_matrix, height=0)
        st.session_state.text_to_speak = None