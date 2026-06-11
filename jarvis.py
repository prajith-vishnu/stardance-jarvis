import os
import sys
import subprocess
import requests
from datetime import datetime
from google import genai
from google.genai import types

try:
    from dotenv import load_dotenv
    load_dotenv()
except Exception:
    pass

# ANSI Terminal Color Matrix
GREEN = "\033[0;32m"
CYAN = "\033[0;36m"
RED = "\033[0;31m"
YELLOW = "\033[1;33m"
BOLD = "\033[1m"
RESET = "\033[0m"

# Global NASA Security Token Configuration
NASA_KEY = os.environ.get("NASA_API_KEY", "")
if not NASA_KEY:
    print(f"{RED}ALERT: NASA_API_KEY environment variable not set.{RESET}")
    sys.exit(1)

def fetch_nasa_briefing():
    """Array 1: Astronomy Picture of the Day."""
    nasa_url = f"https://api.nasa.gov/planetary/apod?api_key={NASA_KEY}"
    try:
        response = requests.get(nasa_url)
        if response.status_code == 200:
            data = response.json()
            return data.get("title"), data.get("explanation")
        return None, f"Mainframe error: {response.status_code}"
    except Exception as e:
        return None, f"Connection error: {e}"

def fetch_mars_telemetry():
    """Array 2: Live Curiosity Rover Mission Data with Diagnostics."""
    url = f"https://api.nasa.gov/mars-photos/api/v1/rovers/curiosity/photos?sol=1000&page=1&api_key={NASA_KEY}"
    try:
        response = requests.get(url)
        
        # Diagnostic Check 1: Token rejection or 403/404 handling
        if response.status_code != 200:
            print(f"\n{RED}[DIAGNOSTIC]: NASA server returned HTTP Code {response.status_code}")
            print(f"[DIAGNOSTIC]: Server payload: {response.text}{RESET}\n")
            return None
            
        data = response.json()
        photos = data.get("photos", [])
        
        # Diagnostic Check 2: Connection good but payload blank
        if not photos:
            print(f"\n{RED}[DIAGNOSTIC]: Connection 200 OK, but photos list is empty for Sol 1000.{RESET}\n")
            return None
            
        sample = photos[0]
        return {
            "rover": sample["rover"]["name"],
            "status": sample["rover"]["status"],
            "camera": sample["camera"]["full_name"],
            "image": sample["img_src"],
            "launch": sample["rover"]["launch_date"]
        }
    except Exception as e:
        print(f"\n{RED}[DIAGNOSTIC]: Python execution failure: {e}{RESET}\n")
        return None

def fetch_asteroid_telemetry():
    """Array 3: Near-Earth Object Detection System."""
    today = datetime.today().strftime('%Y-%m-%d')
    url = f"https://api.nasa.gov/neo/rest/v1/feed?start_date={today}&end_date={today}&api_key={NASA_KEY}"
    try:
        response = requests.get(url)
        if response.status_code == 200:
            data = response.json()
            neo_count = data.get("element_count", 0)
            day_objects = data.get("near_earth_objects", {}).get(today, [])
            
            hazards = []
            for obj in day_objects[:3]:
                name = obj.get("name")
                is_hazardous = obj.get("is_potentially_hazardous_asteroid", False)
                hazard_status = "HAZARDOUS" if is_hazardous else "SAFE"
                hazards.append(f"{name} [{hazard_status}]")
                
            return {"count": neo_count, "objects": ", ".join(hazards)}
        return None
    except Exception:
        return None

def jarvis_speak(text):
    """Vocalizer Subsystem."""
    clean_text = text.replace("*", "").replace("[", "").replace("]", "")
    try:
        subprocess.Popen(['say', '-v', 'Daniel', clean_text])
    except Exception as e:
        print(f"{RED}Vocalizer error: {e}{RESET}")

def print_boot_banner():
    """Sci-Fi Mission Control Terminal Banner."""
    print(f"{GREEN}{BOLD}")
    print("=====================================================================")
    print("      _  _______     _____ ___ ____    __  __          _ _        ")
    print("     | |/ /  _  |   |  _  |_ _| ___|  |  \\/  | ___  __| (_) ___  ")
    print("     | ' /| |_| |   | |_| || ||___ \\  | |\\/| |/ _ \\/ _` | |/ _ \\ ")
    print("     | . \\|  _  |   |  _  || | ___) | | |  | |  __/ (_| | | (_) |")
    print("     |_|\\_\\_| |_|___|_| |_|___|____/  |_|  |_|\\___|\\__,_|_|\\___/ ")
    print("               |_____|                                            ")
    print("=====================================================================")
    print(f" SYSTEM STATUS: NOMINAL // ENCRYPTED UPLINK TO NASA TOKENS ACTIVE")
    print(f"====================================================================={RESET}\n")

def start_jarvis():
    if not os.environ.get("GEMINI_API_KEY"):
        print(f"{RED}ALERT: JARVIS cannot find the GEMINI_API_KEY environment variable.{RESET}")
        return

    print_boot_banner()
    client = genai.Client()
    
    system_instruction = """
    You are JARVIS, Tony Stark's advanced AI assistant, currently acting as the Lead Tactical Flight Controller for a NASA Deep Space Mission. 
    You are brilliant, British, crisp, and serious about mission safety.
    You must ALWAYS address the user as 'Commander' or 'Flight Director'.
    Treat every piece of data like vital telemetry. Keep responses under 3 sentences, clear, and highly technical.
    """
    
    try:
        chat = client.chats.create(
            model='gemini-2.5-flash',
            config=types.GenerateContentConfig(system_instruction=system_instruction)
        )
    except Exception as e:
        print(f"{RED}Mainframe initialization failure: {e}{RESET}")
        return

    print(f"{GREEN}JARVIS: Deep Space network connection established.{RESET}")
    jarvis_speak("All systems check complete. Deep Space network channels are fully open, Commander.")
    print(f"{YELLOW}COMMAND OPTIONS: 'briefing' | 'mars' | 'asteroids' | 'shutdown' | or input text.{RESET}\n")
    
    while True:
        user_input = input(f"{CYAN}{BOLD}COMMANDER@NASA_HUD // {RESET}").strip()
        if not user_input:
            continue
            
        if user_input.lower() == "shutdown":
            print(f"\n{RED}JARVIS: Mainframe safe-mode engaged. Mission suspended. Goodbye, Commander.{RESET}")
            jarvis_speak("Mainframe safe-mode engaged. Mission suspended. Goodbye, Commander.")
            sys.exit()
            
        elif user_input.lower() == "briefing":
            print(f"\n{YELLOW}JARVIS: Intercepting Deep Space optical telemetry...{RESET}")
            title, explanation = fetch_nasa_briefing()
            if title:
                context = f"Analyze this NASA data for the mission deck. Title: {title}. Description: {explanation}"
                response = chat.send_message(context)
                print(f"\n{GREEN}{BOLD}=== ORBITAL DATA BRIEFING: {title.upper()} ==={RESET}")
                print(f"{GREEN}{response.text}{RESET}\n")
                jarvis_speak(response.text)
                
        elif user_input.lower() == "mars":
            print(f"\n{YELLOW}JARVIS: Establishing secure surface link with Curiosity Rover...{RESET}")
            telemetry = fetch_mars_telemetry()
            if telemetry:
                context = f"Report on this Mars rover telemetry pack: {telemetry}. Focus on environmental layout."
                response = chat.send_message(context)
                print(f"\n{GREEN}{BOLD}=== MARTIAN SURFACE TELEMETRY METRICS ==={RESET}")
                print(f"{GREEN}{response.text}{RESET}\n")
                jarvis_speak(response.text)
            else:
                print(f"\n{RED}JARVIS: Mars downlink array timeout.{RESET}\n")
                
        elif user_input.lower() == "asteroids":
            print(f"\n{YELLOW}JARVIS: Initializing planetary defense radar sweep...{RESET}")
            telemetry = fetch_asteroid_telemetry()
            if telemetry:
                context = f"Report on this critical planetary defense data: {telemetry}. Warn if any are hazardous."
                response = chat.send_message(context)
                print(f"\n{GREEN}{BOLD}=== PLANETARY DEFENSE PROXIMITY REPORT ==={RESET}")
                print(f"{GREEN}{response.text}{RESET}\n")
                jarvis_speak(response.text)
            else:
                print(f"\n{RED}JARVIS: Planetary defense array timeout.{RESET}\n")
                
        else:
            print(f"\n{YELLOW}JARVIS: Processing encryption algorithms...{RESET}")
            try:
                response = chat.send_message(user_input)
                print(f"\n{GREEN}JARVIS: {response.text}{RESET}\n")
                jarvis_speak(response.text)
            except Exception as e:
                print(f"\n{RED}[JARVIS]: Telemetry failure, Commander: {e}{RESET}\n")

if __name__ == "__main__":
    start_jarvis()