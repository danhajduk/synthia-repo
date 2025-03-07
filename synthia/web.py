from flask import Flask, render_template, jsonify
import logging
import sql

app = Flask(__name__)

def get_email_data():
    """Fetch email summary data from the database."""
    try:
        return sql.get_email_data()
    except Exception as e:
        logging.error(f"Error fetching email data: {e}")
        return {
            "unread_count": 0,
            "last_fetch": "Never",
            "cutoff_date": "N/A",
            "senders": []
        }

@app.route("/")
def index():
    """Render main UI with email data."""
    data = get_email_data()
    return render_template("index.html", **data)

@app.route("/api/status")
def api_status():
    """Return email summary data as JSON."""
    return jsonify(get_email_data())

def run():
    """Run the Flask web server on Ingress port 5000."""
    app.run(host="0.0.0.0", port=5000, debug=False)

if __name__ == "__main__":
    run()
