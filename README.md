# Automated FAQ Generator for Policy Documents

This project is an automated system for reading policy documents (PDF, DOCX, TXT), extracting their texts, and utilizing Generative AI (Google Gemini) to dynamically generate detailed summaries and Frequently Asked Questions (FAQs) in multiple languages.

## Features

- **Document Parsing:** Upload PDF, DOCX, or TXT formats easily.
- **AI-Powered Insights:** Automatically generate summaries and tailored FAQs from document content using Google Gemini.
- **Multilingual Support:** Select output language for FAQs and summaries dynamically.
- **Scanned Document Support:** Utilizes the Gemini File API to understand scanned documents and images.
- **Interactive Chat Interface:** Allows users to ask questions via an interactive chat, context-aware from the uploaded file text.
- **Mobile QR Synchronization:** Get a generated QR code to easily access the document results and chat on a mobile device.

## Prerequisites

- Python 3.9+
- A valid Google Gemini API Key

## Getting Started

1. Clone the repository.
2. Install the requirements:
   ```bash
   pip install -r requirements.txt
   ```
3. Copy `.env.example` to `.env` and fill in your `GOOGLE_API_KEY`.
4. Run the application:
   ```bash
   python backend/app.py
   ```
5. Open your browser and navigate to `http://localhost:5000`.

## Directory Structure

Check out the folders inside for different modules of the project:
* `backend/` - Contains the core Flask server logic.
* `frontend/` - Contains UI templates and static assets.
* `data/` - Holds knowledge base inputs like Excel datasets.
* `models/` - Contains configuration and list files for available AI models.
* `scripts/` - Additional utility scripts.
* `tests/` - Contains project test files.
* `docs/` - For comprehensive documentation.
* `deployment/` - For deployment configurations like Docker.
