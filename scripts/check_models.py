import google.generativeai as genai
import os

# Use the key from app.py
GOOGLE_API_KEY = "AIzaSyB18ABCdY04PKX1lH4f-y4wTlc9cejLOfE"
genai.configure(api_key=GOOGLE_API_KEY)

print("Listing available models for this API key...")
try:
    with open("models.txt", "w") as f:
        for m in genai.list_models():
            if 'generateContent' in m.supported_generation_methods:
                print(f"- {m.name}")
                f.write(f"{m.name}\n")
    print("Models written to models.txt")
except Exception as e:
    print(f"Error listing models: {e}")
