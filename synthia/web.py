from flask import Flask, render_template, jsonify, request
import logging
import sql
import gmail

app = Flask(__name__, template_folder="/app/templates")

# Enable logging for debugging
logging.basicConfig(level=logging.INFO)

@app.before_request
def log_request():
    """Log all incoming requests for debugging."""
    logging.info(f"📥 Received request: {request.method} {request.path} from {request.remote_addr}")

@app.route("/")
def index():
    """Render main dashboard."""
    logging.info("✅ Rendering index.html")
    data = sql.get_email_data()
    return render_template("index.html", **data)

@app.route("/settings")
def settings():
    """Render settings page."""
    logging.info("✅ Rendering settings.html")
    return render_template("settings.html")

@app.route("/ingress/settings")
def ingress_settings():
    """Handle Ingress requests to `/settings`."""
    logging.info("✅ Rendering settings.html via Ingress")
    return render_template("settings.html")

@app.route("/clear_and_refresh", methods=["POST"])
def clear_and_refresh():
    """Clear email table and fetch new emails."""
    try:
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

def run():
    """Run the Flask web server on Ingress port 5000."""
    logging.info("🚀 Starting Flask web server on port 5000")
    app.run(host="0.0.0.0", port=5000, debug=False)

if __name__ == "__main__":
    run()
