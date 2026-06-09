import os
import sys
import subprocess
import requests
from google import genai

def fetch_nasa_briefing():
    """Fetches today's space data from NASA."""
    nasa_url = "https://api.nasa.gov/planetary/apod?api_key=DEMO_KEY"
    try:
        response = requests.get(nasa_url)
        if response.status_code == 200:
            data = response.json()
            return data.get("title"), data.get("explanation")
        else:
            return None, f"Mainframe error: {response.status_code}"
    except Exception as e:
        return None, f"Connection error: {e}"

def jarvis_speak(text):
    """Uses the native macOS 'say' command to make JARVIS talk."""
    # Remove markdown bolding asterisks so JARVIS doesn't try to pronounce them
    clean_text = text.replace("*", "")
    try:
        # This tells your Mac to use its built-in text-to-speech engine
        subprocess.Popen(['say', clean_text])
    except Exception as e:
        print(f"Text-to-speech subsystem failure: {e}")

def ask_jarvis_ai(prompt_context):
    """Passes context to Gemini to respond in JARVIS's distinct personality."""
    try:
        client = genai.Client()
        system_prompt = f"""
        You are JARVIS, Tony Stark's advanced AI assistant from Iron Man. 
        You are sophisticated, brilliant, British, and deeply polite. You must always address the user as 'sir'.
        Keep your responses clean, short, and intelligent. 
        CRITICAL: Since your text will be read out loud, keep your answers under 3 sentences maximum so you do not drag on.
        
        Task context:
        {prompt_context}
        """
        response = client.models.generate_content(
            model='gemini-2.5-flash',
            contents=system_prompt,
        )
        return response.text
    except Exception as e:
        return f"Apologies, sir. My cognitive subroutines encountered an error: {e}"

def start_jarvis():
    if not os.environ.get("GEMINI_API_KEY"):
        print("ALERT: JARVIS cannot find the GEMINI_API_KEY environment variable.")
        return

    print("JARVIS: Audio matrices active. Vocal synthesizers initialized.")
    jarvis_speak("Systems online, sir. Vocal synthesizers initialized.")
    print("JARVIS: Type 'briefing', 'shutdown', or speak with me.\n")
    
    while True:
        user_input = input("YOU: ").strip()
        if not user_input:
            continue
            
        if user_input.lower() == "shutdown":
            print("\nJARVIS: Powering down thrusters. Safe travels, sir.")
            jarvis_speak("Powering down thrusters. Safe travels, sir.")
            sys.exit()
            
        elif user_input.lower() == "briefing":
            print("\nJARVIS: Accessing NASA archives and processing telemetry...")
            jarvis_speak("Accessing NASA archives and processing telemetry, please standby.")
            title, explanation = fetch_nasa_briefing()
            
            if title:
                context = f"Summarize this NASA data in 2 concise sentences as JARVIS. Title: {title}. Description: {explanation}"
                jarvis_response = ask_jarvis_ai(context)
                
                print(f"\n==================================================")
                print(f"JARVIS DATA UPLINK: {title.upper()}")
                print(f"==================================================")
                print(f"{jarvis_response}")
                print(f"==================================================\n")
                jarvis_speak(jarvis_response)
            else:
                print(f"\n[JARVIS]: Alert. Unable to fetch telemetry.\n")
                
        else:
            print("\nJARVIS: Processing...")
            context = f"The user just said: '{user_input}'. Respond to them naturally as their AI assistant in under 3 sentences."
            jarvis_response = ask_jarvis_ai(context)
            print(f"\nJARVIS: {jarvis_response}\n")
            jarvis_speak(jarvis_response)

if __name__ == "__main__":
    start_jarvis()