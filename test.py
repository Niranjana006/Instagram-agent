import requests
import json

# 1. Configuration
API_URL = "https://weaponless-sibyl-heteromorphic.ngrok-free.dev/api/v1/instagram/webhook"
# 2. The Fake "Customer" Comment
# This looks exactly like the data Instagram sends you
fake_payload = {
  "entry": [
    {
      "changes": [
        {
          "field": "comments",
          "value": {
            "id": "17980238201937623",
            "text": "Nice",
            "media": {
              # Use a real media ID from your DB if you want the AI to read the caption
              # Or leave this dummy one (AI will just say 'No context found' but still reply)
              "id": "17903028441326536" 
            }
          }
        }
      ]
    }
  ]
}

print(f"🚀 Sending fake webhook to {API_URL}...")

try:
    response = requests.post(API_URL, json=fake_payload)
    print(f"✅ Status Code: {response.status_code}")
    print(f"📄 Response: {response.text}")
    print("\n👉 NOW CHECK YOUR 'WORKER' TERMINAL TO SEE THE AI REPLY!")
except Exception as e:
    print(f"❌ Failed: {e}")