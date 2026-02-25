import streamlit as st
import tempfile
import os
import json

from utils import speech_to_text, summarize_text, generate_quiz, extract_keywords
from pdf_utils import create_pdf

st.set_page_config(page_title="AI Smart Lecture Assistant", layout="wide")

HISTORY_FILE = "history.json"

def load_history():
    if os.path.exists(HISTORY_FILE):
        with open(HISTORY_FILE, "r") as f:
            return json.load(f)
    return []

def save_history(history):
    with open(HISTORY_FILE, "w") as f:
        json.dump(history, f, indent=4)

# ---------------- SESSION INIT ----------------

if "history" not in st.session_state:
    st.session_state.history = load_history()

if "transcript" not in st.session_state:
    st.session_state.transcript = None

if "summary" not in st.session_state:
    st.session_state.summary = None

if "keywords" not in st.session_state:
    st.session_state.keywords = None

if "quiz" not in st.session_state:
    st.session_state.quiz = None

if "score" not in st.session_state:
    st.session_state.score = None

# ---------------- UI ----------------

st.title("🎓 AI Smart Lecture Assistant")
st.write("Speech-to-Notes | Summarization | Interactive Quiz")
st.write("---")

audio_file = st.file_uploader("Upload Lecture Audio (.mp3/.wav)", type=["mp3", "wav"])

# -------- PROCESS AUDIO ONLY ONCE --------

if audio_file is not None and st.session_state.transcript is None:

    with st.spinner("Processing Audio..."):

        with tempfile.NamedTemporaryFile(delete=False) as tmp:
            tmp.write(audio_file.read())
            audio_path = tmp.name

        transcript = speech_to_text(audio_path)
        summary = summarize_text(transcript)
        keywords = extract_keywords(transcript)

        os.remove(audio_path)

        st.session_state.transcript = transcript
        st.session_state.summary = summary
        st.session_state.keywords = keywords

    st.success("Processing Complete ✅")

# -------- DISPLAY RESULTS --------

if st.session_state.transcript:

    col1, col2 = st.columns(2)

    with col1:
        st.subheader("📜 Transcript")
        st.write(st.session_state.transcript)

    with col2:
        st.subheader("📚 Summary")
        st.write(st.session_state.summary)

    st.subheader("🔑 Key Concepts")
    st.write(", ".join(st.session_state.keywords))

    st.write("---")
    st.subheader("🎯 Interactive Quiz")

    if st.button("Generate Quiz"):
        st.session_state.quiz = generate_quiz(st.session_state.summary)
        st.session_state.score = None

    if st.session_state.quiz:

        user_answers = []

        for idx, q in enumerate(st.session_state.quiz):
            st.write(q["question"])
            selected = st.radio(
                "Choose your answer:",
                q["options"],
                key=f"q_{idx}"
            )
            user_answers.append(selected)

        if st.button("Submit Quiz"):
            score = 0

            st.write("### 📊 Results")

            for i, q in enumerate(st.session_state.quiz):
                if user_answers[i] == q["answer"]:
                    st.success(f"Q{i+1}: Correct ✅")
                    score += 1
                else:
                    st.error(f"Q{i+1}: Wrong ❌ | Correct Answer: {q['answer']}")

            st.info(f"Final Score: {score} / 5")

            st.session_state.score = score

            # Save history
            new_session = {
                "summary": st.session_state.summary,
                "score": score
            }

            st.session_state.history.append(new_session)
            save_history(st.session_state.history)

            # Generate PDF
            os.makedirs("Notes", exist_ok=True)
            pdf_path = os.path.join("Notes", "Lecture_Notes.pdf")
            create_pdf(
                pdf_path,
                st.session_state.transcript,
                st.session_state.summary,
                score
            )

            with open(pdf_path, "rb") as f:
                st.download_button(
                    label="📥 Download Notes as PDF",
                    data=f,
                    file_name="Lecture_Notes.pdf",
                    mime="application/pdf"
                )

# -------- HISTORY --------

st.write("---")
st.subheader("🕘 Previous Sessions")

if st.session_state.history:
    for i in range(len(st.session_state.history)-1, -1, -1):
        session = st.session_state.history[i]

        with st.expander(f"Session {i+1}"):
            st.write("### Summary")
            st.write(session["summary"])
            st.write(f"### Score: {session['score']} / 5")

            if st.button(f"Delete Session {i+1}", key=f"delete_{i}"):
                st.session_state.history.pop(i)
                save_history(st.session_state.history)
                st.rerun()
else:
    st.write("No previous sessions yet.")