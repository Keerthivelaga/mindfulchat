# 💜 MindfulChat — Mental Wellness Chatbot

A compassionate AI-powered mental wellness chatbot built with Streamlit, designed to provide emotional support, detect distress, and alert emergency contacts when needed.

---

## ✨ Features

- 💬 **AI Chat** — Powered by Google Gemini 1.5 Flash for empathetic, context-aware conversations
- 🧠 **Smart NLP** — Detects 7 distress levels from emergency to very positive
- 🆘 **Emergency Alerts** — Automatically sends SMS (Fast2SMS) + Email to emergency contact on crisis detection
- 🫁 **Breathing Exercises** — Animated 4-7-8, Box, and Simple breathing guides
- 📝 **Journal** — Private mood-tagged journal entries
- 📊 **Mood Tracker** — 30-day mood history chart
- 📞 **Resources** — Indian helplines (iCall, AASRA, NIMHANS, Vandrevala)
- 🔐 **Auth** — Secure registration & login with bcrypt

---

## 🚀 Getting Started

### Prerequisites

- Python 3.11+
- A Google Gemini API key (free) — [Get it here](https://aistudio.google.com)
- A Fast2SMS account (for SMS alerts) — [fast2sms.com](https://fast2sms.com)
- A Gmail account with App Password enabled

### Installation

1. **Clone the repository**
   ```bash
   git clone https://github.com/YOURUSERNAME/mindfulchat.git
   cd mindfulchat
   ```

2. **Install dependencies**
   ```bash
   pip install streamlit bcrypt requests python-dotenv
   ```

3. **Set up secrets**

   Create `.streamlit/secrets.toml`:
   ```toml
   GEMINI_API_KEY = "your_gemini_api_key"
   FAST2SMS_API_KEY = "your_fast2sms_api_key"
   GMAIL_SENDER = "yourname@gmail.com"
   GMAIL_APP_PASSWORD = "your_app_password"
   ```

4. **Run the app**
   ```bash
   python -m streamlit run app.py
   ```

   Open [http://localhost:8501](http://localhost:8501) in your browser.


---

## 📁 Project Structure

```
mindfulchat/
├── app.py              # Main Streamlit app
├── llm_handler.py      # Gemini AI + Ollama + fallback responses
├── nlp_engine.py       # Keyword-based emotion & distress detection
├── alert_system.py     # Emergency SMS + Email alerts
├── config.py           # Constants, prompts, keywords
├── database.py         # SQLite database operations
├── auth.py             # User registration & login
└── .streamlit/
    └── config.toml     # Streamlit theme settings
```

---
## ⚠️ Disclaimer

MindfulChat is not a substitute for professional mental health care. If you or someone you know is in crisis, please contact a licensed mental health professional or call a helpline immediately.

---

## 🛠️ Built With

- [Streamlit](https://streamlit.io) — UI framework
- [Google Gemini](https://aistudio.google.com) — AI language model
- [Fast2SMS](https://fast2sms.com) — SMS alerts
- [SQLite](https://sqlite.org) — Local database
- [bcrypt](https://pypi.org/project/bcrypt/) — Password hashing
