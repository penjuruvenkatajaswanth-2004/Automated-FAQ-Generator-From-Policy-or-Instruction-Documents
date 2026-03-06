
import google.generativeai as genai
import pandas as pd
import json
import time
import os

# --- CONFIGURATION ---
GOOGLE_API_KEY = "AIzaSyB18ABCdY04PKX1lH4f-y4wTlc9cejLOfE"
genai.configure(api_key=GOOGLE_API_KEY)
DATASET_PATH = 'dataset.xlsx'
TUNED_MODEL_ID = "faq-tuned-model-" + str(int(time.time())) # Unique ID

def main():
    print(f"--- 1. Loading Dataset from {DATASET_PATH} ---")
    try:
        df = pd.read_excel(DATASET_PATH)
        print("Columns found:", df.columns.tolist())
        
        # Auto-detect columns
        question_col = next((c for c in df.columns if 'quest' in c.lower() or 'input' in c.lower()), None)
        answer_col = next((c for c in df.columns if 'answ' in c.lower() or 'output' in c.lower()), None)
        
        if not question_col or not answer_col:
            raise ValueError(f"Could not automatically accept QUESTION and ANSWER columns. Found: {df.columns.tolist()}")
            
        print(f"Using '{question_col}' as Input and '{answer_col}' as Output.")
        
        training_data = []
        for index, row in df.iterrows():
            training_data.append({
                "text_input": str(row[question_col]),
                "output": str(row[answer_col])
            })
            
        print(f"Loaded {len(training_data)} examples.")
        
    except Exception as e:
        print(f"Error loading dataset: {e}")
        return

    print(f"--- 2. Starting Fine-Tuning Job (ID: {TUNED_MODEL_ID}) ---")
    try:
        operation = genai.create_tuned_model(
            # Using flash suitable for tuning
            source_model='models/gemini-1.0-pro-001',
            training_data=training_data,
            id=TUNED_MODEL_ID,
            epoch_count=5,
            batch_size=4,
            learning_rate=0.001,
        )
        
        print(f"Job Initialized. Name: {operation.name}")
        
        with open("tuned_model_info.txt", "w") as f:
            f.write(operation.name)
            
        print("Tuning job submitted! It may take a few minutes to complete.")
        print("You can verify status using: python check_tuning_status.py")
        print(f"Model Name successfully saved to tuned_model_info.txt: {operation.name}")

    except Exception as e:
        import traceback
        traceback.print_exc()
        print(f"Error creating tuning job: {e}")
        with open("tuning_error.txt", "w") as f:
            f.write(str(e))
            f.write("\n")
            f.write(traceback.format_exc())

if __name__ == "__main__":
    main()
