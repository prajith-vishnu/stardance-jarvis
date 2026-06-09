import os
from google import genai

# This line checks if your Mac successfully hid the key where Google expects it
api_key = os.environ.get("GEMINI_API_KEY")

if not api_key:
    print("ALERT: JARVIS cannot find the GEMINI_API_KEY. Check Step 1 again, sir.")
else:
    print("JARVIS: AI Core located. Initializing handshake...")
    
    # Fire up the Google GenAI client
    client = genai.Client()
    
    # We use 'gemini-2.5-flash' because it's insanely fast
    response = client.models.generate_content(
        model='gemini-2.5-flash',
        contents='Give me a 1-sentence greeting as JARVIS from Iron Man welcoming me to my cybernetic lab.',
    )
    
    print(f"\n[JARVIS]: {response.text}")