import os
import requests
from dotenv import load_dotenv

def send_telegram_message(message: str):
    """
    Sends a message to the configured Telegram chat.
    Requires TELEGRAM_BOT_TOKEN and TELEGRAM_CHAT_ID in .env
    """
    load_dotenv()
    
    bot_token = os.getenv("TELEGRAM_BOT_TOKEN")
    chat_id = os.getenv("TELEGRAM_CHAT_ID")
    
    if not bot_token or not chat_id:
        print("[!] Telegram credentials missing in .env file.")
        return False
        
    url = f"https://api.telegram.org/bot{bot_token}/sendMessage"
    payload = {
        "chat_id": chat_id,
        "text": message,
        "parse_mode": "Markdown"
    }
    
    try:
        response = requests.post(url, json=payload)
        if response.status_code == 200:
            print("[+] Telegram message sent successfully!")
            return True
        else:
            print(f"[!] Failed to send Telegram message: {response.text}")
            return False
    except Exception as e:
        print(f"[!] Exception while sending Telegram message: {e}")
        return False

if __name__ == "__main__":
    # Test execution
    test_msg = "🚀 *PhantomX AGI Update*\nThis is a test notification from your Ghost Hunter Bot."
    send_telegram_message(test_msg)
