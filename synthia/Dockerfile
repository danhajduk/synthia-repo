FROM python:3.10-slim

# Set up working directory
WORKDIR /app

# Install dependencies
RUN pip install --no-cache-dir \
    requests \
    google-auth \
    google-auth-oauthlib \
    google-auth-httplib2 \
    google-api-python-client

# Copy the script
COPY synthia.py /app/synthia.py

# Set the command to run
CMD ["python3", "/app/synthia.py"]
