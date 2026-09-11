import requests
import os
import shutil

# Manually load env to avoid circular imports errors
env_path = ".env"
config = {}

# Read the current .env file
if os.path.exists(env_path):
    with open(env_path, "r") as f:
        for line in f:
            if "=" in line and not line.startswith("#"):
                key, val = line.strip().split("=", 1)
                config[key] = val

APP_ID = config.get("INSTAGRAM_APP_ID")
APP_SECRET = config.get("INSTAGRAM_APP_SECRET")

def update_env_file(new_token):
    """Safely updates the .env file with the new token"""
    temp_path = ".env.tmp"
    with open(env_path, "r") as input_file, open(temp_path, "w") as output_file:
        for line in input_file:
            if line.startswith("INSTAGRAM_ACCESS_TOKEN="):
                # Replace the old line completely
                output_file.write(f"INSTAGRAM_ACCESS_TOKEN={new_token}\n")
            else:
                output_file.write(line)
    
    # Move temp file to actual file
    shutil.move(temp_path, env_path)
    print(f"✅ SUCCESS: Updated {env_path} with the new Long-Lived Token.")

def exchange_token():
    print("--- 🔄 AUTO TOKEN FIXER ---")
    
    if not APP_ID or not APP_SECRET:
        print("❌ Error: Could not find App ID/Secret in .env. Check your file!")
        return

    print("1. Go to Graph API Explorer: https://developers.facebook.com/tools/explorer/")
    print("2. Make sure 'InfluencerBot' is selected in the top right.")
    print("3. Click the blue 'Generate Access Token' button.")
    short_token = input("\n👉 Paste that new SHORT token here: ").strip()
    
    if not short_token:
        print("❌ Token cannot be empty.")
        return

    # The magic Facebook endpoint to swap tokens
    url = "https://graph.facebook.com/v19.0/oauth/access_token"
    params = {
        "grant_type": "fb_exchange_token",
        "client_id": APP_ID,
        "client_secret": APP_SECRET,
        "fb_exchange_token": short_token
    }
    
    try:
        response = requests.get(url, params=params)
        data = response.json()
        
        if "access_token" in data:
            long_token = data["access_token"]
            expires_in_seconds = data.get("expires_in", 0)
            days = expires_in_seconds / 60 / 60 / 24
            
            print(f"\n🎉 GOT IT! New Token valid for: {days:.1f} days.")
            
            # UPDATE THE FILE AUTOMATICALLY
            update_env_file(long_token)
            
            print("\n" + "="*50)
            print("🚨 CRITICAL: YOU MUST RESTART THE WORKER NOW 🚨")
            print("="*50)
            print("The worker has the OLD token loaded in its RAM.")
            print("1. Go to your Worker terminal.")
            print("2. Press CTRL+C to stop it.")
            print("3. Run the start command again.")
        else:
            print("\n❌ FAILED to exchange token.")
            print(f"Facebook says: {data}")
            
    except Exception as e:
        print(f"Network Error: {e}")

if __name__ == "__main__":
    exchange_token()