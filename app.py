# Full updated app.py - replace the entire content with this
from flask import Flask, render_template, request, jsonify
import logging
import sys
import threading
import markdown # For converting the report to HTML for the email
from backend.models import UserGoalInput
from backend.validators import validate_goal, validate_location
from backend.resume_extractor import extract_text_from_file
from backend.prompt_builder import build_career_roadmap_prompt
from backend.openai_client import call_openai_gpt4
from backend.perplexity_prompt_builder import build_perplexity_prompt
from backend.perplexity_client import call_perplexity_api
# --- NEW IMPORT ---
from backend.email_sender import send_email
# --- END NEW IMPORT ---
import tempfile
import os
from dotenv import load_dotenv
import re
import json

load_dotenv()
logging.basicConfig(level=logging.INFO, format='%(asctime)s %(levelname)s %(message)s')

app = Flask(__name__, template_folder='templates', static_folder='static')

def run_perplexity_and_email_in_background(roadmap_json, resume_snippet, location, user_email):
    """
    This function runs in a separate thread. It builds the prompt, calls the 
    Perplexity API, and then emails the resulting report.
    """
    with app.app_context():
        try:
            logging.info("BACKGROUND THREAD: Building Perplexity prompt...")
            perplexity_prompt = build_perplexity_prompt(
                roadmap_json=roadmap_json,
                resume_snippet=resume_snippet,
                location=location
            )
            
            logging.info("BACKGROUND THREAD: Calling Perplexity API...")
            market_report_md = call_perplexity_api(perplexity_prompt)

            if "Error" not in market_report_md:
                logging.info("BACKGROUND THREAD: Converting report to HTML and sending email...")
                report_html = markdown.markdown(market_report_md)
                email_subject = "Your Custom Career Intelligence Report is Ready!"
                send_email(user_email, email_subject, report_html)
            else:
                logging.error(f"BACKGROUND THREAD: Perplexity returned an error, not sending email. Report content: {market_report_md}")

            print("\n--- [BACKGROUND TASK COMPLETE] ---")
            print("--- MARKET INTELLIGENCE REPORT FROM PERPLEXITY ---\n")
            print(market_report_md)
            print("\n--- END OF REPORT ---\n")

        except Exception as e:
            logging.error(f"BACKGROUND THREAD FAILED: {e}")

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/generate_prompt', methods=['POST'])
def generate_prompt():
    logging.info("Processing /generate_prompt request")
    try:
        goal = request.form.get('goal')
        location = request.form.get('location')
        user_email = request.form.get('email') # Get email from form
        resume_file = request.files.get('resume')

        if not all([goal, location, user_email]):
            return jsonify({'error': 'Goal, location, and email are required'}), 400

        user_input = UserGoalInput(five_year_goal=goal, location=location)
        goal = user_input.five_year_goal
        location = user_input.location

        resume_text = None
        if resume_file:
            allowed_extensions = {'pdf', 'docx', 'txt'}
            if resume_file.filename.split('.')[-1].lower() not in allowed_extensions:
                return jsonify({'error': 'Invalid file type'}), 400
            if len(resume_file.read()) > 500 * 1024:
                return jsonify({'error': 'Resume too large (max 500KB)'}), 400
            resume_file.seek(0)
            ext = '.' + resume_file.filename.split('.')[-1].lower()
            with tempfile.NamedTemporaryFile(delete=False, suffix=ext) as tmp:
                resume_file.save(tmp.name)
                resume_text = extract_text_from_file(tmp.name)
            os.unlink(tmp.name)
            if not resume_text:
                return jsonify({'error': 'Failed to extract text from resume'}), 400
            if len(resume_text) > 10000:
                return jsonify({'error': 'Resume too long (max ~2 pages)'}), 400
        
        resume_snippet = resume_text[:3000] if resume_text else ""

        openai_prompt = build_career_roadmap_prompt(goal, location, resume_snippet)
        openai_response = call_openai_gpt4(openai_prompt)

        clean_response = re.sub(r"^```(?:json)?\s*|```$", "", openai_response.strip(), flags=re.MULTILINE)
        try:
            roadmap_obj = json.loads(clean_response)
            roadmap_json = json.dumps(roadmap_obj, indent=2)
        except json.JSONDecodeError as e:
            logging.error(f"Failed to parse OpenAI response as JSON: {e}")
            return jsonify({'error': "OpenAI response wasn't valid JSON"}), 400

        # Start the background task for Perplexity and Emailing
        logging.info("Starting background thread for Perplexity and Email task.")
        background_task = threading.Thread(
            target=run_perplexity_and_email_in_background,
            args=(roadmap_json, resume_snippet, location, user_email)
        )
        background_task.start()

        logging.info("Returning roadmap to frontend immediately.")
        return jsonify({'roadmap': roadmap_json})

    except Exception as e:
        logging.error(f"Top-level error in /generate_prompt: {e}")
        return jsonify({'error': 'A critical server error occurred.'}), 500

if __name__ == '__main__':
    app.run(debug=True)
