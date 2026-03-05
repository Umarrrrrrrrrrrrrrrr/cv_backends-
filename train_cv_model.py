"""
Train CV grading model. Run once to generate logistic_model.pkl and vectorizer.pkl.
Requires Resume.csv in project root (or set RESUME_CSV path).

Usage:
  python train_cv_model.py

Output:
  ml/models/logistic_model.pkl
  ml/models/vectorizer.pkl
"""
import re
import pickle
from pathlib import Path

import numpy as np
import pandas as pd
from sklearn.model_selection import train_test_split
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.linear_model import LogisticRegression
from scipy.sparse import hstack

# Project root
ROOT = Path(__file__).resolve().parent
MODEL_DIR = ROOT / "ml" / "models"
MODEL_DIR.mkdir(parents=True, exist_ok=True)


def main():
    import nltk
    nltk.download("stopwords", quiet=True)
    from nltk.corpus import stopwords

    # Load CSV
    csv_path = Path(__file__).parent / "Resume.csv"
    if not csv_path.exists():
        csv_path = Path(__file__).parent / "Resume.csv"
    if not csv_path.exists():
        print("ERROR: Resume.csv not found. Place it in the project root.")
        return 1

    df = pd.read_csv(csv_path, engine="python", on_bad_lines="skip")
    df.columns = df.columns.str.strip().str.lower()

    if "resume_str" in df.columns:
        df["resume_text"] = df["resume_str"]
    elif "resume_html" in df.columns:
        from bs4 import BeautifulSoup
        def extract(html):
            if pd.isna(html):
                return ""
            return BeautifulSoup(str(html), "html.parser").get_text(separator=" ", strip=True)
        df["resume_text"] = df["resume_html"].apply(extract)
    else:
        print("ERROR: CSV must have 'resume_str' or 'resume_html' column")
        return 1

    def clean_text(text):
        text = str(text).lower()
        text = re.sub(r"[^a-z0-9\s]", "", text)
        text = re.sub(r"\s+", " ", text).strip()
        text = " ".join(w for w in text.split() if w not in stopwords.words("english"))
        return text

    def extract_hand_features(text):
        if not text or len(str(text).strip()) < 10:
            return np.array([[0, 0, 0, 0]])
        t = str(text).lower()
        wc = min(1.0, len(t.split()) / 500)
        kw = ["managed", "developed", "led", "implemented", "achieved", "improved", "created", "analyzed"]
        kw_count = min(1.0, sum(1 for k in kw if k in t) / 6)
        sec = ["experience", "education", "skills", "summary"]
        sec_count = sum(1 for s in sec if s in t) / 4
        quant = len(re.findall(r"\d+%|\d+\s*(?:years?|months?)\b", t))
        quant_norm = min(1.0, quant / 5)
        return np.array([[wc, kw_count, sec_count, quant_norm]])

    df["cleaned_text"] = df["resume_text"].apply(clean_text)

    def generate_score(text):
        if not text or len(text.strip()) < 50:
            return 1
        t = text.lower()
        words = t.split()
        wc = len(words)
        if wc < 80:
            ws = 1
        elif wc < 150:
            ws = 2
        elif wc < 220:
            ws = 4
        elif wc < 300:
            ws = 6
        elif 300 <= wc <= 800:
            ws = 9
        elif wc <= 1100:
            ws = 8
        else:
            ws = 5
        kw = ["managed", "developed", "designed", "led", "implemented", "achieved", "improved", "created", "analyzed"]
        kw_score = min(10, sum(1 for k in kw if k in t) * 0.8)
        skill = ["python", "java", "sql", "aws", "docker", "linux", "git", "api", "database", "cloud"]
        tech = min(10, sum(1 for s in skill if s in t) * 0.7)
        req = ["experience", "education", "skills"]
        opt = ["projects", "certification", "summary", "objective"]
        struct = min(10, sum(1 for s in req if s in t) * 2.5 + sum(1 for s in opt if s in t) * 0.5)
        quant = len(re.findall(r"\d+%|\d+\s*(?:x|times|years?|months?)\b", t))
        qs = min(10, quant * 2) if quant else 3
        penalty = min(3, len(re.findall(r"(.)\1{4,}", t)) + len(re.findall(r"[@#$%^&*_=+<>]", t)) // 10)
        score = ws * 0.2 + kw_score * 0.25 + tech * 0.2 + struct * 0.25 + qs * 0.1 - penalty
        return max(1, min(10, round(score)))

    df["score_class"] = df["cleaned_text"].apply(generate_score)
    X = df["cleaned_text"]
    y = df["score_class"]

    X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)

    vectorizer = TfidfVectorizer(
        max_features=8000,
        min_df=2,
        max_df=0.85,
        ngram_range=(1, 3),
        sublinear_tf=True,
        strip_accents="unicode",
    )
    X_train_tfidf = vectorizer.fit_transform(X_train)
    X_test_tfidf = vectorizer.transform(X_test)
    X_train_hand = np.vstack([extract_hand_features(t) for t in X_train])
    X_test_hand = np.vstack([extract_hand_features(t) for t in X_test])
    X_train_combined = hstack([X_train_tfidf, X_train_hand])
    X_test_combined = hstack([X_test_tfidf, X_test_hand])

    model = LogisticRegression(
        max_iter=2000,
        random_state=42,
        class_weight="balanced",
        C=1.0,
        solver="lbfgs",
        multi_class="multinomial",
    )
    model.fit(X_train_combined, y_train)

    from sklearn.metrics import accuracy_score
    acc = accuracy_score(y_test, model.predict(X_test_combined))
    print(f"Model accuracy: {acc:.4f}")

    with open(MODEL_DIR / "logistic_model.pkl", "wb") as f:
        pickle.dump(model, f)
    with open(MODEL_DIR / "vectorizer.pkl", "wb") as f:
        pickle.dump(vectorizer, f)

    print(f"\nSaved to {MODEL_DIR}/")
    print("  - logistic_model.pkl")
    print("  - vectorizer.pkl")
    return 0


if __name__ == "__main__":
    exit(main())
