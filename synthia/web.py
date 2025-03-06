from flask import Flask, render_template, jsonify
import json
import os
from datetime import datetime, timedelta

app = Flask(__name__, template_folder="/app/templates")

CONFIG_PATH = "/data/options.json"

def load_config():
    """Load the Home Assistant configuration file."""
    try:
        if not os.path.exists(CONFIG_PATH):
            return {}
        with open(CONFIG_PATH, "r") as f:
            return json.load(f)
    except json.JSONDecodeError:
        return {}

@app.route("/")
def index():
    """Render the web UI."""
    config = load_config()

    # Get version from config.json
    version = config.get("version", "Unknown")

    # Load email data
    email_data = {"unread_count": 0, "last_fetch": "Never"}
    try:
        with open("/data/email_data.json") as f:
            email_data = json.load(f)
    except json.JSONDecodeError:
        pass

    # Calculate cutoff date based on `days_to_fetch`
    days_to_fetch = config.get("general", {}).get("days_to_fetch", 7)
    cutoff_date = (datetime.utcnow() - timedelta(days=days_to_fetch)).strftime("%Y-%m-%d")

    return render_template("index.html",
                           version=version,
                           unread_count=email_data.get("unread_count", 0),
                           last_fetch=email_data.get("last_fetch", "Never"),
                           cutoff_date=cutoff_date)

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=True)
