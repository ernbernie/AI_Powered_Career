from flask import Flask, render_template, request, jsonify
from backend.resume_extractor import extract_text_from_file
from backend.prompt_builder import build_career_roadmap_prompt
from backend.validators import validate_goal, validate_location
import tempfile
import os
import logging

logging.basicConfig(level=logging.INFO)  # Consider DEBUG for more details if needed

app = Flask(__name__)

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/generate_prompt', methods=['POST'])
def generate_prompt():
    try:
        goal = request.form['goal']
        location = request.form['location']
        resume_file = request.files['resume']

        if not resume_file:
            return jsonify({'error': 'No resume uploaded'}), 400

        # Basic file validation (type and size for ~2 pages)
        allowed_extensions = {'pdf', 'docx', 'txt'}
        if resume_file.filename.split('.')[-1].lower() not in allowed_extensions:
            return jsonify({'error': 'Invalid file type (PDF, DOCX, TXT only)'}), 400

        # Temp save + extract (add original extension for format detection)
        ext = '.' + resume_file.filename.split('.')[-1].lower()
        with tempfile.NamedTemporaryFile(delete=False, suffix=ext) as tmp:
            resume_file.save(tmp.name)
            resume_text = extract_text_from_file(tmp.name)
        os.unlink(tmp.name)

        if not resume_text:
            return jsonify({'error': 'Failed to extract text from resume'}), 400

        # Enforce 2-page limit via text length (~10k chars max)
        if len(resume_text) > 10000:
            return jsonify({'error': 'Resume too long (max ~2 pages)'}), 400

        # Validate goal and location
        goal = validate_goal(goal)
        location = validate_location(location)

        # Build prompt
        prompt = build_career_roadmap_prompt(goal, location, resume_text)

        return jsonify({'prompt': prompt})

    except ValueError as e:
        return jsonify({'error': str(e)}), 400
    except Exception as e:
        logging.error(f"Error: {e}")
        return jsonify({'error': 'Server error - please try again'}), 500

if __name__ == '__main__':
    app.run(debug=True)