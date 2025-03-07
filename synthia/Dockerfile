FROM python:3.10-slim

# Set up working directory
WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y sqlite3 && rm -rf /var/lib/apt/lists/*

# Install Python dependencies
RUN pip install --no-cache-dir \
    requests \
    flask \
    google-auth \
    google-auth-oauthlib \
    google-auth-httplib2 \
    google-api-python-client

# Ensure /data directory exists
RUN mkdir -p /data

# Copy files
COPY synthia.py /app/synthia.py
COPY web.py /app/web.py
COPY templates /app/templates

# Start both Synthia and Flask UI
CMD ["sh", "-c", "python3 /app/synthia.py & python3 /app/web.py"]
