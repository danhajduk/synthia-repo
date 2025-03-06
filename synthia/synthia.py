import time
import logging

# Configure Logging
logging.basicConfig(
    format="%(asctime)s - INFO - %(message)s",
    level=logging.INFO
)

if __name__ == "__main__":
    while True:
        logging.info("Synthia is on")
        time.sleep(10)  # Log every 10 seconds
