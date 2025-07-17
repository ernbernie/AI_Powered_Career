# backend/perplexity_client.py
import os
import logging
import requests
import json # Import json for detailed error logging

def call_perplexity_api(prompt: str) -> str:
    """
    Sends a prompt to the Perplexity API and returns the response.
    """
    api_key = os.getenv("PERPLEXITY_API_KEY")
    if not api_key:
        logging.error("PERPLEXITY_API_KEY environment variable not set")
        return "Error: Perplexity API key not configured."

    url = "https://api.perplexity.ai/chat/completions"
    headers = {
        "Authorization": f"Bearer {api_key}",
        "Content-Type": "application/json"
    }
    
    payload = {
        # FIX: Updated to the correct and most appropriate model name.
        "model": "sonar-deep-research",
        "messages": [
            {"role": "user", "content": prompt}
        ],
        "max_tokens": 4096,
        "temperature": 0.7 
    }
    
    logging.info("Sending prompt to Perplexity...")
    
    try:
        response = requests.post(url, headers=headers, json=payload, timeout=300)
        # This will raise an HTTPError if the HTTP request returned an unsuccessful status code
        response.raise_for_status()
        
        result = response.json()
        content = result["choices"][0]["message"]["content"]
        
        logging.info(f"Perplexity response received: {len(content)} characters")
        return content
        
    except requests.exceptions.HTTPError as http_err:
        # This enhanced logging will now catch any new errors.
        logging.error(f"HTTP error occurred: {http_err}")
        logging.error(f"Response status code: {http_err.response.status_code}")
        try:
            error_details = http_err.response.json()
            logging.error(f"Perplexity API Error Details: {json.dumps(error_details, indent=2)}")
            return f"Error from Perplexity API: {error_details.get('error', {}).get('message', 'Unknown error')}"
        except json.JSONDecodeError:
            logging.error(f"Raw error response: {http_err.response.text}")
            return f"Error communicating with Perplexity API. Raw response: {http_err.response.text}"
            
    except Exception as e:
        logging.error(f"An unexpected error occurred: {e}")
        return "An unexpected error occurred while calling Perplexity."
