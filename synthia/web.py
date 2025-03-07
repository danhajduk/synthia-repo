from flask import Flask, render_template, jsonify, request
import logging
import sql
import gmail

app = Flask(__name__, template_folder="/app/templates")  # Ensure correct template path

def get_email_data():
    """Fetch email summary data from the database."""
    try:
        data = sql.get_email_data()
        if isinstance(data["senders"], list):
            data["senders"] = {sender["sender"]: sender["count"] for sender in data["senders"]}
        return data
    except Exception as e:
        logging.error(f"Error fetching email data: {e}")
        return {
            "unread_count": 0,
            "last_fetch": "Never",
            "cutoff_date": "N/A",
            "senders": {}
        }

@app.route("/")
def index():
    """Render main dashboard."""
    data = get_email_data()
    return render_template("index.html", **data)

@app.route("/settings")
def settings():
    """Render settings page."""
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

        return jsonify({"message": "Database cleared & emails refreshed."})
    except Exception as e:
        logging.error(f"Error clearing and refreshing emails: {e}")
        return jsonify({"message": "Error occurred."}), 500

def run():
    """Run the Flask web server on Ingress port 5000."""
    app.run(host="0.0.0.0", port=5000, debug=False)

if __name__ == "__main__":
    run()
