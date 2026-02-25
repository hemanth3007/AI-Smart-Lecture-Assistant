import random
import re
from transformers import pipeline
from sklearn.feature_extraction.text import TfidfVectorizer

# ---------------- SPEECH RECOGNITION (CLOUD SAFE) ----------------

speech_recognizer = pipeline(
    "automatic-speech-recognition",
    model="openai/whisper-tiny"
)

# ---------------- SUMMARIZER ----------------

summarizer = pipeline(
    "summarization",
    model="facebook/bart-large-cnn"
)

# ---------------- FUNCTIONS ----------------

def speech_to_text(audio_path):
    try:
        result = speech_recognizer(audio_path)
        return result["text"]
    except Exception as e:
        return f"Transcription failed: {str(e)}"

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

def extract_keywords(text, top_n=8):
    if not text:
        return []

    vectorizer = TfidfVectorizer(stop_words='english')
    X = vectorizer.fit_transform([text])
    scores = zip(vectorizer.get_feature_names_out(), X.toarray()[0])
    sorted_keywords = sorted(scores, key=lambda x: x[1], reverse=True)
    return [word for word, score in sorted_keywords[:top_n]]

# ---------------- QUIZ GENERATOR ----------------

def generate_quiz(text):
    sentences = re.split(r'\.|\n', text)
    sentences = [s.strip() for s in sentences if len(s.strip()) > 30]

    if not sentences:
        return []

    quiz_data = []
    question_number = 1

    while len(quiz_data) < 5:

        sentence = random.choice(sentences)

        words = [
            w.strip(",.?!").lower()
            for w in sentence.split()
            if len(w.strip(",.?!")) > 5
        ]

        # If not enough words, skip and try another sentence
        if len(words) < 4:
            continue

        correct = random.choice(words)

        # Replace only first occurrence
        question = sentence.replace(correct, "______", 1)

        distractors = random.sample(words, min(3, len(words)))
        options = list(set([correct] + distractors))

        while len(options) < 4:
            options.append(random.choice(words))

        random.shuffle(options)

        quiz_data.append({
            "question": f"Q{question_number}. {question}?",
            "options": options[:4],
            "answer": correct
        })

        question_number += 1

    return quiz_data