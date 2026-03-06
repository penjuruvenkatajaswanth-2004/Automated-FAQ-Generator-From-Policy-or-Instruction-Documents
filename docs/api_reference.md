# API Reference

The backend Flask server exposes several endpoints to handle file uploads, generate AI tasks, and interact with the user via chat.

## Document Upload & AI Control

### `POST /upload`
Uploads a document (PDF, DOCX, TXT) and begins the background analysis process using Gemini AI.
- **Form Data:**
  - `file`: The document to upload.
  - `language`: Target language for FAQs and Summary (e.g., "English", "Spanish", "Hindi").
- **Response:** Redirects seamlessly to `/result/<file_id>`

### `GET /api/data/<file_id>`
Fetches the current analysis results for a specific uploaded document. This is polled by the frontend to react when AI finishes its task.
- **Response Format (JSON):**
  - `summary`: The generated document summary string.
  - `faqs`: List of FAQ JSON objects (each containing a `question` and `answer`).
  - `ai_status`: Background processing status indicator (`processing`, `completed`, or `error`).

## Interactive AI Chat

### `POST /api/chat`
Ask specific questions dynamically generated from the uploaded document's context.
- **JSON Payload:**
  - `message`: User's question string.
  - `file_id`: Unique Identifier of the previously processed document context.
- **Response Format (JSON):**
  - `response`: The AI's isolated contextual answer based completely on the doc content without hallucination.
  - `is_angry`: Internal tracking boolean checking the sentiment of the user's message.

## Synchronization Endpoints

### `POST /api/scan_event/<file_id>`
Triggered implicitly when the mobile device directly loads the QR code linked mobile view. It alerts the server that the sync established.

### `GET /api/check_scan/<file_id>`
A polling mechanism constantly returning data to check if the QR code sync has been completed (`pending` vs `scanned`).
