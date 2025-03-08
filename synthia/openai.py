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

def generate_json_response(prompt, json_schema, system_role):
    """
    Generate a structured JSON response using OpenAI's GPT-4o mini API with a predefined JSON schema.

    Args:
        prompt (str): The prompt to send to the OpenAI API.
        json_schema (dict): The JSON schema to enforce the output format.
        system_role (str): The system role content to provide context for OpenAI.

    Returns:
        dict: Parsed JSON response from OpenAI.
    """
    config = load_openai_config()
    api_key = config.get("openai_api_key")

    if not api_key:
        logging.error("❌ OpenAI API key is missing.")
        return {}

    headers = {
        "Content-Type": "application/json",
        "Authorization": f"Bearer {api_key}"
    }

    data = {
        "model": "gpt-4o-mini",
        "messages": [
            {
                "role": "system",
                "content": system_role + 
                           "\nEnsure the response strictly follows this JSON format without additional text:\n\n" +
                           json.dumps(json_schema, indent=2)
            },
            {"role": "user", "content": prompt}
        ],
        "max_tokens": 300,
        "temperature": 0.3
    }

    try:
        response = requests.post("https://api.openai.com/v1/chat/completions", headers=headers, json=data)
        response.raise_for_status()
        result = response.json()

        # Ensure response is properly formatted
        raw_content = result["choices"][0]["message"]["content"]
        
        # Strip potential code blocks
        json_content = raw_content.replace("```json", "").replace("```", "").strip()
        
        json_response = json.loads(json_content)
        return json_response
    except requests.exceptions.HTTPError as e:
        logging.error(f"❌ HTTP error generating response from OpenAI: {e}")
        return {}
    except Exception as e:
        logging.error(f"❌ Error generating response from OpenAI: {e}")
        return {}

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

    # Define JSON schema for expected OpenAI response
    json_schema = {
        "type": "object",
        "properties": {
            "important_senders": {
                "type": "array",
                "items": {
                    "type": "string"
                }
            }
        },
        "required": ["important_senders"]
    }

    # Format the senders as JSON instead of a long string list
    senders_json = json.dumps({"senders": senders}, indent=2)

    # Prepare the prompt for OpenAI
    prompt = (
        "Identify important email senders from the following JSON list and return them in JSON format:\n\n" + senders_json
    )
    logging.info(f"📝 Prompt sent to OpenAI: {prompt}")
    
    # Generate response using OpenAI with JSON schema
    response = generate_json_response(prompt, json_schema, "You are an AI that filters important email senders and returns structured JSON output.")
    
    if not response:
        logging.error("❌ No response received from OpenAI.")
        return []

    important_senders = response.get("important_senders", [])
    logging.info(f"✅ Identified important senders: {important_senders}")
 
    # Save the identified important senders to the database
    for sender in important_senders:
        if sender:
            sql.add_important_sender(sender, category="Important")

    return important_senders

if __name__ == "__main__":
    # Example usage
    prompt = "What is the capital of France?"
    response = generate_json_response(prompt, {
        "type": "object",
        "properties": {
            "answer": {"type": "string"}
        },
        "required": ["answer"]
    }, "You are an AI that provides concise and factual answers.")
    print(response)

    important_senders = identify_important_senders()
    print("Important senders identified by OpenAI:", important_senders)
