# backend/perplexity_client.py
import os, logging, requests, json
from dotenv import load_dotenv
load_dotenv()

API_KEY = os.getenv("PERPLEXITY_API_KEY")
if not API_KEY:
    raise RuntimeError("PERPLEXITY_API_KEY missing")

HEADERS = {
    "Authorization": f"Bearer {API_KEY}",
    "Content-Type": "application/json"
}

def call_perplexity_api(system_prompt: str) -> str:
    """
    system_prompt already contains location, resume + roadmap details.
    """
    payload = {
        "model": "sonar-deep-research",
        "messages": [
            {
                "role": "system",
                "content": system_prompt
            },
            {
                "role": "user",
                "content": (
                    "Generate the market‑intelligence report exactly as instructed. "
                    "Return ONLY the final report in Markdown, starting with "
                    "`# Market Intelligence Report`."
                )
            }
        ],
        "max_tokens": 8000,
        "temperature": 0.3
    }

    logging.info("Calling Perplexity (job)…")
    try:
        r = requests.post(
            "https://api.perplexity.ai/chat/completions",
            headers=HEADERS,
            json=payload,
            timeout=(10, 480)   # 10 s connect timeout, 480 s read timeout
        )
        r.raise_for_status()
        content = r.json()['choices'][0]['message']['content']
        logging.info("Perplexity returned %d chars", len(content))
        return content
    except requests.exceptions.HTTPError as e:
        logging.error("Perplexity HTTP error: %s", e.response.text)
        raise
    except Exception:
        logging.exception("Perplexity call failed")
        raise
