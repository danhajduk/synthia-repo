import time
import logging
import os
import sql
import gmail
import web

# Configure Logging
logging.basicConfig(
    format="%(asctime)s - %(levelname)s - %(message)s",
    level=logging.INFO
)

def log_directory_structure():
    """Log the directory structure for debugging."""
    logging.info(f"Current working directory: {os.getcwd()}")

    directories = ["/", "/app", "/data"]
    for directory in directories:
        logging.info(f"Listing files in {directory}:")
        try:
            for item in os.listdir(directory):
                full_path = os.path.join(directory, item)
                logging.info(f" - {full_path} ({'DIR' if os.path.isdir(full_path) else 'FILE'})")
        except Exception as e:
            logging.error(f"Could not list {directory}: {e}")

def main_loop():
    """Main loop to check and save emails."""
    while True:
        logging.info("Checking for unread emails...")
        emails = gmail.fetch_unread_emails()
        if emails:
            sender_counts = {}
            for email in emails:
                sender_counts[email] = sender_counts.get(email, 0) + 1
            sql.save_email_data(len(emails), sender_counts)
            logging.info("Email data successfully saved to Synthia's database.")
        else:
            logging.info("No new emails found.")
        time.sleep(600)  # Fetch emails every 10 minutes

if __name__ == "__main__":
    logging.info("#####################################################################################")
    logging.info("Synthia is running...")
    log_directory_structure()
    sql.create_table()  # Ensure the database table exists
    logging.info("Starting Web UI...")
    web.run()  # Start the Flask web server in a separate thread
    main_loop()
