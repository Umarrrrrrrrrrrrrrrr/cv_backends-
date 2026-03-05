"""
CV/Resume grading and enhancement - uses model from model/ folder.
"""
import re
from pathlib import Path

# Model files are in Back_Back/model/
MODEL_DIR = Path(__file__).resolve().parent.parent / "model"
MODEL_PATH = MODEL_DIR / "logistic_model.pkl"
VECTORIZER_PATH = MODEL_DIR / "vectorizer.pkl"

_nltk_stopwords = None
_vectorizer = None
_model = None
_model_loaded = False


def _get_stopwords():
    global _nltk_stopwords
    if _nltk_stopwords is None:
        try:
            import nltk
            nltk.download("stopwords", quiet=True)
            from nltk.corpus import stopwords
            _nltk_stopwords = set(stopwords.words("english"))
        except Exception:
            _nltk_stopwords = set()
    return _nltk_stopwords


def clean_text(text):
    """Clean and preprocess resume text."""
    if not text or not str(text).strip():
        return ""
    text = str(text).lower()
    text = re.sub(r'[^a-z0-9\s]', '', text)
    text = re.sub(r'\s+', ' ', text).strip()
    stopwords_set = _get_stopwords()
    text = " ".join(w for w in text.split() if w not in stopwords_set)
    return text


def extract_hand_features(text):
    """Extract rule-based features for the model."""
    import numpy as np
    if not text or len(str(text).strip()) < 10:
        return np.array([[0, 0, 0, 0]])
    text_lower = str(text).lower()
    words = text_lower.split()
    wc = min(1.0, len(words) / 500)
    action_kw = ['managed', 'developed', 'led', 'implemented', 'achieved', 'improved', 'created', 'analyzed']
    kw_count = min(1.0, sum(1 for k in action_kw if k in text_lower) / 6)
    sections = ['experience', 'education', 'skills', 'summary']
    sec_count = sum(1 for s in sections if s in text_lower) / 4
    quant = len(re.findall(r'\d+%|\d+\s*(?:years?|months?)\b', text_lower))
    quant_norm = min(1.0, quant / 5)
    return np.array([[wc, kw_count, sec_count, quant_norm]])


def _load_model():
    """Load model and vectorizer from model/ folder."""
    global _model, _vectorizer, _model_loaded
    if _model_loaded:
        return _model is not None
    if not MODEL_PATH.exists() or not VECTORIZER_PATH.exists():
        return False
    try:
        import pickle
        with open(MODEL_PATH, "rb") as f:
            _model = pickle.load(f)
        with open(VECTORIZER_PATH, "rb") as f:
            _vectorizer = pickle.load(f)
        _model_loaded = True
        return True
    except Exception:
        _model = None
        _vectorizer = None
        return False


def _rule_based_score(text):
    """Rule-based scoring when ML model is not available."""
    if not text or len(text.strip()) < 50:
        return 1
    text_lower = text.lower()
    words = text.split()
    word_count = len(words)

    if word_count < 80:
        word_score = 1
    elif word_count < 150:
        word_score = 2
    elif word_count < 220:
        word_score = 4
    elif word_count < 300:
        word_score = 6
    elif 300 <= word_count <= 800:
        word_score = 9
    elif word_count <= 1100:
        word_score = 8
    else:
        word_score = 5

    professional_keywords = [
        'managed', 'developed', 'designed', 'led', 'implemented',
        'achieved', 'improved', 'created', 'analyzed', 'optimized',
        'coordinated', 'delivered', 'maintained', 'executed',
    ]
    keyword_hits = sum(1 for k in professional_keywords if k in text_lower)
    keyword_score = min(10, keyword_hits * 0.8)

    skill_terms = [
        'python', 'java', 'sql', 'aws', 'docker', 'kubernetes',
        'linux', 'git', 'api', 'database', 'cloud', 'ml', 'ai',
        'excel', 'analytics', 'project management'
    ]
    skill_hits = sum(1 for t in skill_terms if t in text_lower)
    tech_score = min(10, skill_hits * 0.7)

    required_sections = ['experience', 'education', 'skills']
    optional_sections = ['projects', 'certification', 'summary', 'objective', 'achievement']
    required_count = sum(1 for s in required_sections if s in text_lower)
    optional_count = sum(1 for s in optional_sections if s in text_lower)
    structure_score = min(10, (required_count * 2.5) + (optional_count * 0.5))

    quant_patterns = re.findall(r'\d+%|\d+\s*(?:x|times|years?|months?)\b', text_lower)
    quant_score = min(10, len(quant_patterns) * 2) if quant_patterns else 3

    repeated_chars = len(re.findall(r'(.)\1{4,}', text))
    symbol_noise = len(re.findall(r'[@#$%^&*_=+<>]', text))
    penalty = min(3, repeated_chars + (symbol_noise // 10))

    final_score = (
        word_score * 0.20 +
        keyword_score * 0.25 +
        tech_score * 0.20 +
        structure_score * 0.25 +
        quant_score * 0.10
    ) - penalty
    return max(1, min(10, round(final_score)))


def predict_professional_score(text):
    """Predict resume score 0-100."""
    clean = clean_text(text)
    if not clean:
        return 0

    if _load_model():
        from scipy.sparse import hstack
        vec_tfidf = _vectorizer.transform([clean])
        vec_hand = extract_hand_features(text)
        vec_combined = hstack([vec_tfidf, vec_hand])
        probs = _model.predict_proba(vec_combined)[0]
        classes = _model.classes_
        score_0_100 = sum(p * c * 10 for p, c in zip(probs, classes))
        return round(score_0_100)
    else:
        rule_score = _rule_based_score(text)
        return min(100, rule_score * 10)


def grade_resume(text):
    """Return (score_0_100, grade_level, needs_enhancement)."""
    score = predict_professional_score(text)
    if score < 65:
        grade = "Poor"
        needs_enhancement = True
    elif score < 75:
        grade = "Average"
        needs_enhancement = True
    elif score < 82:
        grade = "Good"
        needs_enhancement = False
    else:
        grade = "Excellent"
        needs_enhancement = False
    return score, grade, needs_enhancement


def enhance_resume(text):
    """Enhance resume with suggestions and template additions."""
    text_lower = str(text).lower()
    enhancements = []
    enhanced_text = text

    required_sections = {
        'summary': ['professional summary', 'summary', 'executive summary', 'profile'],
        'experience': ['experience', 'work experience', 'employment', 'professional experience'],
        'education': ['education', 'academic', 'degree', 'qualification'],
        'skills': ['skills', 'technical skills', 'competencies', 'expertise']
    }

    missing_sections = []
    for section_name, keywords in required_sections.items():
        if not any(kw in text_lower for kw in keywords):
            missing_sections.append(section_name)

    if missing_sections:
        enhancements.append(f"ADD: Missing sections - {', '.join(missing_sections)}")

    weak_verbs = {
        'did': 'Executed', 'made': 'Developed', 'helped': 'Supported',
        'worked on': 'Delivered', 'used': 'Leveraged', 'got': 'Achieved',
        'handled': 'Managed', 'did work': 'Implemented'
    }

    action_verb_suggestions = []
    for weak, strong in weak_verbs.items():
        if weak in text_lower:
            action_verb_suggestions.append(f"Replace '{weak}' with '{strong}'")

    if action_verb_suggestions:
        enhancements.append("IMPROVE: " + "; ".join(action_verb_suggestions[:3]))

    quant_count = len(re.findall(r'\d+%|\d+\s*(?:x|times|years?|months?)\b', text_lower))
    if quant_count < 2:
        enhancements.append(
            "ADD: Include quantitative achievements (e.g., 'Increased X by 25%', 'Reduced costs by $Y')"
        )

    enhanced_parts = [enhanced_text]

    if 'summary' in missing_sections or 'profile' in missing_sections:
        summary_template = (
            "\n\nPROFESSIONAL SUMMARY\n" + "-" * 40 +
            "\nResults-driven professional with proven experience. Skilled in [ADD YOUR KEY SKILLS]. "
            "Demonstrated success in [ADD KEY ACHIEVEMENT]. Seeking to leverage expertise to [ADD GOAL].\n"
        )
        enhanced_parts.append(summary_template)

    if 'skills' in missing_sections:
        skills_template = (
            "\n\nSKILLS\n" + "-" * 40 +
            "\n• [Technical Skill 1]  • [Technical Skill 2]  • [Technical Skill 3]\n"
            "• [Soft Skill 1]  • [Soft Skill 2]\n"
        )
        enhanced_parts.append(skills_template)

    enhanced_text = "".join(enhanced_parts)

    return {
        'enhanced_resume': enhanced_text,
        'suggestions': enhancements,
        'missing_sections': missing_sections
    }


def grade_and_enhance(text):
    """Full pipeline: grade resume and return enhanced version if needed."""
    score, grade, needs_enhancement = grade_resume(text)

    result = {
        'score': score,
        'grade': grade,
        'needs_enhancement': needs_enhancement,
        'suggestions': [],
        'enhanced_resume': None,
        'missing_sections': [],
    }

    if needs_enhancement:
        enhancement = enhance_resume(text)
        result['suggestions'] = enhancement['suggestions']
        result['missing_sections'] = enhancement['missing_sections']
        result['enhanced_resume'] = enhancement['enhanced_resume']

    return result
