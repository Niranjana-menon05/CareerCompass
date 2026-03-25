# Career Compass — Setup Guide

## Folder Structure
```
CareerCompass/
├── app.py                  ← Flask app (run this)
├── auth.py                 ← Login / register / SQLite
├── chatbot.py              ← Groq chatbot
├── profile_builder.py      ← Resume pipeline orchestrator
├── resume_parser.py        ← PDF text extraction
├── text_cleaner.py         ← Text normalisation
├── extractor.py            ← NLP info extraction
├── skill_db.py             ← Skill vocabulary
├── career_matcher.py       ← O*NET career scoring
├── career_recovery.py      ← Gap analysis & roadmap
├── requirements.txt
├── datasets/               ← O*NET JSON files (keep as-is)
├── static/images/          ← logo-transparent.png goes here
└── templates/              ← HTML pages
    ├── index.html          ← Landing page (your Canva UI)
    ├── login.html          ← Login / Register
    └── dashboard.html      ← Main app + chatbot widget
```

## Setup Steps

### 1. Install dependencies
```bash
pip install flask groq pdfplumber spacy
python -m spacy download en_core_web_sm
```

### 2. Add your Groq API key
Open `chatbot.py` and replace:
```python
GROQ_API_KEY = "YOUR_GROQ_API_KEY_HERE"
```
Get a free key at https://console.groq.com

### 3. Run
```bash
cd CareerCompass
python app.py
```
Then open http://localhost:5000

## User Flow
1. Landing page → click "Get Started" or "Sign Up / Login"
2. Register a new account or log in
3. Upload a PDF resume → system analyses it automatically
4. View Career Matches tab
5. Run Gap Analysis on any target career
6. Chat with the AI at any time using the 💬 button (bottom-right)

## Notes
- `users.db` is created automatically on first run (SQLite)
- Each user's profile is saved — they don't need to re-upload every session
- The temp PDF file is deleted immediately after parsing (no residual files)
- Groq's `llama3-8b-8192` model is free-tier and very fast
