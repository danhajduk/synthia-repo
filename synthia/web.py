from flask import Flask, render_template, jsonify, request
import logging
import json
import sql
import gmail
import update  # Import the update script

app = Flask(__name__, template_folder="/app/templates")

# Enable logging for debugging
logging.basicConfig(level=logging.INFO)

fetching = False  # Track if emails are being fetched


def get_current_version():
    """Get the current version from options.json"""
    try:
        with open("/data/options.json", "r") as f:
            return json.load(f).get("version", "Unknown")
    except Exception as e:
        logging.error(f"Error reading version: {e}")
        return "Unknown"


@app.before_request
def log_request():
    """Log all incoming requests for debugging."""
    logging.info(f"📥 Received request: {request.method} {request.path} from {request.remote_addr}")


@app.route("/")
def index():
    """Render main dashboard."""
    logging.info("✅ Rendering index.html")
    
    try:
        unread_count, senders = sql.get_email_data()
    except ValueError as e:
        logging.error(f"❌ Error retrieving email data: {e}")
        unread_count, senders = 0, {}

    return render_template("index.html", version=get_current_version(), unread_count=unread_count, senders=senders)


@app.route("/settings")
def settings():
    """Render settings page."""
    logging.info("✅ Rendering settings.html")
    return render_template("settings.html")


@app.route("/fetch_status")
def fetch_status():
    """Return the current email fetching status."""
    status = "📩 Fetching emails..." if fetching else "✅ Ready"
    return jsonify({"status": status})


@app.route("/clear_and_refresh", methods=["POST"])
def clear_and_refresh():
    """Clear email table and fetch new emails."""
    global fetching
    try:
        fetching = True  # Set status to fetching
        sql.clear_email_table()
        emails = gmail.fetch_unread_emails()

        if emails:
            sender_counts = {}
            for email in emails:
                sender_counts[email] = sender_counts.get(email, 0) + 1
            sql.save_email_data(len(emails), sender_counts)

        logging.info("✅ Database cleared & emails refreshed.")
        return jsonify({"message": "Database cleared & emails refreshed."})
    except Exception as e:
        logging.error(f"❌ Error clearing and refreshing emails: {e}")
        return jsonify({"message": "Error occurred."}), 500
    finally:
        fetching = False  # Reset fetching status


@app.route("/check_update", methods=["POST"])
def check_update():
    """Check for updates and restart if needed."""
    latest_version = update.get_latest_version()
    if latest_version and update.update_config(latest_version):
        return jsonify({"message": f"Updated to {latest_version}, restarting..."})
    return jsonify({"message": "Already up to date."})


def run():
    """Run the Flask web server on port 5000."""
    logging.info("🚀 Starting Flask web server on port 5000")
    app.run(host="0.0.0.0", port=5000, debug=False)


if __name__ == "__main__":
    run()
