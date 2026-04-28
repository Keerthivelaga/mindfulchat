"""
MindfulChat — Configuration
"""

import os

# ─── Paths ───
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DB_PATH = os.path.join(BASE_DIR, "mindfulchat.db")

# ─── Ollama / Gemma ───
OLLAMA_HOST = "http://localhost:11434"
OLLAMA_MODEL = "gemma:2b"  # Smaller, faster model for low latency
OLLAMA_TEMPERATURE = 0.7
OLLAMA_MAX_TOKENS = 256  # Reduced for faster responses
OLLAMA_CONTEXT_WINDOW = 6  # Fewer history messages = faster inference

# ─── Distress Levels ───
DISTRESS_LEVELS = ["emergency", "high", "moderate", "mild", "positive", "neutral"]

# ─── Emergency Keywords ───
EMERGENCY_KEYWORDS = [
    "kill myself", "want to die", "end my life", "end it all", "suicide",
    "suicidal", "don't want to live", "no reason to live", "can't go on",
    "better off dead", "want to disappear", "end everything", "hurt myself",
    "self harm", "self-harm", "take my life", "overdose", "jump off",
    "slit my", "hang myself", "not worth living", "i want to end",
]

HIGH_DISTRESS_KEYWORDS = [
    "hopeless", "worthless", "useless", "no point", "give up",
    "giving up", "hate myself", "broken", "empty inside", "numb",
    "can't take it", "falling apart", "drowning", "suffocating",
    "trapped", "no way out", "nobody cares", "burden", "all alone",
    "dark place", "rock bottom", "can't breathe", "panic",
]

MODERATE_DISTRESS_KEYWORDS = [
    "depressed", "depression", "anxious", "anxiety", "lonely",
    "alone", "scared", "afraid", "overwhelmed", "exhausted",
    "tired of everything", "can't sleep", "insomnia", "crying",
    "sad", "unhappy", "miserable", "lost", "confused", "angry",
    "frustrated", "stressed", "burnout", "burnt out",
    "worried", "nervous", "panic attack",
]

MILD_DISTRESS_KEYWORDS = [
    "bad day", "rough day", "feeling down", "not great", "a bit low",
    "stressed", "tired", "bored", "restless", "uneasy",
    "not okay", "not fine", "meh", "blah", "off",
    "struggle", "hard time", "tough", "difficult", "heavy",
]

POSITIVE_KEYWORDS = [
    "happy", "good", "great", "better", "grateful", "thankful",
    "hopeful", "relieved", "calm", "peaceful", "fine", "okay",
    "doing well", "content", "smile", "smiling", "glad", "nice day",
    "feeling good", "alright", "not bad", "pretty good", "enjoyed",
    "had fun", "laughed", "made me smile", "positive", "uplifted",
]

VERY_POSITIVE_KEYWORDS = [
    # Joy & happiness
    "amazing", "wonderful", "fantastic", "incredible", "awesome",
    "brilliant", "outstanding", "magnificent", "superb", "excellent",
    # Excitement
    "so excited", "thrilled", "pumped", "can't wait", "stoked",
    "over the moon", "on cloud nine", "jumping for joy",
    # Achievement
    "proud", "accomplished", "achieved", "succeeded", "nailed it",
    "got the job", "passed", "won", "best day", "milestone",
    # Love & connection
    "in love", "fell in love", "got engaged", "got married",
    "new baby", "best friend", "family", "together",
    # Gratitude
    "so grateful", "so thankful", "blessed", "appreciate everything",
    "couldn't be happier", "life is good", "so happy right now",
    # Celebration
    "celebrating", "celebration", "party", "birthday", "anniversary",
    "promotion", "graduation", "good news", "great news",
]

# ─── Harmful Action Keywords (user admits doing something harmful) ───
HARMFUL_ACTION_KEYWORDS = [
    "i killed", "i murdered", "i hit someone", "i hurt someone",
    "i stabbed", "i attacked", "i beat", "i harmed",
    "i poisoned", "i assaulted", "i choked",
]

# ─── Restricted Words — NEVER use in bot responses ───
RESTRICTED_WORDS = [
    "kill", "murder", "suicide", "stab", "slit", "hang yourself",
    "overdose", "jump off", "cut yourself", "end your life",
    "shoot", "strangle", "choke", "poison", "suffocate",
    "bleed out", "drown yourself", "weapon", "gun", "knife",
    "noose", "pills", "razor", "die", "death",
]

# ─── Restricted Word Replacements ───
RESTRICTED_REPLACEMENTS = {
    "kill": "harm", "murder": "hurt", "suicide": "crisis",
    "stab": "hurt", "slit": "hurt", "overdose": "crisis",
    "shoot": "harm", "strangle": "harm", "choke": "harm",
    "poison": "harm", "die": "be in pain", "death": "loss",
    "gun": "danger", "knife": "danger", "noose": "danger",
    "pills": "substance", "razor": "danger", "weapon": "danger",
}

# ─── Music Recommendations by Emotion ───
MUSIC_RECOMMENDATIONS = {
    "anxiety": [
        {"title": "Weightless", "artist": "Marconi Union", "type": "🎵 Ambient", "note": "Scientifically proven to reduce anxiety by 65%"},
        {"title": "Clair de Lune", "artist": "Debussy", "type": "🎹 Classical", "note": "Calming piano piece to slow your breathing"},
        {"title": "Breathe Me", "artist": "Sia", "type": "🎤 Indie", "note": "A gentle, emotional release"},
        {"title": "River Flows in You", "artist": "Yiruma", "type": "🎹 Piano", "note": "Peaceful piano to ease tension"},
    ],
    "sadness": [
        {"title": "Fix You", "artist": "Coldplay", "type": "🎸 Rock", "note": "A reminder that you can find your way"},
        {"title": "Lean on Me", "artist": "Bill Withers", "type": "🎵 Soul", "note": "You don't have to carry it alone"},
        {"title": "Here Comes the Sun", "artist": "The Beatles", "type": "🎸 Classic", "note": "The sun always rises again"},
        {"title": "Better Days", "artist": "OneRepublic", "type": "🎤 Pop", "note": "Hope for brighter tomorrow"},
    ],
    "loneliness": [
        {"title": "You've Got a Friend", "artist": "Carole King", "type": "🎤 Folk", "note": "A warm reminder of connection"},
        {"title": "Count on Me", "artist": "Bruno Mars", "type": "🎤 Pop", "note": "Friendship and support"},
        {"title": "Lovely Day", "artist": "Bill Withers", "type": "🎵 Soul", "note": "Uplifting and warm"},
        {"title": "I'll Be There", "artist": "Jackson 5", "type": "🎤 Pop", "note": "You are never truly alone"},
    ],
    "stress": [
        {"title": "Three Little Birds", "artist": "Bob Marley", "type": "🎵 Reggae", "note": "Every little thing is gonna be alright"},
        {"title": "Somewhere Over the Rainbow", "artist": "IZ", "type": "🎵 Hawaiian", "note": "A peaceful escape"},
        {"title": "Don't Worry Be Happy", "artist": "Bobby McFerrin", "type": "🎵 Pop", "note": "Simple joy in every note"},
        {"title": "Let It Be", "artist": "The Beatles", "type": "🎸 Classic", "note": "Sometimes letting go helps"},
    ],
    "anger": [
        {"title": "Imagine", "artist": "John Lennon", "type": "🎹 Classic", "note": "Perspective and peace"},
        {"title": "What a Wonderful World", "artist": "Louis Armstrong", "type": "🎵 Jazz", "note": "Finding beauty in the world"},
        {"title": "Peace of Mind", "artist": "Boston", "type": "🎸 Rock", "note": "Finding inner calm"},
        {"title": "Bridge Over Troubled Water", "artist": "Simon & Garfunkel", "type": "🎤 Folk", "note": "Comfort and support"},
    ],
    "exhaustion": [
        {"title": "Gymnopédie No.1", "artist": "Erik Satie", "type": "🎹 Classical", "note": "Gentle rest for a tired mind"},
        {"title": "Sunset Lover", "artist": "Petit Biscuit", "type": "🎵 Electronic", "note": "Dreamy and restorative"},
        {"title": "Skinny Love", "artist": "Bon Iver", "type": "🎤 Indie", "note": "A quiet, reflective moment"},
        {"title": "Ocean Eyes", "artist": "Billie Eilish", "type": "🎤 Pop", "note": "Soft and soothing"},
    ],
    "positive": [
        {"title": "Happy", "artist": "Pharrell Williams", "type": "🎤 Pop", "note": "Celebrate your good mood!"},
        {"title": "Walking on Sunshine", "artist": "Katrina & The Waves", "type": "🎸 Pop", "note": "Pure joy energy"},
        {"title": "Good as Hell", "artist": "Lizzo", "type": "🎤 Pop", "note": "Self-love anthem"},
        {"title": "Best Day of My Life", "artist": "American Authors", "type": "🎸 Rock", "note": "Keep the positivity going!"},
    ],
}

# ─── Movie Recommendations by Emotion ───
MOVIE_RECOMMENDATIONS = {
    "anxiety": [
        {"title": "The Secret Life of Walter Mitty", "year": "2013", "type": "🎬 Adventure", "note": "Inspires courage and stepping outside comfort zones"},
        {"title": "Soul", "year": "2020", "type": "🎬 Animation", "note": "Finding purpose and appreciating small moments"},
        {"title": "My Neighbor Totoro", "year": "1988", "type": "🎬 Animation", "note": "A calming, heartwarming Studio Ghibli classic"},
    ],
    "sadness": [
        {"title": "Inside Out", "year": "2015", "type": "🎬 Animation", "note": "Understanding that sadness is okay and necessary"},
        {"title": "Good Will Hunting", "year": "1997", "type": "🎬 Drama", "note": "It's not your fault — healing through connection"},
        {"title": "The Pursuit of Happyness", "year": "2006", "type": "🎬 Drama", "note": "Resilience and hope through hardship"},
    ],
    "loneliness": [
        {"title": "Up", "year": "2009", "type": "🎬 Animation", "note": "Adventure and connection can come from unexpected places"},
        {"title": "The Intouchables", "year": "2011", "type": "🎬 Comedy-Drama", "note": "An unlikely friendship that changes everything"},
        {"title": "Cast Away", "year": "2000", "type": "🎬 Drama", "note": "The human will to connect and survive"},
    ],
    "stress": [
        {"title": "Ferris Bueller's Day Off", "year": "1986", "type": "🎬 Comedy", "note": "Sometimes you just need a day off"},
        {"title": "Chef", "year": "2014", "type": "🎬 Comedy", "note": "Rediscovering passion and simplicity"},
        {"title": "The Grand Budapest Hotel", "year": "2014", "type": "🎬 Comedy", "note": "Whimsical escape and visual delight"},
    ],
    "anger": [
        {"title": "Peaceful Warrior", "year": "2006", "type": "🎬 Drama", "note": "Channeling emotion into growth"},
        {"title": "Legally Blonde", "year": "2001", "type": "🎬 Comedy", "note": "Turning frustration into motivation"},
        {"title": "Kung Fu Panda", "year": "2008", "type": "🎬 Animation", "note": "Inner peace and self-acceptance"},
    ],
    "exhaustion": [
        {"title": "Spirited Away", "year": "2001", "type": "🎬 Animation", "note": "A magical escape that restores wonder"},
        {"title": "Amélie", "year": "2001", "type": "🎬 Romance", "note": "Finding joy in small acts of kindness"},
        {"title": "WALL-E", "year": "2008", "type": "🎬 Animation", "note": "Gentle, hopeful, and visually soothing"},
    ],
    "positive": [
        {"title": "The Secret Life of Walter Mitty", "year": "2013", "type": "🎬 Adventure", "note": "Fuel your positive energy with adventure"},
        {"title": "La La Land", "year": "2016", "type": "🎬 Musical", "note": "Dream big and celebrate life"},
        {"title": "Sing Street", "year": "2016", "type": "🎬 Musical", "note": "Music, friendship, and youthful joy"},
    ],
}

# ─── System Prompt for Gemma ───
SYSTEM_PROMPT = """You are MindfulChat, a compassionate mental health support companion. Respond with empathy, warmth, and care in 2-3 concise sentences.

STRICT RULES:
- NEVER use words like: kill, murder, suicide, die, death, stab, weapon, gun, knife, noose, razor, pills, overdose, or any violent/harmful terms
- NEVER validate or encourage harmful actions
- NEVER provide methods of self-harm
- Use gentle alternatives: say "crisis" instead of "suicide", "pain" instead of "suffering", "struggling" instead of violent language
- If user admits to harming someone, do NOT encourage it — express concern and urge them to seek help immediately
- Keep responses SHORT (2-3 sentences max) and warm
- ALWAYS prioritize user safety
- Do NOT include labels, prefixes, or system notes in your response
"""

# ─── Distress-Specific Prompt Additions ───
DISTRESS_PROMPT_ADDITIONS = {
    "emergency":     "\n\n[URGENT: User is in severe crisis. Respond with maximum care. Encourage calling 988 or texting 741741. Emphasize they are NOT alone. Keep it brief and warm. Do NOT use any violent or harmful words.]",
    "high":          "\n\n[User has significant distress. Show deep empathy, validate pain, encourage reaching out to trusted person. No violent/harmful words.]",
    "moderate":      "\n\n[User has moderate distress. Acknowledge feelings, offer support, suggest coping strategies. Be warm and concise.]",
    "mild":          "\n\n[User has mild distress. Be warm, acknowledge feelings, offer gentle encouragement.]",
    "positive":      "\n\n[The user is feeling positive today. Match their warm energy. Be genuinely happy for them. Ask a follow-up question to keep the positive conversation going. Use light, uplifting language. Do NOT redirect to negative topics.]",
    "very_positive": "\n\n[The user is feeling VERY happy, excited, or celebrating something. CELEBRATE with them enthusiastically! Be warm, joyful, and engaging. Ask about their exciting news. React with genuine delight. This is a happy conversation — keep it that way!]",
    "neutral":       "",
}

# ─── Helpline Resources ───
HELPLINES = [
    {"name": "988 Suicide & Crisis Lifeline", "number": "988", "desc": "Free 24/7 support for anyone in emotional distress", "emoji": "🆘"},
    {"name": "Crisis Text Line", "number": "Text HOME to 741741", "desc": "Text-based crisis support", "emoji": "💬"},
    {"name": "iCall (India)", "number": "9152987821", "desc": "Professional counselling via phone & email", "emoji": "🌍"},
    {"name": "Vandrevala Foundation", "number": "1860-2662-345", "desc": "24/7 mental health helpline for India", "emoji": "🤝"},
    {"name": "AASRA (India)", "number": "9820466726", "desc": "Crisis intervention for prevention", "emoji": "📱"},
    {"name": "NIMHANS Helpline", "number": "080-46110007", "desc": "National mental health helpline by NIMHANS", "emoji": "🧠"},
]

# ─── Music Recommendations by Emotion ───
MUSIC_RECOMMENDATIONS = {
    "anxiety": [
        {"title": "Weightless", "artist": "Marconi Union", "type": "🎵 Ambient", "note": "Proven to reduce anxiety by 65%"},
        {"title": "Clair de Lune", "artist": "Debussy", "type": "🎹 Classical", "note": "Calming piano to slow your breathing"},
        {"title": "River Flows in You", "artist": "Yiruma", "type": "🎹 Piano", "note": "Peaceful piano to ease tension"},
    ],
    "sadness": [
        {"title": "Fix You", "artist": "Coldplay", "type": "🎸 Rock", "note": "A reminder you can find your way"},
        {"title": "Here Comes the Sun", "artist": "The Beatles", "type": "🎸 Classic", "note": "The sun always rises again"},
        {"title": "Better Days", "artist": "OneRepublic", "type": "🎤 Pop", "note": "Hope for a brighter tomorrow"},
    ],
    "loneliness": [
        {"title": "You've Got a Friend", "artist": "Carole King", "type": "🎤 Folk", "note": "A warm reminder of connection"},
        {"title": "Count on Me", "artist": "Bruno Mars", "type": "🎤 Pop", "note": "Friendship and support"},
        {"title": "Lovely Day", "artist": "Bill Withers", "type": "🎵 Soul", "note": "Uplifting and warm"},
    ],
    "stress": [
        {"title": "Three Little Birds", "artist": "Bob Marley", "type": "🎵 Reggae", "note": "Every little thing gonna be alright"},
        {"title": "Let It Be", "artist": "The Beatles", "type": "🎸 Classic", "note": "Sometimes letting go helps"},
        {"title": "Don't Worry Be Happy", "artist": "Bobby McFerrin", "type": "🎵 Pop", "note": "Simple joy in every note"},
    ],
    "anger": [
        {"title": "Imagine", "artist": "John Lennon", "type": "🎹 Classic", "note": "Perspective and peace"},
        {"title": "What a Wonderful World", "artist": "Louis Armstrong", "type": "🎵 Jazz", "note": "Finding beauty in the world"},
    ],
    "exhaustion": [
        {"title": "Gymnopédie No.1", "artist": "Erik Satie", "type": "🎹 Classical", "note": "Gentle rest for a tired mind"},
        {"title": "Ocean Eyes", "artist": "Billie Eilish", "type": "🎤 Pop", "note": "Soft and soothing"},
    ],
    "hopelessness": [
        {"title": "Fix You", "artist": "Coldplay", "type": "🎸 Rock", "note": "You will find your way"},
        {"title": "Lean on Me", "artist": "Bill Withers", "type": "🎵 Soul", "note": "You don't have to carry it alone"},
    ],
    "positive": [
        {"title": "Happy", "artist": "Pharrell Williams", "type": "🎤 Pop", "note": "Celebrate your good mood!"},
        {"title": "Good as Hell", "artist": "Lizzo", "type": "🎤 Pop", "note": "Self-love anthem"},
    ],
}

# ─── Movie Recommendations by Emotion ───
MOVIE_RECOMMENDATIONS = {
    "anxiety": [
        {"title": "The Secret Life of Walter Mitty", "year": "2013", "type": "🎬 Adventure", "note": "Courage to step outside your comfort zone"},
        {"title": "My Neighbor Totoro", "year": "1988", "type": "🎬 Animation", "note": "A calming, heartwarming classic"},
    ],
    "sadness": [
        {"title": "Inside Out", "year": "2015", "type": "🎬 Animation", "note": "Sadness is okay — and necessary"},
        {"title": "The Pursuit of Happyness", "year": "2006", "type": "🎬 Drama", "note": "Resilience and hope through hardship"},
    ],
    "loneliness": [
        {"title": "Up", "year": "2009", "type": "🎬 Animation", "note": "Connection from unexpected places"},
        {"title": "The Intouchables", "year": "2011", "type": "🎬 Drama", "note": "An unlikely friendship changes everything"},
    ],
    "stress": [
        {"title": "Ferris Bueller's Day Off", "year": "1986", "type": "🎬 Comedy", "note": "Sometimes you just need a day off"},
        {"title": "Chef", "year": "2014", "type": "🎬 Comedy", "note": "Rediscovering passion and simplicity"},
    ],
    "anger": [
        {"title": "Kung Fu Panda", "year": "2008", "type": "🎬 Animation", "note": "Inner peace and self-acceptance"},
        {"title": "Peaceful Warrior", "year": "2006", "type": "🎬 Drama", "note": "Channeling emotion into growth"},
    ],
    "exhaustion": [
        {"title": "Spirited Away", "year": "2001", "type": "🎬 Animation", "note": "A magical escape that restores wonder"},
        {"title": "WALL-E", "year": "2008", "type": "🎬 Animation", "note": "Gentle, hopeful, and soothing"},
    ],
    "hopelessness": [
        {"title": "Good Will Hunting", "year": "1997", "type": "🎬 Drama", "note": "It's not your fault — healing through connection"},
        {"title": "Soul", "year": "2020", "type": "🎬 Animation", "note": "Finding purpose in small moments"},
    ],
    "positive": [
        {"title": "La La Land", "year": "2016", "type": "🎬 Musical", "note": "Dream big and celebrate life"},
        {"title": "Sing Street", "year": "2016", "type": "🎬 Musical", "note": "Music, friendship, and youthful joy"},
    ],
}
