"""
MindfulChat — NLP Engine
Full sentiment analysis: positive emotions + distress detection.
"""

from config import (
    EMERGENCY_KEYWORDS,
    HIGH_DISTRESS_KEYWORDS,
    MODERATE_DISTRESS_KEYWORDS,
    MILD_DISTRESS_KEYWORDS,
    POSITIVE_KEYWORDS,
    VERY_POSITIVE_KEYWORDS,
    HARMFUL_ACTION_KEYWORDS,
)

# ─── Negative Emotion Patterns ───
NEGATIVE_EMOTION_PATTERNS = [
    {"label": "anxiety",     "words": ["anxious", "anxiety", "worried", "nervous", "panic", "restless", "dread"]},
    {"label": "loneliness",  "words": ["lonely", "alone", "isolated", "nobody", "no one", "abandoned", "left out"]},
    {"label": "sadness",     "words": ["sad", "crying", "tears", "unhappy", "miserable", "depressed", "depression", "grief", "heartbroken"]},
    {"label": "anger",       "words": ["angry", "frustrated", "furious", "rage", "mad", "irritated", "resentful", "bitter"]},
    {"label": "exhaustion",  "words": ["tired", "exhausted", "drained", "burnout", "fatigue", "burnt out", "worn out", "no energy"]},
    {"label": "fear",        "words": ["scared", "afraid", "terrified", "fear", "frightened", "phobia", "dread"]},
    {"label": "stress",      "words": ["stressed", "overwhelmed", "pressure", "overloaded", "swamped", "too much"]},
    {"label": "hopelessness","words": ["hopeless", "worthless", "useless", "pointless", "empty", "numb", "void", "meaningless"]},
    {"label": "guilt",       "words": ["guilty", "ashamed", "shame", "regret", "blame myself", "my fault"]},
    {"label": "confusion",   "words": ["confused", "lost", "don't know", "uncertain", "stuck", "unsure"]},
]

# ─── Positive Emotion Patterns ───
POSITIVE_EMOTION_PATTERNS = [
    {"label": "joy",          "words": ["happy", "joy", "joyful", "joyous", "elated", "delighted", "overjoyed", "blissful", "ecstatic"]},
    {"label": "excitement",   "words": ["excited", "thrilled", "pumped", "hyped", "stoked", "can't wait", "looking forward", "eager", "enthusiastic"]},
    {"label": "gratitude",    "words": ["grateful", "thankful", "blessed", "appreciate", "appreciated", "thankful for", "so thankful"]},
    {"label": "pride",        "words": ["proud", "accomplished", "achieved", "success", "succeeded", "nailed it", "did it", "finally did"]},
    {"label": "love",         "words": ["love", "loved", "in love", "caring", "affection", "adore", "cherish", "wonderful people"]},
    {"label": "contentment",  "words": ["content", "peaceful", "calm", "relaxed", "at peace", "settled", "comfortable", "cozy"]},
    {"label": "relief",       "words": ["relieved", "relief", "finally over", "weight lifted", "so glad it's done", "phew", "thank god"]},
    {"label": "hope",         "words": ["hopeful", "optimistic", "looking up", "better days", "things are improving", "positive outlook"]},
    {"label": "amusement",    "words": ["funny", "laughing", "hilarious", "cracking up", "lol", "haha", "so funny", "made me laugh"]},
    {"label": "confidence",   "words": ["confident", "strong", "capable", "ready", "motivated", "determined", "unstoppable", "on top of the world"]},
]

# ─── Negation Words ───
NEGATION_WORDS = ["not", "no", "never", "don't", "doesn't", "isn't", "aren't", "wasn't", "weren't", "can't", "won't"]


def _text_contains_keyword(text_lower: str, keywords: list) -> list:
    return [kw for kw in keywords if kw in text_lower]


def _detect_negation(text_lower: str, keyword: str) -> bool:
    idx = text_lower.find(keyword)
    if idx <= 0:
        return False
    prefix = text_lower[max(0, idx - 15):idx]
    return any(neg in prefix for neg in NEGATION_WORDS)


def detect_emotions(text: str) -> list:
    """Detect all emotions (both positive and negative) present in the text."""
    text_lower = text.lower()
    detected = []
    for pattern in NEGATIVE_EMOTION_PATTERNS + POSITIVE_EMOTION_PATTERNS:
        for word in pattern["words"]:
            if word in text_lower and not _detect_negation(text_lower, word):
                detected.append(pattern["label"])
                break
    return detected


def detect_positive_emotions(text: str) -> list:
    """Detect only positive emotions."""
    text_lower = text.lower()
    detected = []
    for pattern in POSITIVE_EMOTION_PATTERNS:
        for word in pattern["words"]:
            if word in text_lower and not _detect_negation(text_lower, word):
                detected.append(pattern["label"])
                break
    return detected


def _compute_sentiment_score(text_lower: str) -> float:
    """
    Score from -1.0 (very negative) to +1.0 (very positive).
    Positive emotions now have higher weight.
    """
    weights = {
        "emergency": -1.0, "high": -0.7, "moderate": -0.4, "mild": -0.2,
        "positive": 0.6, "very_positive": 1.0,
    }

    emergency_hits = _text_contains_keyword(text_lower, EMERGENCY_KEYWORDS)
    high_hits      = _text_contains_keyword(text_lower, HIGH_DISTRESS_KEYWORDS)
    moderate_hits  = _text_contains_keyword(text_lower, MODERATE_DISTRESS_KEYWORDS)
    mild_hits      = _text_contains_keyword(text_lower, MILD_DISTRESS_KEYWORDS)
    positive_hits  = _text_contains_keyword(text_lower, POSITIVE_KEYWORDS)
    vpos_hits      = _text_contains_keyword(text_lower, VERY_POSITIVE_KEYWORDS)

    total = (len(emergency_hits) + len(high_hits) + len(moderate_hits) +
             len(mild_hits) + len(positive_hits) + len(vpos_hits))

    if total == 0:
        return 0.0

    score = (
        len(emergency_hits) * weights["emergency"] +
        len(high_hits)      * weights["high"] +
        len(moderate_hits)  * weights["moderate"] +
        len(mild_hits)      * weights["mild"] +
        len(positive_hits)  * weights["positive"] +
        len(vpos_hits)      * weights["very_positive"]
    ) / total

    return round(max(-1.0, min(1.0, score)), 2)


def detect_distress_level(text: str) -> str:
    """
    Classify the emotional level of a message.
    Returns: 'emergency' | 'high' | 'moderate' | 'mild' |
             'very_positive' | 'positive' | 'neutral'
    """
    text_lower = text.lower()

    # Crisis always takes priority
    if _text_contains_keyword(text_lower, EMERGENCY_KEYWORDS):
        return "emergency"
    if _text_contains_keyword(text_lower, HIGH_DISTRESS_KEYWORDS):
        return "high"
    if _text_contains_keyword(text_lower, MODERATE_DISTRESS_KEYWORDS):
        return "moderate"
    if _text_contains_keyword(text_lower, MILD_DISTRESS_KEYWORDS):
        return "mild"

    # Positive tiers
    if _text_contains_keyword(text_lower, VERY_POSITIVE_KEYWORDS):
        return "very_positive"
    if _text_contains_keyword(text_lower, POSITIVE_KEYWORDS):
        return "positive"

    # Fallback: count positive emotion patterns
    pos_emotions = detect_positive_emotions(text)
    if len(pos_emotions) >= 2:
        return "very_positive"
    if len(pos_emotions) == 1:
        return "positive"

    return "neutral"


def analyze_message(text: str, previous_levels: list = None) -> dict:
    """
    Full NLP analysis of a user message.
    Returns distress_level, emotions, sentiment_score, emergency_flag, etc.
    """
    text_lower = text.lower()

    distress_level   = detect_distress_level(text)
    all_emotions     = detect_emotions(text)
    positive_emotions = [e for e in all_emotions if e in
                         [p["label"] for p in POSITIVE_EMOTION_PATTERNS]]
    negative_emotions = [e for e in all_emotions if e in
                         [p["label"] for p in NEGATIVE_EMOTION_PATTERNS]]
    sentiment_score  = _compute_sentiment_score(text_lower)

    keywords_matched = []
    keywords_matched.extend(_text_contains_keyword(text_lower, EMERGENCY_KEYWORDS))
    keywords_matched.extend(_text_contains_keyword(text_lower, HIGH_DISTRESS_KEYWORDS))
    keywords_matched.extend(_text_contains_keyword(text_lower, MODERATE_DISTRESS_KEYWORDS))
    keywords_matched.extend(_text_contains_keyword(text_lower, MILD_DISTRESS_KEYWORDS))

    harmful_action = bool(_text_contains_keyword(text_lower, HARMFUL_ACTION_KEYWORDS))
    emergency_flag = distress_level == "emergency" or harmful_action

    # Escalation detection
    escalation_detected = False
    if previous_levels and len(previous_levels) >= 2:
        severity = {"neutral": 0, "very_positive": 0, "positive": 0,
                    "mild": 1, "moderate": 2, "high": 3, "emergency": 4}
        curr = severity.get(distress_level, 0)
        avg_prev = sum(severity.get(l, 0) for l in previous_levels[-3:]) / min(len(previous_levels), 3)
        if curr > avg_prev + 1:
            escalation_detected = True

    return {
        "distress_level":     distress_level,
        "detected_emotions":  all_emotions,
        "positive_emotions":  positive_emotions,
        "negative_emotions":  negative_emotions,
        "emergency_flag":     emergency_flag,
        "harmful_action":     harmful_action,
        "keywords_matched":   keywords_matched,
        "sentiment_score":    sentiment_score,
        "escalation_detected": escalation_detected,
        "is_positive":        distress_level in ("positive", "very_positive"),
    }
