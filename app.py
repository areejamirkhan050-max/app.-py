"""
AamFahm AI - Legal Document Simplifier for Pakistan
Upload any legal PDF -> Get a simplified Roman Urdu breakdown + Urdu audio.

Run locally:
    streamlit run app.py

Requires a GROQ_API_KEY (free at https://console.groq.com/keys)
Set it via environment variable, a .env file, or Streamlit secrets.
"""

import os
import io
import tempfile

import streamlit as st
from PyPDF2 import PdfReader
from gtts import gTTS
from groq import Groq

# ---------------------------------------------------------------------------
# CONFIG
# ---------------------------------------------------------------------------

st.set_page_config(
    page_title="AamFahm AI",
    page_icon="📜",
    layout="centered",
)

MODEL_NAME = "llama-3.3-70b-versatile"

SYSTEM_PROMPT = """Tum ek expert Pakistani legal assistant ho jo complex legal aur official 
documents ko aam logon (jinki legal English samajh kamzor hai) ke liye Roman Urdu mein 
simplify karte ho. Tumhara tone dosti wala, aasaan aur clear hona chahiye — jaise koi 
samajhdar dost samjha raha ho, lawyer jaisi mushkil zabaan bilkul nahi.

Tumhe document ka text diya jayega. Tumhein iska Roman Urdu breakdown EXACTLY neeche di gayi 
teen headings ke sath dena hai, aur kuch nahi likhna:

### Asaan Khulasa
(2-4 sentences mein document ka overall matlab, simple Roman Urdu mein)

### Aham Shartain
(Bullet points mein — important clauses, dates, deadlines, amounts, penalties, obligations. 
Har point chota aur clear ho. Agar koi specific date ya deadline document mein ho to zaroor 
highlight karo.)

### Aap Ko Kya Karna Hai
(Bullet points mein — user ko exactly kya action lena hai, kis tareekh tak, kis se contact 
karna hai, agar kuch sign/submit/pay karna hai to wo. Practical aur actionable hona chahiye.)

Sirf Roman Urdu mein likho (English alphabet mein Urdu jaisi zabaan, jaise "Aapko yeh karna 
hoga"). Kabhi bhi legal jargon repeat mat karo bina explain kiye. Agar document mein koi 
cheez unclear ho to wo bhi bata do ke "yeh clear nahi hai, lawyer se confirm karein"."""


# ---------------------------------------------------------------------------
# HELPERS
# ---------------------------------------------------------------------------

def get_api_key() -> str:
    """Fetch Groq API key from secrets or environment."""
    key = os.environ.get("GROQ_API_KEY", "")
    if not key:
        try:
            key = st.secrets.get("GROQ_API_KEY", "")
        except Exception:
            pass
    return key


def extract_text_from_pdf(uploaded_file) -> str:
    """Extract raw text from an uploaded PDF file."""
    reader = PdfReader(uploaded_file)
    text_chunks = []
    for page in reader.pages:
        page_text = page.extract_text() or ""
        text_chunks.append(page_text)
    return "\n".join(text_chunks).strip()


def simplify_with_llm(document_text: str, api_key: str) -> str:
    """Send the extracted text to the LLM and get back a structured Roman Urdu breakdown."""
    client = Groq(api_key=api_key)

    # Guard against extremely long documents - truncate to keep within context limits
    max_chars = 15000
    trimmed_text = document_text[:max_chars]

    response = client.chat.completions.create(
        model=MODEL_NAME,
        messages=[
            {"role": "system", "content": SYSTEM_PROMPT},
            {"role": "user", "content": f"Yeh document ka text hai:\n\n{trimmed_text}"},
        ],
        temperature=0.3,
        max_tokens=1200,
    )
    return response.choices[0].message.content.strip()


def text_to_speech(text: str) -> bytes:
    """Convert Roman Urdu / Urdu text to speech audio bytes using gTTS."""
    # gTTS with lang="ur" reads Urdu script best; for Roman Urdu text it still
    # produces reasonably understandable Urdu-accented speech.
    tts = gTTS(text=text, lang="ur")
    buf = io.BytesIO()
    tts.write_to_fp(buf)
    buf.seek(0)
    return buf.read()


def strip_markdown_for_audio(markdown_text: str) -> str:
    """Clean markdown symbols so TTS doesn't read out '###' or '-' etc."""
    lines = []
    for line in markdown_text.splitlines():
        clean = line.replace("###", "").replace("**", "").replace("*", "").replace("- ", "")
        lines.append(clean.strip())
    return " ".join([l for l in lines if l])


# ---------------------------------------------------------------------------
# UI
# ---------------------------------------------------------------------------

st.markdown(
    """
    <style>
    .main-title {
        font-size: 2.2rem;
        font-weight: 800;
        margin-bottom: 0;
    }
    .subtitle {
        color: #555;
        font-size: 1.05rem;
        margin-top: 0.2rem;
        margin-bottom: 1.5rem;
    }
    .stButton>button {
        background-color: #0F9D58;
        color: white;
        font-weight: 600;
        border-radius: 8px;
        padding: 0.6rem 1.2rem;
    }
    </style>
    """,
    unsafe_allow_html=True,
)

st.markdown('<p class="main-title">📜 AamFahm AI</p>', unsafe_allow_html=True)
st.markdown(
    '<p class="subtitle">Apna legal document upload karein — Roman Urdu mein aasaan '
    'khulasa aur Urdu audio turant paayein.</p>',
    unsafe_allow_html=True,
)

api_key = get_api_key()
if not api_key:
    st.warning(
        "⚠️ GROQ_API_KEY set nahi hai. Terminal mein set karein:\n\n"
        "`export GROQ_API_KEY=your_key_here` (Mac/Linux) ya\n"
        "`setx GROQ_API_KEY your_key_here` (Windows)\n\n"
        "Free key yahan se milegi: https://console.groq.com/keys"
    )

uploaded_file = st.file_uploader("Apni PDF file yahan upload karein", type=["pdf"])

if uploaded_file is not None:
    with st.expander("📄 File details"):
        st.write(f"**File name:** {uploaded_file.name}")
        st.write(f"**Size:** {round(uploaded_file.size / 1024, 1)} KB")

    if st.button("🔍 Document Samjhayein (Simplify)", disabled=not api_key):
        with st.spinner("Document parh raha hoon aur Roman Urdu mein samjha raha hoon..."):
            try:
                raw_text = extract_text_from_pdf(uploaded_file)

                if not raw_text or len(raw_text.strip()) < 20:
                    st.error(
                        "❌ Is PDF se text extract nahi ho saka. Ho sakta hai yeh scanned "
                        "image PDF ho — is version mein sirf text-based PDFs support hoti hain."
                    )
                else:
                    simplified = simplify_with_llm(raw_text, api_key)
                    st.session_state["simplified_output"] = simplified
                    st.session_state["audio_ready"] = False

            except Exception as e:
                st.error(f"❌ Kuch ghalat ho gaya: {e}")

if "simplified_output" in st.session_state:
    st.markdown("---")
    st.markdown(st.session_state["simplified_output"])

    st.markdown("---")
    col1, col2 = st.columns([1, 3])
    with col1:
        generate_audio = st.button("🔊 Audio Sunein")

    if generate_audio:
        with st.spinner("Audio taiyar ho raha hai..."):
            try:
                clean_text = strip_markdown_for_audio(st.session_state["simplified_output"])
                audio_bytes = text_to_speech(clean_text)
                st.session_state["audio_bytes"] = audio_bytes
                st.session_state["audio_ready"] = True
            except Exception as e:
                st.error(f"❌ Audio generate nahi ho saka: {e}")

    if st.session_state.get("audio_ready"):
        st.audio(st.session_state["audio_bytes"], format="audio/mp3")
        st.download_button(
            "⬇️ Audio Download Karein",
            data=st.session_state["audio_bytes"],
            file_name="aamfahm_summary.mp3",
            mime="audio/mp3",
        )

st.markdown("---")
st.caption(
    "AamFahm AI — Hackathon MVP. Yeh tool sirf general samajh ke liye hai, "
    "official legal advice ke liye hamesha qualified lawyer se rujoo karein."
)
