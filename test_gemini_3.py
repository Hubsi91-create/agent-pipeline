import os
import google.generativeai as genai
from dotenv import load_dotenv
import traceback

load_dotenv("backend/.env")
api_key = os.getenv("GEMINI_API_KEY")
genai.configure(api_key=api_key)

print("Testing gemini-3-pro-preview...")
try:
    model = genai.GenerativeModel('gemini-3-pro-preview')
    response = model.generate_content("Hello, are you Gemini 3.0?")
    print(f"✅ Success! Response: {response.text}")
except Exception:
    print("❌ Failed:")
    traceback.print_exc()
