import google.generativeai as genai
import os

# Use the key from app.py
GOOGLE_API_KEY = "AIzaSyB18ABCdY04PKX1lH4f-y4wTlc9cejLOfE"
genai.configure(api_key=GOOGLE_API_KEY)

print("Listing available models...")
with open("available_models.txt", "w") as f:
    try:
        for m in genai.list_models():
            if 'generateContent' in m.supported_generation_methods:
                f.write(f"{m.name}\n")
                print(f"Found: {m.name}")
    except Exception as e:
        f.write(f"Error: {e}\n")
        print(f"Error: {e}")
