import os
import sys
import subprocess
import time
import shutil

def install_pyngrok():
    try:
        import pyngrok
    except ImportError:
        print("[!] pyngrok helper not found. Installing...")
        subprocess.check_call([sys.executable, "-m", "pip", "install", "pyngrok", "--quiet"])
        print("[+] pyngrok installed successfully.")

install_pyngrok()
from pyngrok import ngrok, conf

def main():
    print("====================================================")
    print("    Starting Ngrok Tunnel for Whats360 Webhook      ")
    print("====================================================")

    # 1. Robust check for system ngrok
    system_ngrok = shutil.which("ngrok")
    
    if not system_ngrok:
        # Try common Windows paths or use 'where' command
        try:
            where_out = subprocess.check_output(["where", "ngrok"], stderr=subprocess.STDOUT, text=True)
            system_ngrok = where_out.splitlines()[0].strip()
        except Exception:
            # Check a very specific path we know exists from previous search
            fallback = os.path.expandvars(r"%LOCALAPPDATA%\Programs\Python\Python313\Scripts\ngrok.exe")
            if os.path.exists(fallback):
                system_ngrok = fallback

    if system_ngrok:
        print(f"[+] Found system ngrok at: {system_ngrok}")
        # Ensure path is absolute and quoted for pyngrok
        conf.get_default().ngrok_path = os.path.abspath(system_ngrok)
    else:
        print("[!] ngrok not found in PATH. pyngrok will try to manage its own binary.")

    port = 8080
    
    try:
        # Create tunnel
        public_url = ngrok.connect(port).public_url
        
        print("\n" + "*" * 70)
        print("[SUCCESS] Your Public Webhook URL is:")
        print(f"{public_url}/api/v1/webhook/whats360")
        print("*" * 70 + "\n")
        print("--> COPY the URL above and paste it into your Whats360 Dashboard.")
        print("--> The local backend will now start.")
        print("--> Keep this window open! Closing it will disconnect the webhook.\n")
        
        # Start the FastAPI backend
        subprocess.run([sys.executable, "-m", "uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", str(port), "--log-level", "info"])
        
    except KeyboardInterrupt:
        print("\n[!] Shutting down backend and tunnel...")
    except Exception as e:
        print(f"\n[!] Error starting tunnel: {e}")
        if "authtoken" in str(e).lower():
            print("\n[TIP] It looks like you need to set your ngrok auth token.")
            print("Run this command in a NEW terminal: ngrok config add-authtoken YOUR_TOKEN")
    finally:
        ngrok.kill()

if __name__ == "__main__":
    main()
