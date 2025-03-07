FROM python:3.10-slim

# Set up working directory
WORKDIR /app

# Install dependencies
RUN pip install --no-cache-dir \
    requests \
    flask \
    google-auth \
    google-auth-oauthlib \
    google-auth-httplib2 \
    google-api-python-client \
    sqlite3

# Ensure /data directory exists
RUN mkdir -p /data

# Copy files
COPY synthia.py /app/synthia.py
COPY web.py /app/web.py
COPY templates /app/templates

# Start both Synthia and Flask UI
CMD ["sh", "-c", "python3 /app/synthia.py & python3 /app/web.py"]
