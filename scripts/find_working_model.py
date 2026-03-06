import google.generativeai as genai
import time
import os

# Use the key from app.py
GOOGLE_API_KEY = "AIzaSyB18ABCdY04PKX1lH4f-y4wTlc9cejLOfE"
genai.configure(api_key=GOOGLE_API_KEY)

print("--- Testing Models for Availability ---")

def test_model(model_name):
    print(f"Testing {model_name}...", end=" ")
    try:
        model = genai.GenerativeModel(model_name)
        response = model.generate_content("Hello, this is a test.")
        if response.text:
            print("SUCCESS! ✅")
            return True
    except Exception as e:
        if "429" in str(e) or "Quota" in str(e):
             print(f"FAILED (Quota Exceeded) ❌")
        elif "404" in str(e) or "not found" in str(e):
             print(f"FAILED (Not Found) ❌")
        else:
             print(f"FAILED ({str(e)[:50]}...) ❌")
    return False

# List of potential models to try (prioritizing stable ones)
candidates = [
    "gemini-1.5-flash",
    "gemini-1.5-flash-001",
    "gemini-1.5-flash-002",
    "gemini-1.5-pro",
    "gemini-1.5-pro-001",
    "gemini-1.0-pro",
    "gemini-pro",
    "gemini-2.0-flash-exp", # Fallback
]

working_model = None

# 1. First try the candidates list
for m in candidates:
    if test_model(m):
        working_model = m
        break

# 2. If none work, try everything in list_models
if not working_model:
    print("\nCandidates failed. Checking ALL available models...")
    for m in genai.list_models():
        if 'generateContent' in m.supported_generation_methods:
            name = m.name.replace("models/", "")
            if name not in candidates:
                if test_model(name):
                    working_model = name
                    break

if working_model:
    print(f"\n RECOMMENDED MODEL: {working_model}")
    with open("working_model.txt", "w") as f:
        f.write(working_model)
else:
    print("\n NO WORKING MODEL FOUND.")
