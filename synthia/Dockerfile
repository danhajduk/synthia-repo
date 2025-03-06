FROM python:3.10-slim

# Set up working directory
WORKDIR /app

# Install dependencies (if needed)
RUN pip install --no-cache-dir requests

# Copy the script
COPY synthia.py /app/synthia.py

# Set the command to run
CMD ["python3", "/app/synthia.py"]
