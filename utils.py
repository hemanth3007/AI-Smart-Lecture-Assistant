import whisper
import random
import re
from transformers import pipeline
from sklearn.feature_extraction.text import TfidfVectorizer

# ---------------- LOAD MODELS ----------------

whisper_model = whisper.load_model("tiny")

summarizer = pipeline(
    "summarization",
    model="facebook/bart-large-cnn"
)

# ---------------- SPEECH TO TEXT ----------------

def speech_to_text(audio_path):
    try:
        result = whisper_model.transcribe(audio_path, fp16=False)
        return result.get("text", "").strip()
    except Exception as e:
        return f"Transcription failed: {str(e)}"

# ---------------- SUMMARIZATION ----------------

def summarize_text(text):
    if not text or "failed" in text.lower():
        return "No valid transcript available."

    summary = summarizer(
        text,
        max_length=200,
        min_length=60,
        do_sample=False
    )
    return summary[0]["summary_text"]

# ---------------- KEYWORDS ----------------

def extract_keywords(text, top_n=8):
    if not text:
        return []

    vectorizer = TfidfVectorizer(stop_words='english')
    X = vectorizer.fit_transform([text])
    scores = zip(vectorizer.get_feature_names_out(), X.toarray()[0])
    sorted_keywords = sorted(scores, key=lambda x: x[1], reverse=True)
    return [word for word, score in sorted_keywords[:top_n]]

# ---------------- INTERACTIVE QUIZ ----------------

def generate_quiz(text):
    sentences = re.split(r'\.|\n', text)
    sentences = [s.strip() for s in sentences if len(s.strip()) > 40]

    if len(sentences) < 5:
        sentences = sentences * 2

    quiz_data = []

    for i in range(5):
        sentence = sentences[i % len(sentences)]
        words = [w for w in sentence.split() if len(w) > 5]

        if len(words) < 4:
            continue

        correct = random.choice(words)
        question = sentence.replace(correct, "______")

        distractors = random.sample(words, min(3, len(words)))
        options = list(set([correct] + distractors))

        while len(options) < 4:
            options.append(random.choice(words))

        random.shuffle(options)

        quiz_data.append({
            "question": f"Q{i+1}. {question}?",
            "options": options[:4],
            "answer": correct
        })

    return quiz_data