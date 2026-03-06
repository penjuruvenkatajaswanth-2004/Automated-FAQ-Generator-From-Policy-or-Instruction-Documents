# Deployment Guide

This Web Application is ready to be deployed on local servers, cloud Virtual Machines (AWS EC2, DigitalOcean Droplets, Azure Virtual Machines), or serverless container orchestration platforms.

## Production Checklist

Before deploying, ensure you have:
1. Created your `.env` file based off of `.env.example` directly in the root directory.
2. Saved your unique `GOOGLE_API_KEY` obtained from Google AI Studio.
3. Changed `FLASK_ENV` from `development` to `production`.

---

## 🚀 Option 1: Deploying with Docker (Recommended)

The easiest way to deploy and maintain parity with local development is using Docker Engine and Docker Compose. 
Ensure you have Docker installed on your host system.

1. Ensure the root directory `Dockerfile` and `docker-compose.yml` are loaded and set.
2. Build the Docker Container.
```bash
# Execute from the root directory of your project
docker-compose up -d --build
```
This will start the Flask server via detached mode accessible through port `5000` via your Host server's IP address.

To view background running logs:
```bash
docker-compose logs -f
```

---

## 🌐 Option 2: Production Proxy Server (Waitress / Gunicorn & Nginx)

If deploying directly on a Linux/Windows VM without Docker, do **not** use the built-in Flask development server (`python backend/app.py`). It is not optimized for security or multi-threading for the Gemini API requests.

### On Linux (Gunicorn)
Install Gunicorn into your Python environment:
```bash
pip install gunicorn
```

Run Gunicorn with multiple worker threads pointing to the `app` instance in `backend/app.py`:
```bash
# Allow long timeouts for large PDF processing
gunicorn --bind 0.0.0.0:5000 --workers 4 --timeout 120 "backend.app:app"
```

### On Windows (Waitress)
If hosting on Windows Server since Gunicorn is not supported natively:
```bash
pip install waitress
waitress-serve --port=5000 --threads=4 backend.app:app
```

### Nginx Reverse Proxy
To serve this cleanly with an SSL certificate and on standard ports (`80` or `443`), wrap your service behind an Nginx Reverse proxy using the provided `deployment/nginx.conf` stub file. This will direct public traffic onto your internal `5000` port gracefully.
