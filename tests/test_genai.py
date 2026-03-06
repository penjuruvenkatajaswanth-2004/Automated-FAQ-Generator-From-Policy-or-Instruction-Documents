import google.generativeai as genai
import sys

# Force UTF-8 for output to avoid encoding errors in terminals
sys.stdout.reconfigure(encoding='utf-8')

GOOGLE_API_KEY = "AIzaSyB18ABCdY04PKX1lH4f-y4wTlc9cejLOfE"
genai.configure(api_key=GOOGLE_API_KEY)

candidates = [
    'gemini-2.0-flash',
    'gemini-1.5-flash',
    'gemini-pro'
]

print("STARTING TEST...")
for model_name in candidates:
    try:
        model = genai.GenerativeModel(model_name)
        response = model.generate_content("Hi")
        print(f"!!! SUCCESS_MODEL: {model_name} !!!")
        break
    except Exception as e:
        print(f"FAILED: {model_name} ({str(e)[:50]}...)")
