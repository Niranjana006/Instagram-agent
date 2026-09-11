import requests
import os

# --- HARDCODED TOKEN FOR DEBUGGING ---
# Replace the string below with your actual Long-Lived Token starting with EAAV...
import os
from dotenv import load_dotenv

load_dotenv()

# Read the token from the .env file instead of hardcoding
USER_TOKEN = os.getenv("INSTAGRAM_ACCESS_TOKEN") 
# -------------------------------------

def enable_webhooks():
    print("--- 🔌 FORCE SUBSCRIBING APP TO PAGE ---")
    
    if USER_TOKEN == "PASTE_YOUR_TOKEN_HERE":
        print("❌ Error: You didn't paste your token into the script yet!")
        print("Open influencer_agent/force_subscribe.py and paste your EAAV... token.")
        return

    # 1. Get the Facebook Page ID and Page Access Token
    url = "https://graph.facebook.com/v19.0/me/accounts"
    params = {"access_token": USER_TOKEN}
    
    try:
        resp = requests.get(url, params=params)
        data = resp.json()
        
        if "data" not in data:
            print(f"❌ Error fetching pages: {data}")
            return

        pages = data["data"]
        print(f"✅ Found {len(pages)} Facebook Page(s).")

        for page in pages:
            page_id = page["id"]
            page_name = page["name"]
            page_token = page["access_token"]
            
            print(f"\nProcessing Page: {page_name} (ID: {page_id})...")
            
            # 2. Subscribe the App to this Page
            sub_url = f"https://graph.facebook.com/v19.0/{page_id}/subscribed_apps"
            
            # Subscribe to 'feed' to ensure connection is active for comments
            sub_params = {
                "subscribed_fields": "feed", 
                "access_token": page_token
            }
            
            sub_resp = requests.post(sub_url, data=sub_params)
            sub_data = sub_resp.json()
            
            if sub_data.get("success"):
                print(f"   ✅ SUCCESS! App installed on Page '{page_name}'.")
                print("   🚀 Webhooks should now fire for the connected Instagram account!")
            else:
                print(f"   ❌ Failed to subscribe. Error: {sub_data}")

    except Exception as e:
        print(f"Network Error: {e}")

if __name__ == "__main__":
    enable_webhooks()