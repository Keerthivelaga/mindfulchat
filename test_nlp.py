import nlp_engine as n

tests = [
    ("Very positive", "I got promoted today! This is the best day of my life!"),
    ("Positive",      "I am feeling pretty good today, had a nice walk"),
    ("Grateful",      "I am so grateful and blessed, life is good"),
    ("Moderate",      "I feel so stressed and overwhelmed at work"),
    ("Loneliness",    "I feel lonely and nobody cares about me"),
    ("Neutral",       "What is the weather like today?"),
]

for label, text in tests:
    r = n.analyze_message(text)
    level = r["distress_level"].upper()
    score = r["sentiment_score"]
    emotions = r["detected_emotions"]
    is_pos = r["is_positive"]
    print(f"[{level:<15}] score={score:+.1f} | positive={is_pos} | emotions={emotions}")
    print(f"  Input: {text[:65]}")
    print()
