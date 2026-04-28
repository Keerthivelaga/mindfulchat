"""
MindfulChat — LLM Handler
Priority: Claude API → Ollama (local) → Template fallback
"""

import json
import os
import re
import random
import requests
from config import (
    OLLAMA_HOST,
    OLLAMA_MODEL,
    OLLAMA_TEMPERATURE,
    OLLAMA_MAX_TOKENS,
    OLLAMA_CONTEXT_WINDOW,
    SYSTEM_PROMPT,
    DISTRESS_PROMPT_ADDITIONS,
    RESTRICTED_WORDS,
    RESTRICTED_REPLACEMENTS,
)

# ── Claude API config ──────────────────────────────────────────────────────────
CLAUDE_API_URL = "https://api.anthropic.com/v1/messages"
CLAUDE_MODEL   = "claude-sonnet-4-20250514"
CLAUDE_MAX_TOKENS = 500


def _get_claude_api_key() -> str | None:
    """Read Claude API key from env or Streamlit secrets."""
    key = os.environ.get("ANTHROPIC_API_KEY")
    if key:
        return key
    try:
        import streamlit as st
        return st.secrets.get("ANTHROPIC_API_KEY")
    except Exception:
        return None


def is_claude_available() -> bool:
    """Return True if an Anthropic API key is configured."""
    return bool(_get_claude_api_key())


def is_ollama_available() -> bool:
    """Check if Ollama is running and accessible."""
    try:
        resp = requests.get(f"{OLLAMA_HOST}/api/tags", timeout=2)
        return resp.status_code == 200
    except Exception:
        return False


# ── Shared helpers ─────────────────────────────────────────────────────────────

def filter_restricted_words(text: str) -> str:
    """Replace restricted/harmful words with safe alternatives."""
    filtered = text
    for word in RESTRICTED_WORDS:
        pattern = re.compile(re.escape(word), re.IGNORECASE)
        replacement = RESTRICTED_REPLACEMENTS.get(word.lower(), "difficulty")
        filtered = pattern.sub(replacement, filtered)
    return filtered


def build_system_prompt(distress_level: str, user_context: dict = None) -> str:
    """Build a dynamic system prompt based on distress level and user context."""
    if distress_level in ("positive", "very_positive"):
        prompt = (
            "You are MindfulChat, a warm and cheerful companion. The user is feeling positive "
            "and wants to share their happiness. Match their energy with genuine joy, enthusiasm, "
            "and warmth.\n\n"
            "RULES for positive conversations:\n"
            "- Be ENTHUSIASTIC and celebratory when they share good news\n"
            "- Ask genuine follow-up questions about their happy experience\n"
            "- Use upbeat, light-hearted language\n"
            "- Share in their excitement naturally\n"
            "- Do NOT pivot to negative topics or add unnecessary caveats\n"
            "- Keep responses natural and conversational (2-3 sentences)\n"
            "- Do NOT include labels, prefixes, or system notes in your response\n"
        )
    else:
        prompt = SYSTEM_PROMPT

    addition = DISTRESS_PROMPT_ADDITIONS.get(distress_level, "")
    if addition:
        prompt += addition

    if user_context:
        parts = []
        if user_context.get("display_name"):
            parts.append(f"The user's name is {user_context['display_name']}.")
        if user_context.get("recent_emotions"):
            emotions_str = ", ".join(set(user_context["recent_emotions"][-5:]))
            parts.append(f"Emotions detected: {emotions_str}.")
        if parts:
            prompt += "\n\n[USER CONTEXT: " + " ".join(parts) + "]"

    return prompt


def build_messages(system_prompt: str, conversation_history: list, user_message: str) -> list:
    """Build messages array (works for both Claude API and Ollama)."""
    messages = [{"role": "system", "content": system_prompt}]
    recent = conversation_history[-OLLAMA_CONTEXT_WINDOW:] if conversation_history else []
    for msg in recent:
        role = msg.get("role", "user")
        content = msg.get("content", "")
        if role in ("user", "assistant"):
            messages.append({"role": role, "content": content})
    messages.append({"role": "user", "content": user_message})
    return messages


# ── Claude API backend ─────────────────────────────────────────────────────────

def _call_claude(system_prompt: str, conversation_history: list, user_message: str) -> str | None:
    """
    Call the Anthropic Messages API.
    Returns the text response or None on failure.
    """
    api_key = _get_claude_api_key()
    if not api_key:
        return None

    # Claude API takes system separately; messages must not start with system role
    recent = conversation_history[-OLLAMA_CONTEXT_WINDOW:] if conversation_history else []
    messages = []
    for msg in recent:
        role = msg.get("role", "user")
        content = msg.get("content", "")
        if role in ("user", "assistant"):
            messages.append({"role": role, "content": content})
    messages.append({"role": "user", "content": user_message})

    try:
        resp = requests.post(
            CLAUDE_API_URL,
            headers={
                "x-api-key": api_key,
                "anthropic-version": "2023-06-01",
                "content-type": "application/json",
            },
            json={
                "model": CLAUDE_MODEL,
                "max_tokens": CLAUDE_MAX_TOKENS,
                "system": system_prompt,
                "messages": messages,
            },
            timeout=20,
        )
        if resp.status_code == 200:
            data = resp.json()
            text = data.get("content", [{}])[0].get("text", "").strip()
            return text if text else None
    except Exception:
        pass
    return None


# ── Ollama backend ─────────────────────────────────────────────────────────────

def _call_ollama(system_prompt: str, conversation_history: list, user_message: str) -> str | None:
    """Call local Ollama. Returns text or None on failure."""
    messages = build_messages(system_prompt, conversation_history, user_message)
    try:
        resp = requests.post(
            f"{OLLAMA_HOST}/api/chat",
            json={
                "model": OLLAMA_MODEL,
                "messages": messages,
                "stream": False,
                "options": {
                    "temperature": OLLAMA_TEMPERATURE,
                    "num_predict": OLLAMA_MAX_TOKENS,
                },
            },
            timeout=30,
        )
        if resp.status_code == 200:
            text = resp.json().get("message", {}).get("content", "").strip()
            return text if text else None
    except Exception:
        pass
    return None


# ── Public API ─────────────────────────────────────────────────────────────────

def generate_response(
    user_message: str,
    conversation_history: list,
    nlp_analysis: dict,
    user_context: dict = None,
) -> str:
    """
    Generate a response.
    Priority: Claude API → Ollama → Template fallback.
    """
    distress_level = nlp_analysis.get("distress_level", "neutral")
    system_prompt  = build_system_prompt(distress_level, user_context)

    # 1. Try Claude API
    if is_claude_available():
        reply = _call_claude(system_prompt, conversation_history, user_message)
        if reply:
            return filter_restricted_words(reply)

    # 2. Try Ollama
    if is_ollama_available():
        reply = _call_ollama(system_prompt, conversation_history, user_message)
        if reply:
            return filter_restricted_words(reply)

    # 3. Template fallback
    return _fallback_response(distress_level, nlp_analysis)


def generate_response_stream(
    user_message: str,
    conversation_history: list,
    nlp_analysis: dict,
    user_context: dict = None,
):
    """
    Streaming-compatible response generator.
    Claude API and fallback yield a single chunk; Ollama streams.
    """
    distress_level = nlp_analysis.get("distress_level", "neutral")
    system_prompt  = build_system_prompt(distress_level, user_context)

    # 1. Try Claude API (yields single complete response — fast enough)
    if is_claude_available():
        reply = _call_claude(system_prompt, conversation_history, user_message)
        if reply:
            yield filter_restricted_words(reply)
            return

    # 2. Try Ollama with true streaming
    if is_ollama_available():
        messages = build_messages(system_prompt, conversation_history, user_message)
        try:
            resp = requests.post(
                f"{OLLAMA_HOST}/api/chat",
                json={
                    "model": OLLAMA_MODEL,
                    "messages": messages,
                    "stream": True,
                    "options": {
                        "temperature": OLLAMA_TEMPERATURE,
                        "num_predict": OLLAMA_MAX_TOKENS,
                    },
                },
                stream=True,
                timeout=60,
            )
            if resp.status_code == 200:
                full_text = ""
                for line in resp.iter_lines():
                    if line:
                        try:
                            data = json.loads(line)
                            chunk = data.get("message", {}).get("content", "")
                            if chunk:
                                full_text += chunk
                            if data.get("done", False):
                                break
                        except json.JSONDecodeError:
                            continue
                if full_text:
                    yield filter_restricted_words(full_text)
                    return
        except Exception:
            pass

    # 3. Template fallback
    yield _fallback_response(distress_level, nlp_analysis)


# ── Fallback response library ──────────────────────────────────────────────────

_FALLBACK_RESPONSES = {
    "emergency": [
        "I'm really sorry you're feeling this much pain right now. Please know you're not alone. "
        "I'd encourage you to reach out to iCall at 9152987821 or AASRA at 9820466627. "
        "You deserve support and care.",
        "I hear you, and your pain matters. Please consider reaching out to a trusted person "
        "or calling iCall at 9152987821 right now. You don't have to carry this alone.",
    ],
    "high": [
        "I'm really sorry you're carrying so much right now. That weight sounds incredibly heavy. "
        "You don't have to face this alone — please consider reaching out to someone you trust.",
        "It sounds like you're going through an incredibly tough time. Your feelings are valid. "
        "Would it help to talk about what's been weighing on you?",
    ],
    "moderate": [
        "I'm sorry you're feeling this way. That sounds really draining. "
        "Do you want to talk about what's been contributing to these feelings?",
        "I hear you. That can feel like a heavy cloud. "
        "I'm here to listen without judgment — what's been making things feel this way?",
    ],
    "mild": [
        "I'm sorry to hear that. Even small things can weigh on us. "
        "Do you want to share what's been bothering you?",
        "That sounds tough. It's okay to not be okay sometimes. I'm here to listen.",
    ],
    "positive": [
        "That's so good to hear! 😊 I'm really glad things are going well for you. "
        "What's been making you feel this way?",
        "It sounds like you're in a really good place right now — that's wonderful! "
        "Tell me more about what's been going well.",
        "I love hearing that! Positive moments like these are worth celebrating. "
        "What's been the highlight of your day?",
    ],
    "very_positive": [
        "Oh wow, that's absolutely amazing!! 🎉 I'm so genuinely happy for you! "
        "Tell me everything — I want to hear all about it!",
        "That's incredible news! 🥳 You must be over the moon right now! "
        "You totally deserve this — congratulations!",
        "This is SO exciting!! 🎊 I'm celebrating right along with you! "
        "What happened — I need all the details!",
        "YESSS!! That is the best news!! 🌟 I'm so proud of you and so happy for you! "
        "How are you feeling right now?",
    ],
    "neutral": [
        "Thank you for reaching out. I'm here for you — feel free to share whatever is on your mind.",
        "I'm here whenever you need to talk. What's been on your mind?",
    ],
}


def _fallback_response(distress_level: str, nlp_analysis: dict) -> str:
    responses = _FALLBACK_RESPONSES.get(distress_level, _FALLBACK_RESPONSES["neutral"])
    return random.choice(responses)