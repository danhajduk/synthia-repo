import logging
import time
import threading
import gmail
import sql
import web

# Configure Logging
logging.basicConfig(
    format="%(asctime)s - INFO - %(message)s",
    level=logging.INFO
)

def start_web_server():
    """Start the Flask web server in a separate thread."""
    logging.info("Starting Web UI...")
    threading.Thread(target=web.run, daemon=True).start()

def main_loop():
    """Main loop to fetch emails and store them in the database."""
    while True:
        logging.info("Checking for unread emails...")
        emails = gmail.fetch_important_emails()
        
        if emails:
            sender_counts = {}
            for email in emails:
                sender_counts[email] = sender_counts.get(email, 0) + 1
            sql.save_email_data(len(emails), sender_counts)

        time.sleep(600)  # Wait 10 minutes before fetching again

if __name__ == "__main__":
    logging.info("Synthia is running...")
    sql.create_table()  # Ensure table exists
    start_web_server()  # Start the web UI
    main_loop()  # Start the email checking loop
