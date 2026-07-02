# J.A.R.V.I.S. // NASA CORE

### Joint Artificial Reconnaissance & Vigilance Intelligence System

<!-- Add a screenshot: docs/screenshot.png -->
<!-- ![JARVIS Mission Control](docs/screenshot.png) -->

A real-time NASA mission intelligence dashboard powered by six live NASA APIs and Google Gemini AI. Named after Iron Man's AI assistant, JARVIS monitors near-Earth asteroid threats, ISS crew status, Mars surface conditions, solar weather, and Earth events — all in one unified command interface.

## Live Demo

🚀 **[stardance-jarvis.streamlit.app](https://stardance-jarvis.streamlit.app)**

## Features

- **Planetary Defense Radar** — Real-time near-Earth object tracking from NASA NeoWs API, with hazard classification and 7-day trend context
- **ISS Mission Control** — Live crew count and station position from Open Notify API, rendered on a dark-matter world map
- **Mars Surface Feed** — Latest Curiosity rover imagery from NASA Mars Rover Photos API
- **Solar Weather Monitor** — DONKI space weather alerts with NOMINAL / ELEVATED / HIGH threat levels
- **Earth Events Tracker** — Active natural events (wildfires, storms, volcanoes) from NASA EONET API
- **AI Mission Briefing** — Google Gemini powered natural-language interface for mission queries
- **Voice Input & Speech Output** — Speak your queries directly to JARVIS; it answers out loud in a British accent

## NASA APIs Used

- NASA NeoWs (Near Earth Object Web Service)
- NASA Astronomy Picture of the Day (APOD)
- NASA Mars Rover Photos API
- NASA DONKI (Space Weather Database)
- NASA EONET (Earth Observatory Natural Event Tracker)
- NASA EPIC (Earth Polychromatic Imaging Camera)
- Open Notify ISS API

## Setup & Installation

### Prerequisites

- Python 3.9+
- NASA API key — free at [api.nasa.gov](https://api.nasa.gov)
- Google Gemini API key — free at [aistudio.google.com](https://aistudio.google.com)

### Installation

```bash
git clone https://github.com/prajith-vishnu/stardance-jarvis
cd stardance-jarvis
pip install -r requirements.txt
```

### Configuration

API keys are **never** hardcoded — the app reads them from Streamlit secrets (cloud) or a local `.env` file. Copy `.env.example` to `.env` and fill in your keys:

```
NASA_API_KEY=your_nasa_api_key_here
GEMINI_API_KEY=your_gemini_api_key_here
```

For Streamlit Cloud deployment, add the same two keys under **App settings → Secrets** instead:

```toml
NASA_API_KEY = "your_nasa_api_key_here"
GEMINI_API_KEY = "your_gemini_api_key_here"
```

### Run

```bash
streamlit run app.py
```

There is also a terminal-only version with macOS voice output:

```bash
python jarvis.py
```

## Tech Stack

- Python 3.9+
- Streamlit
- Google Gemini AI (`google-genai`)
- NASA Public APIs
- Custom CSS with Iron Man HUD aesthetic (arc reactor, starfield, mission strip)

## Built For

Hack Club 2026

## AI Usage

Claude (Anthropic) was used as a coding assistant to implement this project. All creative decisions — the JARVIS concept, NASA API selection, Iron Man HUD aesthetic, and feature design — were conceived and directed by Prajith Vishnu Rajesh Kumar.

## License

MIT

## Creator

**Prajith Vishnu Rajesh Kumar**
Ray Braswell High School, Aubrey, Texas
