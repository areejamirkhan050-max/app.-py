# AamFahm AI 📜

**Legal documents ko Roman Urdu mein simplify karne wala AI assistant — Pakistani awaam ke liye.**

Upload any legal PDF (rent agreement, loan contract, court notice, government circular) and instantly get:
- **Asaan Khulasa** — a plain-language summary
- **Aham Shartain** — key clauses, dates, and obligations
- **Aap Ko Kya Karna Hai** — clear action steps
- 🔊 One-click Urdu audio playback of the summary

---

## Quick Start

### 1. Clone / unzip and enter the project folder
```bash
cd aamfahm_ai
```

### 2. (Recommended) Create a virtual environment
```bash
python -m venv venv
source venv/bin/activate      # Mac/Linux
venv\Scripts\activate         # Windows
```

### 3. Install dependencies
```bash
pip install -r requirements.txt
```

### 4. Get a free Groq API key
Sign up at **https://console.groq.com/keys** — it's free and takes 1 minute.

### 5. Set your API key

**Option A — Environment variable (fastest):**
```bash
export GROQ_API_KEY=your_key_here      # Mac/Linux
setx GROQ_API_KEY your_key_here        # Windows (restart terminal after)
```

**Option B — Streamlit secrets (recommended for deployment):**
Create a file at `.streamlit/secrets.toml`:
```toml
GROQ_API_KEY = "your_key_here"
```

### 6. Run the app
```bash
streamlit run app.py
```

The app will open at `http://localhost:8501`.

---

## Deploying for the Demo (Streamlit Community Cloud — free)

1. Push this folder to a GitHub repo.
2. Go to **https://share.streamlit.io** and sign in with GitHub.
3. Click "New app", select your repo and `app.py` as the entry point.
4. Under **Advanced settings → Secrets**, paste:
   ```toml
   GROQ_API_KEY = "your_key_here"
   ```
5. Deploy — you'll get a public link to demo live in front of judges.

---

## Project Structure
```
aamfahm_ai/
├── app.py              # Main Streamlit application
├── requirements.txt    # Python dependencies
├── .env.example         # Sample env file
└── README.md           # This file
```

## Tech Stack
| Layer            | Technology                          |
|-------------------|--------------------------------------|
| Frontend          | Streamlit                            |
| PDF Extraction    | PyPDF2                               |
| LLM               | Llama 3.3 70B via Groq API           |
| Text-to-Speech    | gTTS (Google Text-to-Speech, Urdu)   |

## Known Limitations (MVP)
- Only text-based PDFs are supported (scanned/image PDFs need OCR — future improvement).
- Very long documents are truncated to ~15,000 characters to fit LLM context limits.
- gTTS reads Roman Urdu with an Urdu-accented voice; it is not a true Roman Urdu phonetic reader.

## Roadmap / Future Improvements
- OCR support for scanned documents (e.g., via `pytesseract`)
- Multi-language support (Sindhi, Pashto, Punjabi)
- Clause-by-clause Q&A chat feature
- Higher quality TTS (e.g., ElevenLabs Urdu voices)

---

*Disclaimer: AamFahm AI provides simplified explanations for general understanding only and does not constitute legal advice. Always consult a qualified lawyer for official matters.*
