import logging
import json
import requests
import sql  # Import sql module to interact with the database

# Enable logging for debugging with timestamps
logging.basicConfig(level=logging.DEBUG, format='%(asctime)s %(levelname)s: %(message)s')

def load_openai_config():
    """
    Load OpenAI API credentials from the configuration file.

    Returns:
        dict: A dictionary containing OpenAI configuration.
    """
    try:
        with open("/data/options.json", "r") as f:
            config = json.load(f)
        logging.info("✅ OpenAI configuration successfully loaded.")
        return config["openai"]
    except Exception as e:
        logging.error(f"❌ Failed to load OpenAI configuration: {e}")
        return {}

def generate_response(prompt):
    """
    Generate a response using OpenAI's GPT-4o mini API.

    Args:
        prompt (str): The prompt to send to the OpenAI API.

    Returns:
        str: The generated response from OpenAI.
    """
    config = load_openai_config()
    api_key = config.get("openai_api_key")

    if not api_key:
        logging.error("❌ OpenAI API key is missing.")
        return "OpenAI API key is missing."

    headers = {
        "Content-Type": "application/json",
        "Authorization": f"Bearer {api_key}"
    }

    data = {
        "model": "gpt-4o-mini",
        "messages": [
            {"role": "system", "content": "you are a personal assistant that help with varius tasks."},
            {"role": "user", "content": prompt}
        ],
        "max_tokens": 150,
        "temperature": 0.7
    }

    try:
        response = requests.post("https://api.openai.com/v1/chat/completions", headers=headers, json=data)
        response.raise_for_status()
        result = response.json()
        return result["choices"][0]["message"]["content"].strip()
    except requests.exceptions.HTTPError as e:
        logging.error(f"❌ HTTP error generating response from OpenAI: {e}")
        return "HTTP error generating response from OpenAI."
    except Exception as e:
        logging.error(f"❌ Error generating response from OpenAI: {e}")
        return "Error generating response from OpenAI."

def identify_important_senders():
    """
    Identify important senders using the OpenAI API.

    Returns:
        list: A list of important senders identified by OpenAI.
    """
    logging.info("🔍 Identifying important senders using OpenAI...")

    # Fetch all senders from synthia_senders_summary that are not in synthia_important_senders
    try:
        conn = sql.connect_db()
        cursor = conn.cursor()
        cursor.execute('''
            SELECT sender FROM synthia_senders_summary
            WHERE sender NOT IN (SELECT sender FROM synthia_important_senders)
        ''')
        senders = [row[0] for row in cursor.fetchall()]
        conn.close()
    except Exception as e:
        logging.error(f"❌ Error fetching senders from database: {e}")
        return []

    if not senders:
        logging.info("No new senders to analyze.")
        return []

    # Prepare the prompt for OpenAI
    prompt = (
        "Identify which of the following email senders could be important. "
        "Return a list of important senders in csv format:\n\n" + "\n".join(senders)
    )
    logging.info(f"📝 Prompt sent to OpenAI: {prompt}")
    # Generate response using OpenAI
    response = generate_response(prompt)
    important_senders = response.split("\n")
    logging.info(f"📝 Response from OpenAI: {important_senders}")
    # Parse the response to extract senders
    parsed_senders = []
    for sender in important_senders:
        if sender.strip() and not sender.startswith("Identify"):
            parsed_senders.append(sender.strip())

    # Save the identified important senders to the database
    for sender in parsed_senders:
        if sender:
            sql.add_important_sender(sender, category="Important")

    logging.info(f"✅ Identified important senders: {parsed_senders}")
    return parsed_senders

if __name__ == "__main__":
    # Example usage
    prompt = "What is the capital of France?"
    response = generate_response(prompt)
    print(response)

    important_senders = identify_important_senders()
    print("Important senders identified by OpenAI:", important_senders)
