import os
import google.generativeai as genai
from dotenv import load_dotenv
import traceback

load_dotenv("backend/.env")

api_key = os.getenv("GEMINI_API_KEY")
if not api_key:
    print("No API Key found")
    exit(1)

genai.configure(api_key=api_key)

print(f"Testing gemini-1.5-pro with key: {api_key[:5]}...")

try:
    model = genai.GenerativeModel('gemini-1.5-pro')
    response = model.generate_content("List 3 subgenres of Electronic music.")
    print(f"Success! Response:\n{response.text}")
except Exception:
    print("Failed:")
    traceback.print_exc()
