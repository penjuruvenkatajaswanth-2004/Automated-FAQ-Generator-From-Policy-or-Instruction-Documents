# System Architecture

The Automated FAQ Generator is a modular web application that orchestrates file parsing, Background AI processing, and real-time user chat interaction.

## Technical Stack
- **Backend:** Python, Flask, Werkzeug
- **Frontend:** HTML5, CSS3, JavaScript, Jinja2 Templates (inside `frontend/`)
- **AI Integration:** Google Generative AI (Gemini Flash)
- **Document Processing:** PyPDF2 (for PDFs), python-docx (for DOCX files)

## Core Flow Overview
1. **Frontend Submit:** The user uploads a file on the main landing page via `POST /upload`. 
2. **Text Extraction:** The `extract_text()` utility parses the document and converts it to a raw string format. If the file is a scanned document (image-based PDF), it utilizes the Gemini File API fallback.
3. **Background AI Task:** The Document ID is stored in memory (`data_store`), and a `process_background_task()` python thread runs asynchronously. It manages the dual generation of Summaries and JSON-formatted FAQs. It handles retries and specific API rate limiting exceptions safely.
4. **Contextual Chat:** Uses the processed text context (`document_text`) to power conversational prompts on `POST /api/chat`, strictly bound to the uploaded text so the AI doesn't hallucinate outside information.
5. **Mobile Sync:** Unique QR codes generated via `qrcode` store URL schemas, redirecting mobile devices to polling endpoints linking the desktop visualization session instance with the mobile instance.
