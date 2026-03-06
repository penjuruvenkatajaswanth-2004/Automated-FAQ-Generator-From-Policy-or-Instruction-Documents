import warnings
# Suppress warnings from google.generativeai BEFORE importing it
warnings.filterwarnings("ignore", category=FutureWarning)
warnings.filterwarnings("ignore", category=UserWarning)

import os
import uuid
import qrcode
from flask import Flask, render_template, request, redirect, url_for, jsonify, send_from_directory
from werkzeug.utils import secure_filename
import PyPDF2
from docx import Document
from textblob import TextBlob
import random
import socket
import google.generativeai as genai
import time
import pandas as pd

# Initialize Flask App
app = Flask(__name__)
app.config['UPLOAD_FOLDER'] = 'static/uploads'
app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024  # 16MB max limit

# Ensure upload directory exists
os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)

# In-memory storage
# Structure: { 'file_id': { 'summary': '...', 'faqs': [...], 'chat_history': [], 'language': 'English', 'scan_status': 'pending' } }
data_store = {}

# --- CONFIGURATION ---
GOOGLE_API_KEY = "AIzaSyB18ABCdY04PKX1lH4f-y4wTlc9cejLOfE" 

if GOOGLE_API_KEY != "PASTE_YOUR_GOOGLE_API_KEY_HERE":
    genai.configure(api_key=GOOGLE_API_KEY)

# --- LOAD KNOWLEDGE BASE (RAG) ---
KNOWLEDGE_BASE_TEXT = ""
try:
    dataset_path = 'dataset.xlsx'
    if os.path.exists(dataset_path):
        print(f"Loading Knowledge Base from {dataset_path}...")
        df = pd.read_excel(dataset_path)
        
        # Auto-detect columns (simple first pass)
        q_col = next((c for c in df.columns if 'quest' in c.lower() or 'input' in c.lower()), df.columns[0])
        a_col = next((c for c in df.columns if 'answ' in c.lower() or 'output' in c.lower()), df.columns[1])
        
        # Create a text representation
        kb_pairs = []
        for _, row in df.iterrows():
            kb_pairs.append(f"Q: {row[q_col]}\nA: {row[a_col]}")
            
        KNOWLEDGE_BASE_TEXT = "\n\n".join(kb_pairs)
        print(f"Knowledge Base Loaded. {len(kb_pairs)} Q&A pairs.")
    else:
        print("Warning: dataset.xlsx not found. AI will use generic knowledge.")
except Exception as e:
    print(f"Error loading Knowledge Base: {e}")

def extract_text(filepath):
    """Extract text from PDF, DOCX, or TXT."""
    ext = filepath.rsplit('.', 1)[1].lower()
    text = ""
    error = None
    try:
        if ext == 'pdf':
            with open(filepath, 'rb') as f:
                reader = PyPDF2.PdfReader(f)
                if len(reader.pages) == 0:
                    return None, "PDF has no pages."
                for page in reader.pages:
                    page_text = page.extract_text()
                    if page_text:
                        text += page_text
        elif ext == 'docx':
            doc = Document(filepath)
            for para in doc.paragraphs:
                text += para.text + "\n"
        elif ext == 'txt':
            with open(filepath, 'r', encoding='utf-8') as f:
                text = f.read()
        else:
            return None, "Unsupported file format."
    except Exception as e:
        print(f"Error extracting text: {e}")
        return None, f"Error reading file: {str(e)}"
    
    text = text.strip()
    if not text:
         return None, "No text found in file. It might be a scanned image or empty."
         
    return text, None

def generate_ai_content(text, language="English"):
    """
    Generate Summary and FAQs using Google Gemini.
    """
    # Fallback/Mock Data
    summary = f"Summary (Mock): output in {language}."
    faqs = [{"question": f"Mock Q{i}", "answer": f"Answer in {language}"} for i in range(1, 6)]
    
    if GOOGLE_API_KEY == "PASTE_YOUR_GOOGLE_API_KEY_HERE":
        print(" Using MOCK mode (No key set)")
        return summary, faqs

    print(f"--- Connecting to Gemini (Lang: {language}) with Key ending in ...{GOOGLE_API_KEY[-4:]} ---")
    try:
        # User explicitly requested preserving this logic
        print("--- Using Model: gemini-flash-latest ---")
        model = genai.GenerativeModel('gemini-flash-latest')
        
        # Call 1: Summary (Text Mode - Low Failure Rate)
        print("-> Generating Summary...")
        prompt_summary = f"""
        Read the document text below and write a Detailed Summary (approx 300 words) in {language}.
        Structure it clearly with paragraphs. Do NOT use JSON. Just plain text.
        
        Text: {text[:8000]}
        """
        response_summary = retry_gemini_call(lambda: model.generate_content(prompt_summary))
        summary_text = response_summary.text.strip()
        
        # Call 2: FAQs (JSON Mode - Isolated for Safety)
        print("-> Generating FAQs...")
        prompt_faqs = f"""
        Read the document text below and generate 10 Frequently Asked Questions (FAQs) in {language}.
        Return ONLY valid JSON in this exact format:
        [
            {{ "question": "Question 1?", "answer": "Answer 1..." }},
            {{ "question": "Question 2?", "answer": "Answer 2..." }}
        ]
        
        Text: {text[:8000]}
        """
        response_faqs = retry_gemini_call(lambda: model.generate_content(prompt_faqs))
        faq_text = response_faqs.text.strip()
        
        # Clean JSON markdown
        if "```json" in faq_text:
            faq_text = faq_text.replace("```json", "").replace("```", "")
        if "```" in faq_text:
            faq_text = faq_text.replace("```", "")
            
        import json
        try:
            faqs_data = json.loads(faq_text)
        except:
             # Fallback if JSON fails (Small models struggle with JSON)
             print("JSON Parsing Failed for FAQs. Using Raw Text fallback.")
             faqs_data = [{"question": "Error parsing FAQs", "answer": "The AI provided the answers but in an invalid format. Please try again."}]

        print("--- Gemini Success! ---")
        return summary_text, faqs_data
        
    except Exception as e:
        print(f"!!! GEMINI ERROR: {e} !!!")
        error_summary = f"AI Generation Failed. Error: {str(e)}. Please check the terminal."
        return error_summary, faqs

def retry_gemini_call(call_func, max_retries=5, delay=10):
    """
    Wrapper to retry Gemini API calls on 429 (Quota Exceeded) or 503 (Overloaded) errors.
    """
    for attempt in range(max_retries):
        try:
            return call_func()
        except Exception as e:
            error_str = str(e)
            if "429" in error_str or "503" in error_str or "Quota exceeded" in error_str:
                if attempt < max_retries - 1:
                    wait_time = delay * (2 ** attempt) # Exponential backoff: 10, 20, 40, 80, 160
                    print(f"!!! API Limitation (429/503). Retrying in {wait_time} seconds... (Attempt {attempt+1}/{max_retries})")
                    time.sleep(wait_time)
                    continue
            raise e # Reraise if it's another error or retries exhausted

def generate_ai_content_from_file(filepath, language="English"):
    """
    Upload file to Gemini and generate content directly (for scanned PDFs/Images).
    """
    summary = f"Summary (Mock - Scanned): output in {language}."
    faqs = [{"question": f"Mock Q{i}", "answer": f"Answer in {language}"} for i in range(1, 6)]
    
    if GOOGLE_API_KEY == "PASTE_YOUR_GOOGLE_API_KEY_HERE":
        print(" Using MOCK mode (No key set)")
        return summary, faqs

    print(f"--- Uploading file to Gemini (Lang: {language}) ---")
    try:
        # 1. Upload the file
        uploaded_file = genai.upload_file(filepath)
        print(f"File uploaded: {uploaded_file.name}")
        
        # 2. Wait for processing (important for large files)
        while uploaded_file.state.name == "PROCESSING":
            print("Processing file...")
            time.sleep(2)
            uploaded_file = genai.get_file(uploaded_file.name)
            
        if uploaded_file.state.name == "FAILED":
             raise ValueError("Gemini file processing failed.")

        # 3. Generate Content
        print("--- Using Model: gemini-flash-latest ---")
        model = genai.GenerativeModel('gemini-flash-latest')
        
        # Call 1: Summary
        print("-> Generating Summary (File Mode)...")
        prompt_summary = f"""
        Read the document and write a Detailed Summary (300 words) in {language}.
        Return PLAIN TEXT only.
        """
        response_summary = retry_gemini_call(lambda: model.generate_content([prompt_summary, uploaded_file]))
        summary_text = response_summary.text.strip()

        # Call 2: FAQs
        print("-> Generating FAQs (File Mode)...")
        prompt_faqs = f"""
        Read the document and generate 10 FAQs in {language}.
        Return ONLY valid JSON: [ {{ "question": "...", "answer": "..." }}, ... ]
        """
        response_faqs = retry_gemini_call(lambda: model.generate_content([prompt_faqs, uploaded_file]))
        faq_text = response_faqs.text.strip()
        
        # Clean JSON
        if "```json" in faq_text:
            faq_text = faq_text.replace("```json", "").replace("```", "")
        if "```" in faq_text:
            faq_text = faq_text.replace("```", "")
            
        import json
        try:
             faqs_data = json.loads(faq_text)
        except:
             print("JSON Parsing Failed for FAQs (File Mode). Using fallback.")
             faqs_data = [{"question": "Error parsing FAQs", "answer": "Invalid JSON format received."}]
             
        # Store context (Summary + FAQs) for chat
        data_store[file_id]['document_text'] = summary_text + "\n" + str(faqs_data)
             
        print("--- Gemini File API Success! ---")
        return summary_text, faqs_data

    except Exception as e:
        error_msg = str(e)
        print(f"!!! GEMINI FILE API ERROR: {error_msg} !!!")
        
        # Handle "Image input modality not enabled" (Error 400)
        if "400" in error_msg and "modality" in error_msg:
             friendly_error = "The current Free AI Model (Gemma-1b) creates text but cannot 'see' images or scanned PDFs. Please upload a Text-PDF (one you can copy-paste from)."
             return friendly_error, [{"question": "Why did this fail?", "answer": friendly_error}]

        return f"AI Analysis of Scanned File Failed. Error: {error_msg}.", faqs

def get_local_ip():
    """Try to determine the local network IP address."""
    s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    try:
        s.connect(('10.255.255.255', 1))
        IP = s.getsockname()[0]
    except Exception:
        IP = '127.0.0.1'
    finally:
        s.close()
    return IP

import threading

def process_background_task(file_id, text, filepath, language):
    """Background task to generate AI content."""
    print(f"[{file_id}] Starting Background AI Processing...")
    try:
        if text:
             summary, faqs = generate_ai_content(text, language)
             doc_text_for_chat = text
        else:
             print(f"[{file_id}] using Gemini File API for scanned doc...")
             summary, faqs = generate_ai_content_from_file(filepath, language)
             # Note: generate_ai_content_from_file updates data_store[file_id]['document_text'] internally if successful,
             # but we should ensure consistency here.
             # Actually, looking at generate_ai_content_from_file, it returns summary, faqs.
             # We need to construct the document_text equivalent.
             doc_text_for_chat = f"Summary: {summary}\nFAQs: {str(faqs)}" 
        
        # Update Data Store
        if file_id in data_store:
            data_store[file_id]['summary'] = summary
            data_store[file_id]['faqs'] = faqs
            data_store[file_id]['document_text'] = doc_text_for_chat
            data_store[file_id]['ai_status'] = 'completed'
            print(f"[{file_id}] Background Processing COMPLETE")
            
    except Exception as e:
        print(f"[{file_id}] Background Processing FAILED: {e}")
        if file_id in data_store:
            data_store[file_id]['summary'] = f"Error generating content: {str(e)}"
            data_store[file_id]['ai_status'] = 'error'

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/upload', methods=['POST'])
def upload_file():
    if 'file' not in request.files:
        return redirect(request.url)
    
    file = request.files['file']
    language = request.form.get('language', 'English') # Get selected language
    
    if file.filename == '':
        return redirect(request.url)
        
    if file:
        filename = secure_filename(file.filename)
        file_id = str(uuid.uuid4())
        save_path = os.path.join(app.config['UPLOAD_FOLDER'], f"{file_id}_{filename}")
        file.save(save_path)
        
        # 1. Quick Text Extraction (Blocking - usually fast)
        text, error = extract_text(save_path)
        
        # 2. Return Response INSTANTLY
        # Initialize placeholder data
        data_store[file_id] = {
            'original_filename': filename,
            'summary': "Generating summary... please wait.",
            'faqs': [],
            'chat_history': [],
            'document_text': "",
            'language': language,
            'scan_status': 'pending',
            'ai_status': 'processing' # New Status
        }
        
        if error and "No text found" in error:
             # Scanned PDF case - Text is None
             threading.Thread(target=process_background_task, args=(file_id, None, save_path, language)).start()
        elif error:
             return f"Error processing file: {error}", 400
        else:
             # Normal Text case
             threading.Thread(target=process_background_task, args=(file_id, text, save_path, language)).start()

        return redirect(url_for('result', file_id=file_id))
            
    return "Error processing file", 500

@app.route('/result/<file_id>')
def result(file_id):
    if file_id not in data_store:
        return "File not found", 404
        
    hostname = get_local_ip()
    port = 5000
    mobile_url = f"http://{hostname}:{port}{url_for('mobile_view', file_id=file_id)}"
    
    qr = qrcode.QRCode(version=1, box_size=10, border=5)
    qr.add_data(mobile_url)
    qr.make(fit=True)
    img = qr.make_image(fill_color="black", back_color="white")
    
    qr_filename = f"qr_{file_id}.png"
    qr_path = os.path.join(app.config['UPLOAD_FOLDER'], qr_filename)
    img.save(qr_path)
    
    return render_template('result.html', qr_image=qr_filename, mobile_url=mobile_url, file_id=file_id)

@app.route('/mobile/<file_id>')
def mobile_view(file_id):
    if file_id not in data_store:
        return "File not found", 404
    return render_template('mobile_view.html', file_id=file_id)

@app.route('/api/data/<file_id>')
def get_data(file_id):
    if file_id not in data_store:
        return jsonify({"error": "Not found"}), 404
    
    data = data_store[file_id]
    return jsonify({
        "summary": data['summary'],
        "faqs": data['faqs'],
        "ai_status": data.get('ai_status', 'completed')
    })

# --- NEW SYNC ENDPOINTS ---
@app.route('/api/scan_event/<file_id>', methods=['POST'])
def scan_event(file_id):
    if file_id in data_store:
        data_store[file_id]['scan_status'] = 'scanned'
        return jsonify({'status': 'ok'})
    return jsonify({'error': 'not found'}), 404

@app.route('/api/check_scan/<file_id>')
def check_scan(file_id):
    if file_id in data_store:
        return jsonify({'status': data_store[file_id].get('scan_status', 'pending')})
    return jsonify({'error': 'not found'}), 404
# ---------------------------

@app.route('/api/chat', methods=['POST'])
def chat():
    data = request.json
    user_message = data.get('message', '')
    file_id = data.get('file_id')
    
    if not file_id or file_id not in data_store:
        return jsonify({"error": "Context missing"}), 400
        
    # Language Context
    language = data_store[file_id].get('language', 'English')
    
    # Sentiment Analysis (Optional - keeping for metrics but not for control)
    blob = TextBlob(user_message)
    # polarity = blob.sentiment.polarity 
    
    # AI Response
    if GOOGLE_API_KEY != "PASTE_YOUR_GOOGLE_API_KEY_HERE":
        try:
            # Consistent Model
            model = genai.GenerativeModel('gemini-flash-latest')
            doc_context = data_store[file_id].get('document_text', '')
            chat = model.start_chat(history=[])
            
            # Optimized Context-First Prompt for Small Model
            prompt = f"""
            You are an expert AI assistant helping a user understand a document.
            
            [DOCUMENT CONTEXT]
            {doc_context[:10000]}
            
            [USER QUESTION]
            {user_message}
            
            [INSTRUCTION]
            You are an empathetic and helpful AI assistant. Your goal is to help the user understand the document while being polite and aware of their tone.

            1. **Analyze Tone**: If the user seems angry, frustrated, or rude (e.g., "tell me correctly", "don't lie"), START your response with a sincere apology (e.g., "I apologize if my previous answer was not helpful.").
            2. **Handle Greetings**: If the user says "Hi", "Hello", or "Thank you", respond politely/warmly before waiting for a question.
            3. **Strict Context**: Answer purely based on the [DOCUMENT CONTEXT] above. Do not use outside knowledge.
            4. **Not Found**: If the answer is NOT in the document, say: "I checked the document carefully, but I couldn't find specific information about that." (Do NOT say "I found nothing" bluntly).
            5. **Definitions**: If asked to explain/define a term, define it clearly using the document text.
            """
            
            # Wrapped call with retry
            response = retry_gemini_call(lambda: chat.send_message(prompt))
            ai_text = response.text
        except Exception as e:
            ai_text = f"(AI Error matching language: {str(e)})"
        except Exception as e:
            ai_text = f"(AI Error matching language: {str(e)})"
    else:
        ai_text = "Mock AI response."
    
    return jsonify({
        "response": ai_text,
        "is_angry": False # Handled internally by AI now
    })

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000)
