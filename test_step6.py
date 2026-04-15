import requests
import json

# Test the API endpoint
url = "http://localhost:8000/chat"
payload = {
    "query": "What is SBI Large Cap Fund?",
    "session_id": "test1"
}

try:
    response = requests.post(url, json=payload, timeout=30)
    print(f"Status Code: {response.status_code}")
    print(f"Response: {json.dumps(response.json(), indent=2)}")
except requests.exceptions.ConnectionError:
    print("Connection Error: Could not connect to the API server")
except Exception as e:
    print(f"Error: {e}")
