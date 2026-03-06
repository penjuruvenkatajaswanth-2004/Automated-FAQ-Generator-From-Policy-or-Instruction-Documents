import requests
import os

BASE_URL = "http://127.0.0.1:5000"

def test_routes():
    try:
        # 1. Test Home
        print("Testing Homepage...")
        r = requests.get(BASE_URL + "/")
        if r.status_code == 200:
            print("âœ… Homepage accessible.")
        else:
            print(f"âŒ Homepage failed: {r.status_code}")

        # 2. Test Chat API (Mock)
        print("\nTesting Chatbot API...")
        payload = {"message": "I am very angry!", "file_id": "test_id_123"} 
        # Note: In real app, file_id needs to exist. We'll skip deep functional test in this simple check
        # or we have to upload a file first. 
        # Let's just check if it handles missing context gracefully or we can mock the data_store in app if we could.
        # For now, we expect a 400 or 404 because "test_id_123" doesn't exist in the memory of the running server.
        
        r = requests.post(BASE_URL + "/api/chat", json=payload)
        if r.status_code in [200, 400, 404]: 
            # 400/404 is actually "correct" behavior for an invalid ID, proving the route exists.
            print(f"âœ… Chat API endpoint reachable (Status: {r.status_code}).")
        else:
            print(f"âŒ Chat API failed: {r.status_code}")

    except Exception as e:
        print(f"âŒ Connection failed. Is the server running? Error: {e}")

if __name__ == "__main__":
    print("WARNING: Run 'python app.py' in a separate terminal before running this script.\n")
    test_routes()
