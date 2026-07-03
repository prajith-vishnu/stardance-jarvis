# JARVIS — NASA Mission Control

My space dashboard project. It pulls live data from NASA's public APIs and lets you talk to JARVIS (yes, like Iron Man) about what's actually happening in space right now.

**Live demo:** [stardance-jarvis.vercel.app](https://stardance-jarvis.vercel.app)

## What it does

- Tracks asteroids passing Earth today and flags the dangerous ones
- Shows how many people are in space right now
- Live ISS position on a map
- Solar flare monitor (past 7 days)
- NASA's astronomy picture of the day + latest Mars rover photo
- Ask JARVIS anything about space — you can talk to it with your mic and it talks back in a British accent

## How it works

The page itself is just HTML/CSS/JS, no framework. Two small Python functions run on Vercel:

- `api/feeds.py` — grabs data from the NASA APIs so my key never touches the browser
- `api/chat.py` — sends your question to Gemini along with the live telemetry

NASA APIs used: NeoWs, APOD, Mars Rover Photos, DONKI, EONET, EPIC, plus Open Notify for the ISS.

## Run it yourself

1. Get free keys at [api.nasa.gov](https://api.nasa.gov) and [aistudio.google.com](https://aistudio.google.com)
2. Copy `.env.example` to `.env` and paste your keys in
3. `python3 dev_server.py` and open http://localhost:8899

No pip installs needed. To deploy your own: import the repo on [vercel.com](https://vercel.com) and add `NASA_API_KEY` and `GEMINI_API_KEY` under Project Settings → Environment Variables.

The original Streamlit version lives in `legacy/` if you're curious.

## AI note

I used Claude as a coding assistant while building this. The concept, feature choices, and the Iron Man HUD design direction are mine.

## Built for

Hack Club 2026

---

Prajith Vishnu Rajesh Kumar · Ray Braswell High School, Aubrey, TX · MIT License
