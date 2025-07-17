# backend/openai_client.py
import os
import logging
import openai
import sys
from dotenv import load_dotenv
from openai import OpenAIError

load_dotenv()
logging.debug(f"Loaded environment: PYTHONPATH={os.environ.get('PYTHONPATH')}, CWD={os.getcwd()}, Executable={sys.executable}")

OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")

if not OPENAI_API_KEY:
    raise ValueError("OPENAI_API_KEY not found in environment variables.")

client = openai.OpenAI(api_key=OPENAI_API_KEY)

def call_openai_gpt4(prompt: str) -> str:
    logging.info("Sending prompt to OpenAI o3-mini...")
    try:
        response = client.chat.completions.create(
            model="o3-mini",
            messages=[
                {"role": "system", "content": "You are a helpful assistant."},
                {"role": "user", "content": prompt}
            ],
            max_completion_tokens=4000,  # Correct parameter for o3-mini
        )
        result = response.choices[0].message.content
        logging.info(f"o3-mini response received: {result}")
        print("\n--- OPENAI o3-mini RESPONSE ---\n")
        print(result)
        return result
    except openai.OpenAIError as e:
        logging.error(f"OpenAI API error: {str(e)} - Details: {e.__dict__}")
        print(f"Error calling OpenAI o3-mini: {str(e)}")
        return ""
    except Exception as e:
        logging.error(f"Unexpected error calling OpenAI: {str(e)}")
        print(f"Error calling OpenAI o3-mini: {str(e)}")
        return ""