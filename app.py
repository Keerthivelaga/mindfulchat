"""
MindfulChat — Main Streamlit Application
With recommendations, mandatory emergency contact, and harmful action handling.
"""

import streamlit as st
import datetime
import database as db
import auth
import nlp_engine
import llm_handler
import alert_system
from config import HELPLINES, MUSIC_RECOMMENDATIONS, MOVIE_RECOMMENDATIONS

# ─── Page Config ───
st.set_page_config(
    page_title="MindfulChat — Mental Wellness Companion",
    page_icon="💜",
    layout="wide",
    initial_sidebar_state="expanded",
)

# ─── Init DB ───
db.init_db()

# ─── Custom CSS ───
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700&family=Outfit:wght@300;400;500;600;700&display=swap');
:root { --accent: #7c6bf0; --accent2: #5b8def; --danger: #f06b8a; --success: #6bdfb8; }
.stApp { font-family: 'Inter', sans-serif; }
h1, h2, h3 { font-family: 'Outfit', sans-serif !important; }
.brand-header { text-align:center; padding:1.5rem 0 1rem; }
.brand-header h1 { background: linear-gradient(135deg,#7c6bf0,#5b8def); -webkit-background-clip:text;
    -webkit-text-fill-color:transparent; font-size:2rem; margin:0; }
.brand-header p { color:#9896a8; font-size:0.9rem; margin-top:0.3rem; }
.emergency-box { background:rgba(240,107,138,0.12); border:1px solid rgba(240,107,138,0.35);
    border-radius:12px; padding:1rem 1.2rem; margin:0.8rem 0; color:#f06b8a; }
.emergency-box strong { color:#e8e6f0; }
.alert-sent-box { background:rgba(240,107,138,0.2); border:2px solid rgba(240,107,138,0.5);
    border-radius:12px; padding:1rem 1.2rem; margin:0.8rem 0; color:#f06b8a; font-weight:600; }
.joy-box { background:rgba(240,192,107,0.1); border:1px solid rgba(240,192,107,0.3);
    border-radius:12px; padding:0.7rem 1rem; margin:0.5rem 0; color:#f0c06b; font-size:0.85rem; }
.resource-card { background:rgba(26,26,46,0.7); border:1px solid rgba(255,255,255,0.06);
    border-radius:12px; padding:1.2rem; margin-bottom:0.8rem; }
.resource-card:hover { border-color:rgba(124,107,240,0.3); }
.rec-card { background:rgba(26,26,46,0.7); border:1px solid rgba(255,255,255,0.08);
    border-radius:12px; padding:0.9rem 1.1rem; margin-bottom:0.5rem; }
.rec-card h4 { color:#e8e6f0; margin:0 0 2px; font-size:0.9rem; }
.rec-card .artist { color:#7c6bf0; font-size:0.8rem; }
.rec-card .note { color:#9896a8; font-size:0.78rem; margin-top:4px; }
.journal-entry { background:rgba(26,26,46,0.7); border:1px solid rgba(255,255,255,0.06);
    border-radius:12px; padding:1rem 1.2rem; margin-bottom:0.7rem; }
.journal-date { color:#7c6bf0; font-size:0.8rem; font-weight:600; margin-bottom:0.4rem; }
.breathing-text { text-align:center; font-size:1.8rem; font-weight:700; color:#7c6bf0;
    padding:2rem 0; font-family:'Outfit',sans-serif; }
div[data-testid="stChatMessage"] { border-radius:16px !important; }
.stChatInput > div { border-radius:16px !important; }
section[data-testid="stSidebar"] > div { padding-top:1rem; }
.disclaimer { text-align:center; font-size:0.72rem; color:#6b6980; padding:0.5rem 1rem; line-height:1.4; }
</style>
""", unsafe_allow_html=True)


# ─── Session State Defaults ───
def init_session():
    defaults = {
        "user": None, "conversation_id": None, "messages": [],
        "previous_levels": [], "detected_emotions_history": [],
    }
    for k, v in defaults.items():
        if k not in st.session_state:
            st.session_state[k] = v

init_session()


# ─── Auth Pages ───
def render_auth():
    st.markdown('<div class="brand-header"><h1>💜 MindfulChat</h1><p>Your safe space for mental wellness</p></div>', unsafe_allow_html=True)

    tab1, tab2 = st.tabs(["🔑 Login", "📝 Register"])

    with tab1:
        with st.form("login_form"):
            username = st.text_input("Username", key="login_user")
            password = st.text_input("Password", type="password", key="login_pass")
            submitted = st.form_submit_button("Login", use_container_width=True)
            if submitted:
                result = auth.login_user(username, password)
                if result["success"]:
                    st.session_state.user = result["user"]
                    st.rerun()
                else:
                    st.error(result["message"])

    with tab2:
        with st.form("register_form"):
            new_user = st.text_input("Username", key="reg_user")
            new_name = st.text_input("Display Name", key="reg_name")
            new_pass = st.text_input("Password", type="password", key="reg_pass")
            new_pass2 = st.text_input("Confirm Password", type="password", key="reg_pass2")
            st.markdown("##### 🚨 Emergency Contact *(Required)*")
            st.caption("This contact will be notified immediately if a crisis is detected.")
            ec_name = st.text_input("Contact Name *", key="reg_ec_name")
            ec_phone = st.text_input("Contact Phone *", key="reg_ec_phone")
            ec_email = st.text_input("Contact Email", key="reg_ec_email")
            submitted = st.form_submit_button("Create Account", use_container_width=True)
            if submitted:
                if new_pass != new_pass2:
                    st.error("Passwords don't match.")
                else:
                    result = auth.register_user(new_user, new_pass, new_name, ec_name, ec_phone, ec_email)
                    if result["success"]:
                        st.success(result["message"] + " Please login.")
                    else:
                        st.error(result["message"])

    st.markdown('<p class="disclaimer">MindfulChat is an AI companion, not a substitute for professional help.</p>', unsafe_allow_html=True)


# ─── Recommendations ───

# Map detected emotion labels → recommendation keys
EMOTION_TO_REC_KEY = {
    # Negative emotions — direct matches
    "anxiety":     "anxiety",
    "sadness":     "sadness",
    "loneliness":  "loneliness",
    "stress":      "stress",
    "anger":       "anger",
    "exhaustion":  "exhaustion",
    "hopelessness":"hopelessness",
    "fear":        "anxiety",       # fear → anxiety recs
    "guilt":       "hopelessness",  # guilt → hopelessness recs
    "confusion":   "stress",        # confusion → stress recs
    # Positive emotions — all map to "positive"
    "joy":         "positive",
    "excitement":  "positive",
    "gratitude":   "positive",
    "pride":       "positive",
    "love":        "positive",
    "contentment": "positive",
    "relief":      "positive",
    "hope":        "positive",
    "amusement":   "positive",
    "confidence":  "positive",
}


def _get_recommendations(emotions: list) -> dict:
    """Get music and movie recommendations based on detected emotions."""
    music = []
    movies = []
    seen_music = set()
    seen_movies = set()

    for emotion in emotions:
        rec_key = EMOTION_TO_REC_KEY.get(emotion, emotion)
        for m in MUSIC_RECOMMENDATIONS.get(rec_key, []):
            if m["title"] not in seen_music:
                music.append(m)
                seen_music.add(m["title"])
        for mv in MOVIE_RECOMMENDATIONS.get(rec_key, []):
            if mv["title"] not in seen_movies:
                movies.append(mv)
                seen_movies.add(mv["title"])

    # Limit to top 4 each
    return {"music": music[:4], "movies": movies[:3]}


def _render_recommendations(emotions: list):
    """Render music and movie recommendation cards in the sidebar or below chat."""
    if not emotions:
        return

    recs = _get_recommendations(emotions)

    if recs["music"]:
        st.markdown("#### 🎵 Music For You")
        for m in recs["music"]:
            st.markdown(f"""<div class="rec-card">
                <h4>{m['type']} {m['title']}</h4>
                <span class="artist">{m['artist']}</span>
                <p class="note">💡 {m['note']}</p>
            </div>""", unsafe_allow_html=True)

    if recs["movies"]:
        st.markdown("#### 🎬 Movies For You")
        for mv in recs["movies"]:
            st.markdown(f"""<div class="rec-card">
                <h4>{mv['type']} {mv['title']} ({mv['year']})</h4>
                <p class="note">💡 {mv['note']}</p>
            </div>""", unsafe_allow_html=True)


# ─── Chat Page ───
def render_chat():
    # Ensure conversation exists
    if not st.session_state.conversation_id:
        conv_id = db.create_conversation(st.session_state.user["id"])
        st.session_state.conversation_id = conv_id
        st.session_state.messages = []

    # Layout: chat + recommendations sidebar
    chat_col, rec_col = st.columns([3, 1])

    with chat_col:
        # Display messages
        for msg in st.session_state.messages:
            avatar = "💜" if msg["role"] == "assistant" else "🧑"
            with st.chat_message(msg["role"], avatar=avatar):
                st.markdown(msg["content"])

        # Welcome message if empty
        if not st.session_state.messages:
            st.markdown('<div class="brand-header"><h1>💜 MindfulChat</h1><p>A safe space to share how you\'re feeling. I\'m here to listen without judgment.</p></div>', unsafe_allow_html=True)
            cols = st.columns(4)
            prompts = [
                ("😓 Stressed", "I've been feeling really stressed lately"),
                ("😔 Lonely", "I feel lonely and don't know who to talk to"),
                ("😰 Anxious", "I'm anxious about everything"),
                ("💬 Talk", "I just need someone to talk to"),
            ]
            for i, (label, prompt) in enumerate(prompts):
                if cols[i].button(label, use_container_width=True, key=f"qp_{i}"):
                    _process_user_message(prompt)

        # Chat input
        if user_input := st.chat_input("Share what's on your mind..."):
            _process_user_message(user_input)

        st.markdown('<p class="disclaimer">MindfulChat is an AI companion, not a substitute for professional help. If you\'re in danger, please call 988.</p>', unsafe_allow_html=True)

    # Recommendations sidebar
    with rec_col:
        emotions = list(set(st.session_state.detected_emotions_history[-10:]))

        # Mood indicator
        if st.session_state.previous_levels:
            last_level = st.session_state.previous_levels[-1]
            level_display = {
                "very_positive": ("🌟 Very Positive", "#f0c06b"),
                "positive":      ("😊 Positive",      "#6bdfb8"),
                "neutral":       ("😐 Neutral",        "#9896a8"),
                "mild":          ("😟 Mild Distress",  "#f0c06b"),
                "moderate":      ("😔 Moderate",       "#f07c6b"),
                "high":          ("😢 High Distress",  "#f06b8a"),
                "emergency":     ("🆘 Crisis",         "#f06b8a"),
            }
            label, color = level_display.get(last_level, ("😐 Neutral", "#9896a8"))
            st.markdown(f"**Mood:** <span style='color:{color};font-weight:600'>{label}</span>",
                        unsafe_allow_html=True)
            st.divider()

        if emotions:
            _render_recommendations(emotions)
        else:
            st.markdown("#### 💡 Recommendations")
            st.caption("Music & movie suggestions appear here based on your mood.")


def _process_user_message(text):
    user = st.session_state.user

    # Add user message
    st.session_state.messages.append({"role": "user", "content": text})
    with st.chat_message("user", avatar="🧑"):
        st.markdown(text)

    # NLP Analysis
    analysis = nlp_engine.analyze_message(text, st.session_state.previous_levels)
    st.session_state.previous_levels.append(analysis["distress_level"])

    # Track emotions for recommendations
    st.session_state.detected_emotions_history.extend(analysis["detected_emotions"])

    # Save user message to DB
    db.save_message(st.session_state.conversation_id, "user", text, analysis["distress_level"])

    # Only trigger alerts for non-positive messages
    is_positive = analysis.get("is_positive", False)
    alert_result = {"triggered": False, "alert_data": None, "harmful_action": False}
    if not is_positive:
        alert_result = alert_system.check_and_alert(analysis, user, text)

    if alert_result["triggered"]:
        contact_name = user.get("emergency_contact_name", "your emergency contact")
        contact_phone = user.get("emergency_contact_phone", "")
        notif_status = alert_system.get_notification_status(alert_result.get("alert_data", {}))

        if alert_result.get("harmful_action"):
            st.markdown(
                '<div class="alert-sent-box">⚠️ What you\'ve described is very serious. '
                'Please speak to a professional or emergency services immediately.<br>'
                f'<small>{notif_status}</small></div>',
                unsafe_allow_html=True
            )
        else:
            st.markdown(
                '<div class="emergency-box">🆘 <strong>Please call '
                '<a href="tel:988">988</a> or text HOME to '
                '<a href="sms:741741">741741</a></strong><br>'
                f'📢 Alert sent to <strong>{contact_name}</strong>'
                f'{" (" + contact_phone + ")" if contact_phone else ""}<br>'
                f'<small>{notif_status}</small></div>',
                unsafe_allow_html=True
            )

    # Show joy banner for very positive messages
    if analysis["distress_level"] == "very_positive":
        pos_emotions = analysis.get("positive_emotions", [])
        emotions_str = ", ".join(pos_emotions) if pos_emotions else "joy"
        score = analysis["sentiment_score"]
        st.markdown(
            f'<div class="joy-box">🌟 Feeling: <strong>{emotions_str}</strong> '
            f'| Mood score: <strong>+{score}</strong> 🎉</div>',
            unsafe_allow_html=True
        )


    # Build user context for LLM
    user_context = {
        "display_name": user.get("display_name", ""),
        "recent_emotions": list(set(st.session_state.detected_emotions_history[-5:])),
    }

    # Convert messages to LLM format
    conv_history = [
        {"role": m["role"], "content": m["content"]}
        for m in st.session_state.messages[:-1]
    ]

    # Generate response
    with st.chat_message("assistant", avatar="💜"):
        response_placeholder = st.empty()
        full_response = ""
        for chunk in llm_handler.generate_response_stream(text, conv_history, analysis, user_context):
            full_response += chunk
            response_placeholder.markdown(full_response + "▌")
        response_placeholder.markdown(full_response)

    # Save bot message
    st.session_state.messages.append({"role": "assistant", "content": full_response})
    db.save_message(st.session_state.conversation_id, "bot", full_response)


# ─── Breathing Page ───
def render_breathing():
    st.markdown('<div class="brand-header"><h1>🫁 Guided Breathing</h1><p>Take a moment to center yourself</p></div>', unsafe_allow_html=True)

    technique = st.radio("Choose a technique:", ["4-7-8", "Box Breathing", "Simple"], horizontal=True)

    info = {
        "4-7-8": ("Breathe in 4s → Hold 7s → Exhale 8s", "Activates your parasympathetic nervous system."),
        "Box Breathing": ("Breathe in 4s → Hold 4s → Exhale 4s → Hold 4s", "Used by Navy SEALs for calm focus."),
        "Simple": ("Breathe in 4s → Exhale 6s", "A gentle, easy rhythm for quick reset."),
    }
    steps_text, description = info[technique]
    st.info(f"**{technique}**: {steps_text}")
    st.markdown(f"*{description}*")

    phases = {
        "4-7-8": [("🌬️ Breathe In...", 4), ("⏸️ Hold...", 7), ("💨 Breathe Out...", 8)],
        "Box Breathing": [("🌬️ Breathe In...", 4), ("⏸️ Hold...", 4), ("💨 Breathe Out...", 4), ("⏸️ Hold...", 4)],
        "Simple": [("🌬️ Breathe In...", 4), ("💨 Breathe Out...", 6)],
    }

    if st.button("▶️ Start Breathing Exercise", use_container_width=True):
        import time
        status = st.empty()
        progress = st.empty()
        for cycle in range(3):
            for phase_text, duration in phases[technique]:
                status.markdown(f'<div class="breathing-text">{phase_text}</div>', unsafe_allow_html=True)
                for sec in range(duration):
                    progress.progress((sec + 1) / duration, text=f"{duration - sec}s")
                    time.sleep(1)
        status.markdown('<div class="breathing-text">✨ Great job! You did it.</div>', unsafe_allow_html=True)
        progress.empty()


# ─── Resources Page ───
def render_resources():
    st.markdown('<div class="brand-header"><h1>📞 Support Resources</h1><p>You\'re never alone. Help is always available.</p></div>', unsafe_allow_html=True)

    cols = st.columns(2)
    for i, h in enumerate(HELPLINES):
        with cols[i % 2]:
            st.markdown(f"""<div class="resource-card">
                <h3>{h['emoji']} {h['name']}</h3>
                <p style="color:#9896a8;font-size:0.85rem;">{h['desc']}</p>
                <p style="color:#7c6bf0;font-weight:600;">📞 {h['number']}</p>
            </div>""", unsafe_allow_html=True)

    st.divider()
    st.subheader("🧘 Self-Help Strategies")
    strategies = [
        ("🧘 Mindfulness", "5-4-3-2-1: Notice 5 things you see, 4 you touch, 3 you hear, 2 you smell, 1 you taste."),
        ("📝 Journaling", "Write freely. No rules, no judgment. Let your thoughts flow onto the page."),
        ("🚶 Movement", "A short walk can shift your mood. Physical movement releases tension."),
        ("🫂 Connection", "Reach out to someone. A text, a call — human connection heals."),
    ]
    cols2 = st.columns(2)
    for i, (title, desc) in enumerate(strategies):
        with cols2[i % 2]:
            st.markdown(f"**{title}**")
            st.caption(desc)


# ─── Journal Page ───
def render_journal():
    st.markdown('<div class="brand-header"><h1>📝 Your Journal</h1><p>A private space to reflect</p></div>', unsafe_allow_html=True)
    st.caption(datetime.datetime.now().strftime("%A, %B %d, %Y"))

    with st.form("journal_form"):
        entry_text = st.text_area("What's on your mind today?", height=180,
                                  placeholder="Write freely — no rules, no judgment...")
        mood = st.select_slider("Current mood:", options=["😢 Sad", "😟 Low", "😐 Okay", "🙂 Good", "😊 Great"], value="😐 Okay")
        if st.form_submit_button("💾 Save Entry", use_container_width=True):
            if entry_text.strip():
                db.save_journal_entry(st.session_state.user["id"], entry_text.strip(), mood)
                st.success("Journal entry saved!")
                st.rerun()
            else:
                st.warning("Please write something first.")

    st.divider()
    entries = db.get_journal_entries(st.session_state.user["id"])
    if entries:
        st.subheader(f"📖 Past Entries ({len(entries)})")
        for entry in entries:
            st.markdown(f"""<div class="journal-entry">
                <div class="journal-date">{entry['created_at']} — {entry.get('mood','')}</div>
                <p style="color:#9896a8;white-space:pre-wrap;">{entry['content']}</p>
            </div>""", unsafe_allow_html=True)
            if st.button("🗑️ Delete", key=f"del_{entry['id']}"):
                db.delete_journal_entry(entry["id"], st.session_state.user["id"])
                st.rerun()
    else:
        st.info("No journal entries yet. Start writing above!")


# ─── Mood Tracker Page ───
def render_mood():
    st.markdown('<div class="brand-header"><h1>📊 Mood Tracker</h1><p>Track how you feel over time</p></div>', unsafe_allow_html=True)

    moods = {"😊 Great": 5, "🙂 Good": 4, "😐 Okay": 3, "😟 Low": 2, "😢 Sad": 1}
    cols = st.columns(5)
    for i, (label, val) in enumerate(moods.items()):
        if cols[i].button(label, use_container_width=True, key=f"mood_{val}"):
            db.log_mood(st.session_state.user["id"], label)
            st.success(f"Mood logged: {label}")
            st.rerun()

    st.divider()
    history = db.get_mood_history(st.session_state.user["id"], days=30)
    if history:
        import pandas as pd
        df = pd.DataFrame(history)
        mood_to_num = {"😊 Great": 5, "🙂 Good": 4, "😐 Okay": 3, "😟 Low": 2, "😢 Sad": 1}
        df["mood_score"] = df["mood"].map(mood_to_num).fillna(3)
        df["date"] = pd.to_datetime(df["timestamp"])
        st.line_chart(df.set_index("date")["mood_score"], use_container_width=True)
    else:
        st.info("No mood data yet. Log your mood above to start tracking!")


# ─── Settings Page ───
def render_settings():
    st.markdown('<div class="brand-header"><h1>⚙️ Settings</h1></div>', unsafe_allow_html=True)
    user = st.session_state.user

    st.subheader("👤 Profile")
    st.text(f"Username: {user['username']}")
    st.text(f"Display Name: {user['display_name']}")
    st.text(f"Joined: {user['created_at']}")

    st.divider()
    st.subheader("🚨 Emergency Contact")
    st.caption("This contact will be notified immediately during a crisis.")
    with st.form("ec_form"):
        ec_name = st.text_input("Contact Name *", value=user.get("emergency_contact_name", ""))
        ec_phone = st.text_input("Contact Phone *", value=user.get("emergency_contact_phone", ""))
        ec_email = st.text_input("Contact Email", value=user.get("emergency_contact_email", ""))
        if st.form_submit_button("Update Contact", use_container_width=True):
            if not ec_name.strip() or not ec_phone.strip():
                st.error("⚠️ Emergency contact name and phone are required.")
            else:
                db.update_emergency_contact(user["id"], ec_name, ec_phone, ec_email)
                st.session_state.user["emergency_contact_name"] = ec_name
                st.session_state.user["emergency_contact_phone"] = ec_phone
                st.session_state.user["emergency_contact_email"] = ec_email
                st.success("Emergency contact updated!")

    st.divider()
    st.subheader("💬 Conversations")
    if st.button("➕ New Conversation"):
        st.session_state.conversation_id = None
        st.session_state.messages = []
        st.session_state.previous_levels = []
        st.session_state.detected_emotions_history = []
        st.rerun()


# ─── Sidebar & Routing ───
def main():
    if not st.session_state.user:
        render_auth()
        return

    with st.sidebar:
        st.markdown("### 💜 MindfulChat")
        st.caption(f"Welcome, {st.session_state.user['display_name']}")
        st.divider()

        page = st.radio(
            "Navigate",
            ["💬 Chat", "🫁 Breathe", "📞 Resources", "📝 Journal", "📊 Mood", "⚙️ Settings"],
            label_visibility="collapsed",
        )

        st.divider()
        if st.button("🚪 Logout", use_container_width=True):
            for key in list(st.session_state.keys()):
                del st.session_state[key]
            st.rerun()

    pages = {
        "💬 Chat": render_chat,
        "🫁 Breathe": render_breathing,
        "📞 Resources": render_resources,
        "📝 Journal": render_journal,
        "📊 Mood": render_mood,
        "⚙️ Settings": render_settings,
    }
    pages.get(page, render_chat)()


if __name__ == "__main__":
    main()