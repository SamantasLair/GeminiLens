import os
import google.generativeai as genai
from dotenv import load_dotenv

# Load env directly to be sure
load_dotenv()
api_key = os.getenv("GEMINI_API_KEY")

print(f"API Key loaded: {api_key[:5]}...{api_key[-5:] if api_key else 'None'}")

if not api_key:
    print("ERROR: No API Key found.")
    exit()

try:
    genai.configure(api_key=api_key)
    
    # Try listing models first to see what's available
    print("Listing available models...")
    for m in genai.list_models():
        if 'generateContent' in m.supported_generation_methods:
            print(f" - {m.name}")

    print("\nAttempting to generate content with 'gemini-1.5-flash'...")
    model = genai.GenerativeModel('gemini-1.5-flash')
    response = model.generate_content("Hello, do you work?")
    print(f"SUCCESS! Response: {response.text}")

except Exception as e:
    print(f"\nCRITICAL ERROR: {e}")
    import traceback
    traceback.print_exc()
