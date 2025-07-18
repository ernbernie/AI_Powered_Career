# Goal-to-Market Autopilot 🚀

A streamlined Flask web app that generates custom 5-year career roadmaps and personalized market intelligence reports from your resume — then emails the report directly to you.

---

## 🔍 What It Does

- **Resume Upload + Goal Input:**  
  Users upload a resume and specify their 5-year career goal and location.
- **Roadmap Generation (OpenAI):**  
  The app uses GPT (o3-mini) to generate a hyper-personalized JSON roadmap with SMART quarterly goals.
- **Market Intel Report (Perplexity):**  
  A background thread calls the Perplexity API (sonar-deep-research) to build a forensic market report tied to the user’s roadmap.
- **Email Delivery:**  
  The report is converted to HTML and emailed to the user.

---

## ⚙️ Technologies Used

| Layer     | Stack                                                                 |
|-----------|-----------------------------------------------------------------------|
| Backend   | Flask, threading, Pydantic, dotenv, markdown, OpenAI & Perplexity APIs|
| Frontend  | Vanilla JS, HTML5, CSS3 (glassmorphic/blur modern UX)                 |
| Email     | Gmail SMTP + smtplib for rich HTML email delivery                     |

---

## 🧩 Code Structure

```
backend/
  ├─ email_sender.py              # Sends HTML emails via Gmail SMTP
  ├─ models.py                    # Pydantic models for input validation
  ├─ openai_client.py             # Calls GPT (o3-mini) to build JSON roadmaps
  ├─ perplexity_client.py         # Calls Perplexity API (sonar-deep-research)
  ├─ perplexity_prompt_builder.py # Builds market-intel prompt with JSON inputs
  ├─ prompt_builder.py            # Builds OpenAI roadmap prompt with resume context
  ├─ resume_extractor.py          # Parses PDF, DOCX, TXT resumes
  └─ validators.py                # Validates user input (goal, location format)

static/
  ├─ css/style.css                # UI styling (glassmorphic + responsive)
  └─ js/script.js                 # Form validation + roadmap rendering

templates/
  └─ index.html                   # Upload UI

root/
  ├─ app.py                       # Main Flask app with OpenAI + Perplexity flow
  ├─ requirements.txt
  ├─ README.md                    # You’re here 😉
```

---

## 🧪 How to Run Locally

1. **Install dependencies**
   ```sh
   pip install -r requirements.txt
   ```

2. **Set up `.env`**
   ```
   OPENAI_API_KEY=your-key
   PERPLEXITY_API_KEY=your-key
   EMAIL_SENDER=your-gmail@gmail.com
   GMAIL_APP_PASSWORD=your-app-password
   ```

3. **Run the app**
   ```sh
   waitress-serve --host 127.0.0.1 --port=5000 app:app
   ```
   *(Or use `flask run` for development only)*

4. **Open your browser:**  
   Go to [http://127.0.0.1:5000](http://127.0.0.1:5000)

---

## 🛡️ Security & Usage

- **Secrets:** Never commit your `.env` file or any API keys.
- **Daily Limit:** The app enforces a global daily usage limit (10 runs/day, resets at midnight MST).
- **Email:** Uses Gmail SMTP for delivery; you must use an [App Password](https://support.google.com/accounts/answer/185833).

---

## 📣 Feedback & Contributions

This is a beta prototype!  
If you have feedback, ideas, or want to contribute, open an issue or pull request.

---

## 📄 License

MIT License (or your preferred license)
