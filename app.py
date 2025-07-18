import logging
import sys
import pytz
from datetime import datetime

logging.basicConfig(
    level=logging.INFO,  # or logging.DEBUG for more detail
    format='%(asctime)s %(levelname)s [%(threadName)s] %(message)s',
    handlers=[
        logging.StreamHandler(sys.stdout)
    ]
)

# app.py  –  beta flow with deferred e‑mail
from flask import Flask, render_template, request, jsonify
import threading, tempfile, os, re, json, uuid, markdown
from dotenv import load_dotenv

from backend.models import UserGoalInput
from backend.resume_extractor import extract_text_from_file
from backend.prompt_builder import build_career_roadmap_prompt
from backend.openai_client import call_openai_gpt4
from backend.perplexity_prompt_builder import build_perplexity_prompt
from backend.perplexity_client import call_perplexity_api
from backend.email_sender import send_email

load_dotenv()

app = Flask(__name__, template_folder='templates', static_folder='static')

# ------------------------------------------------------------------
# In‑memory cache: job_id ➜ {'status':running/ready/sent, 'html':str}
# In production swap for Redis with expiry.
# ------------------------------------------------------------------
report_store = {}
report_lock = threading.Lock()  # <-- ADD THIS LOCK

# ================================================================
# DAILY USAGE LIMIT (MST, persists in daily_usage.json)
# ================================================================
import json as _json
USAGE_LIMIT = 10
USAGE_FILE = 'daily_usage.json'
MST = pytz.timezone('America/Phoenix')

def check_and_increment_usage():
    now = datetime.now(MST)
    today = now.strftime('%Y-%m-%d')
    try:
        with open(USAGE_FILE, 'r') as f:
            data = _json.load(f)
    except (FileNotFoundError, _json.JSONDecodeError):
        data = {'date': today, 'count': 0}
    if data.get('date') == today:
        if data.get('count', 0) >= USAGE_LIMIT:
            return False
        data['count'] += 1
    else:
        data = {'date': today, 'count': 1}
    with open(USAGE_FILE, 'w') as f:
        _json.dump(data, f)
    return True

# ================================================================
# ROUTES
# ================================================================
@app.route('/')
def index():
    return render_template('index.html')

@app.route('/generate_prompt', methods=['POST'])
def generate_prompt():
    if not check_and_increment_usage():
        return jsonify({'error': 'Daily usage limit reached. Please try again tomorrow (resets at midnight MST).'}), 429
    try:
        goal      = request.form.get('goal')
        location  = request.form.get('location')
        resume_f  = request.files.get('resume')
        if not all([goal, location, resume_f]):
            return jsonify({'error':'Resume, goal and location are required.'}), 400

        # -------- resume extraction ----------
        allowed = {'pdf','docx','txt'}
        if resume_f.filename.split('.')[-1].lower() not in allowed:
            return jsonify({'error':'Invalid resume type.'}), 400
        if len(resume_f.read()) > 500*1024:
            return jsonify({'error':'Resume too large (500 KB).'}), 400
        resume_f.seek(0)
        ext = '.'+resume_f.filename.split('.')[-1].lower()
        with tempfile.NamedTemporaryFile(delete=False, suffix=ext) as tmp:
            resume_f.save(tmp.name)
            resume_txt = extract_text_from_file(tmp.name)
        os.unlink(tmp.name)
        if not resume_txt:
            return jsonify({'error':'Failed to read resume.'}), 400
        if len(resume_txt) > 10000:
            return jsonify({'error':'Resume >~2 pages.'}), 400
        resume_snip = resume_txt[:3000]

        # -------- OpenAI roadmap ----------
        oa_prompt   = build_career_roadmap_prompt(goal, location, resume_snip)
        oa_response = call_openai_gpt4(oa_prompt)
        clean_json  = re.sub(r"^```(?:json)?\s*|```$", "", oa_response.strip(), flags=re.MULTILINE)
        roadmap_obj = json.loads(clean_json)
        roadmap_json = json.dumps(roadmap_obj, indent=2)

        # -------- enqueue Perplexity ----------
        job_id = str(uuid.uuid4())
        with report_lock:
            report_store[job_id] = {'status':'running', 'html':None}
        threading.Thread(
            target=run_perplexity_only,
            args=(job_id, roadmap_json, resume_snip, location),
            daemon=True,
            name=f"PerplexityJob-{job_id[:8]}"
        ).start()

        return jsonify({'roadmap': roadmap_json, 'job_id': job_id})
    except Exception as e:
        logging.exception('Error in /generate_prompt')
        return jsonify({'error':'Server error.'}), 500

@app.route('/report_status')
def report_status():
    job_id = request.args.get('id')
    with report_lock:
        entry  = report_store.get(job_id)
    if not entry:
        return jsonify({'error':'Unknown id'}), 404
    return jsonify({'status': entry['status']})

@app.route('/debug/jobs')
def debug_jobs():
    """Debug endpoint to see all current jobs"""
    with report_lock:
        jobs = {job_id: {'status': entry['status']} for job_id, entry in report_store.items()}
        total_jobs = len(report_store)
    return jsonify({'total_jobs': total_jobs, 'jobs': jobs})

@app.route('/send_report', methods=['POST'])
def send_report():
    data = request.get_json(silent=True) or {}
    job_id  = data.get('id')
    email   = data.get('email')
    with report_lock:
        entry = report_store.get(job_id)
        if not entry or entry['status'] != 'ready':
            return jsonify({'error':'Report not ready.'}), 400
        try:
            send_email(email, 'Your Custom Career Intelligence Report', entry['html'])
            entry['status'] = 'sent'
            return jsonify({'status':'sent'})
        except Exception as e:
            logging.exception('send_email failed')
            return jsonify({'error':'Failed to email report.'}), 500

# ================================================================
# BACKGROUND WORKER
# ================================================================
def run_perplexity_only(job_id, roadmap_json, resume_snip, location):
    logging.info(f'Starting Perplexity job {job_id}...')
    try:
        logging.info(f'Building Perplexity prompt for job {job_id}...')
        prompt = build_perplexity_prompt(roadmap_json, resume_snip, location)
        logging.info(f'Calling Perplexity API for job {job_id}...')
        md = call_perplexity_api(prompt)
        logging.info(f'Converting Markdown to HTML for job {job_id}...')
        html = markdown.markdown(md)
        with report_lock:
            report_store[job_id] = {'status':'ready', 'html': html}
        logging.info(f'Perplexity job {job_id} finished successfully.')
    except Exception as e:
        logging.exception(f'Perplexity thread failed for job {job_id}')
        with report_lock:
            report_store[job_id] = {'status':'error', 'html': None}
        logging.info(f'Updated job {job_id} status to error')

# ================================================================
if __name__ == '__main__':
    # Only use Flask dev server for debugging; use waitress for production
    app.run(debug=True, use_reloader=False)
