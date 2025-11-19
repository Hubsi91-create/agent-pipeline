import os
import google.generativeai as genai
from dotenv import load_dotenv
import traceback

load_dotenv("backend/.env")

api_key = os.getenv("GEMINI_API_KEY")
if not api_key:
    print("No API Key found")
    exit(1)

print(f"Key length: {len(api_key)}")
print(f"Key start: {api_key[:4]}")
print(f"Key end: {api_key[-4:]}")

genai.configure(api_key=api_key)

print("\n--- Testing gemini-1.5-pro ---")
try:
    model = genai.GenerativeModel('gemini-1.5-pro')
    response = model.generate_content("Hello")
    print("Success!")
except Exception:
    traceback.print_exc()

print("\n--- Testing gemini-3.0-pro ---")
try:
    model = genai.GenerativeModel('gemini-3.0-pro')
    response = model.generate_content("Hello")
    print("Success!")
except Exception:
    traceback.print_exc()
