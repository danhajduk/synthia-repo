import os
import json
import requests

# Load options from Home Assistant
CONFIG_PATH = "/data/options.json"
with open(CONFIG_PATH) as f:
    config = json.load(f)

GMAIL_API_KEY = config["gmail_api_key"]
OPENAI_API_KEY = config["openai_api_key"]
NOTIFY_SERVICE = config["notify_service"]

def send_notification(message):
    """Send a notification to Home Assistant."""
    url = "http://supervisor/core/api/services/" + NOTIFY_SERVICE
    headers = {
        "Authorization": f"Bearer {os.getenv('SUPERVISOR_TOKEN')}",
        "Content-Type": "application/json",
    }
    data = {"message": message}
    response = requests.post(url, headers=headers, json=data)
    print("Notification sent:", response.status_code)

if __name__ == "__main__":
    send_notification("Synthia is running! Gmail and OpenAI integration coming soon!")
