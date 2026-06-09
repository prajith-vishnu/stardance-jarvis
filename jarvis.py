import requests
import sys

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

def start_jarvis():
    print("JARVIS: Systems online. Core heuristics initialized.")
    print("JARVIS: Type 'briefing' for space data, or 'shutdown' to exit.\n")
    
    while True:
        # This keeps the program running and waits for your input
        user_input = input("YOU: ").strip().lower()
        
        if user_input == "shutdown":
            print("\nJARVIS: Powering down thrusters. Goodbye, sir.")
            sys.exit()
            
        elif user_input == "briefing":
            print("\nJARVIS: Accessing NASA archives...")
            title, explanation = fetch_nasa_briefing()
            
            if title:
                print(f"\n[JARVIS]: Today's briefing is on '{title}'.")
                print(f"\"{explanation}\"\n")
            else:
                print(f"\n[JARVIS]: Alert. {explanation}\n")
                
        else:
            print(f"\n[JARVIS]: I am programmed for orbital data, sir. Command '{user_input}' not recognized. Try 'briefing' or 'shutdown'.\n")

if __name__ == "__main__":
    start_jarvis()