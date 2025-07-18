# Goal-to-Market Autopilot 🚀

A streamlined Flask-based web app that generates **custom 5-year career roadmaps** and **personalized market intelligence reports** from your resume — then emails the report directly to you.

## 🔍 What It Does

1. **Resume Upload + Goal Input**: Users upload a resume and specify their 5-year career goal and location.
2. **Roadmap Generation (OpenAI)**: The app uses GPT to generate a hyper-personalized JSON roadmap with SMART quarterly goals.
3. **Market Intel Report (Perplexity)**: A background thread calls the Perplexity API to build a forensic market report tied to the user’s roadmap.
4. **Email Delivery**: The report is converted to HTML and emailed to the user.

---

## ⚙️ Technologies Used

| Layer        | Stack                                                                 |
|--------------|------------------------------------------------------------------------|
| **Backend**  | Flask, threading, Pydantic, dotenv, markdown, OpenAI & Perplexity APIs |
| **Frontend** | Vanilla JS, HTML5, CSS3 with blur/glass effects for modern UX          |
| **Email**    | Gmail SMTP + `smtplib` for rich HTML email delivery                    |

---

## 🧩 Code Structure

📁 backend/
├─ email_sender.py # Sends HTML emails via Gmail SMTP
├─ models.py # Pydantic models for input validation
├─ openai_client.py # Calls GPT (o3-mini) to build JSON roadmaps
├─ perplexity_client.py # Calls Perplexity API (sonar-deep-research)
├─ perplexity_prompt_builder.py # Builds market-intel prompt with JSON inputs
├─ prompt_builder.py # Builds OpenAI roadmap prompt with resume context
├─ resume_extractor.py # Parses PDF, DOCX, TXT resumes
└─ validators.py # Validates user input (goal, location format)

📁 static/
├─ css/style.css # UI styling (glassmorphic + responsive)
└─ js/script.js # Form validation + roadmap rendering

📁 templates/
└─ index.html # Upload UI

root/
├─ app.py # Main Flask app with OpenAI + Perplexity flow
├─ ui_test_app.py # Lightweight UI-only tester
├─ scrape_all_code.py # Dumps code and folder tree into one .txt file
├─ requirements.txt
├─ README.md # You’re here 😉



## 🧪 How to Run Locally

1. **Install dependencies**  
   ```bash
   pip install -r requirements.txt
Set up .env


OPENAI_API_KEY=your-key
PERPLEXITY_API_KEY=your-key
EMAIL_SENDER=your-gmail@gmail.com
GMAIL_APP_PASSWORD=your-app-password

Run Flask
