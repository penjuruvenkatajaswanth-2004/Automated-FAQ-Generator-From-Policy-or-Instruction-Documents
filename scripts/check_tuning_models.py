
import google.generativeai as genai

GOOGLE_API_KEY = "AIzaSyB18ABCdY04PKX1lH4f-y4wTlc9cejLOfE"
genai.configure(api_key=GOOGLE_API_KEY)

print("Models supporting tuning:")
with open("tuning_models.txt", "w") as f:
    for m in genai.list_models():
        if 'createTunedModel' in m.supported_generation_methods:
            print(f"- {m.name}")
            f.write(f"{m.name}\n")
