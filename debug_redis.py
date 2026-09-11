from celery import Celery
import sys

def test_connection(url):
    print(f"Testing: {url} ... ", end="")
    try:
        app = Celery(broker=url)
        with app.connection_for_write() as conn:
            conn.connect()
        print("✅ SUCCESS!")
        return True
    except Exception as e:
        print(f"❌ FAILED. ({str(e)})")
        return False

if __name__ == "__main__":
    print("--- REDIS CONNECTION DIAGNOSTIC ---")
    
    urls = [
        "redis://127.0.0.1:6379/0",
        "redis://localhost:6379/0",
        "redis://0.0.0.0:6379/0"
    ]
    
    working_url = None
    for url in urls:
        if test_connection(url):
            working_url = url
            break
            
    if working_url:
        print(f"\n🎉 FOUND WORKING URL: {working_url}")
        print(f"👉 Please update your .env file to use EXACTLY this URL.")
    else:
        print("\n💀 ALL CONNECTIONS FAILED.")
        print("Is Redis (Memurai) running? Check Task Manager.")