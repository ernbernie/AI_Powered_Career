import logging
from pathlib import Path
from typing import Final

import pdfplumber
from docx import Document   # pip install python-docx

MIN_CHARS: Final[int] = 50   # treat anything shorter as “no resume”

def extract_text_from_file(path: str | Path) -> str:
    """
    Returns plaintext from PDF, DOCX, or TXT.
    If the file can’t be read or is too short, returns an empty string.
    """
    path = Path(path)
    logging.info("Extracting resume text from %s", path)

    try:
        match path.suffix.lower():
            case ".pdf":
                with pdfplumber.open(path) as pdf:
                    text = "\n".join(page.extract_text() or "" for page in pdf.pages)
            case ".docx":
                doc = Document(path)
                text = "\n".join(p.text for p in doc.paragraphs)
            case ".txt":
                text = path.read_text(encoding="utf-8")
            case _:
                logging.warning("Unsupported resume format: %s", path.suffix)
                return ""

        text = text.strip()
        if len(text) < MIN_CHARS:
            logging.warning("Resume text too short – treating as missing.")
            return ""

        logging.info("Resume extracted – %s characters", len(text))
        return text

    except Exception as exc:  # broad on purpose – we never want to crash the CLI
        logging.error("Failed to extract resume: %s", exc)
        return "" 