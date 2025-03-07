FROM python:3.10-slim

# Set up working directory
WORKDIR /app

# Install system dependencies (SQLite3)
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

# Copy all required scripts
COPY synthia.py /app/synthia.py
COPY gmail.py /app/gmail.py
COPY sql.py /app/sql.py  # <-- Ensure this is included
COPY web.py /app/web.py
COPY templates /app/templates

# Start Synthia (it will start web.py internally)
CMD ["python3", "/app/synthia.py"]
