FROM python:3.10-slim

# Set up environment
WORKDIR /app

# Install dependencies
RUN pip install requests openai google-auth google-auth-oauthlib google-auth-httplib2 google-api-python-client

# Copy script and run it
COPY synthia.py /app/synthia.py

CMD ["python3", "/app/synthia.py"]
