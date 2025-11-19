import os
import google.generativeai as genai
from dotenv import load_dotenv

load_dotenv()

api_key = os.getenv("GEMINI_API_KEY")
print(f"API Key found: {'Yes' if api_key else 'No'}")

if api_key:
    try:
        genai.configure(api_key=api_key)
        print("Listing available models...")
        for m in genai.list_models():
            if 'generateContent' in m.supported_generation_methods:
                print(f"- {m.name}")
        
        print("\nTesting gemini-3-pro-preview...")
        model = genai.GenerativeModel('gemini-3-pro-preview')
        response = model.generate_content("Hello, are you working?")
        print(f"Response: {response.text}")
        
    except Exception as e:
        print(f"Error: {e}")
