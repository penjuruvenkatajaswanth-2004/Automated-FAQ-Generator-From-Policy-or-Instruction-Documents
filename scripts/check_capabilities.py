
import google.generativeai as genai

GOOGLE_API_KEY = "AIzaSyB18ABCdY04PKX1lH4f-y4wTlc9cejLOfE"
genai.configure(api_key=GOOGLE_API_KEY)

print("Checking model capabilities...")
with open("model_capabilities.txt", "w") as f:
    for m in genai.list_models():
        f.write(f"Model: {m.name}\n")
        f.write(f"Methods: {m.supported_generation_methods}\n")
        f.write("-" * 20 + "\n")
        
print("Done. Check model_capabilities.txt")
