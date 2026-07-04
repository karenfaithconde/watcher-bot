"""
filters.py

Three independent detection checks used by on_message in events.py:

1. is_flagged()        — profanity, word by word, skipping ALLOWED_WORDS
2. is_spamming()       — too many messages too fast from one user
3. is_dangerous_link() — checks any URLs in a message against Google
                         Safe Browsing's malware/phishing database

None of these functions touch Discord directly (delete messages, send
warnings, etc.) — they only answer "is this message bad?" and hand the
decision back to events.py, which handles what to actually do about it.
"""

import re
import string
import time

import aiohttp
from better_profanity import profanity

from config import ALLOWED_WORDS, SPAM_LIMIT, SPAM_WINDOW, SAFE_BROWSING_API_KEY

profanity.load_censor_words()

URL_PATTERN = re.compile(r"https?://\S+")

# Tracks recent message timestamps per user, for spam detection.
message_times = {}


def is_flagged(text):
    """Check a message word by word for profanity, skipping ALLOWED_WORDS."""
    for word in text.split():
        cleaned = word.strip(string.punctuation).lower()
        if cleaned in ALLOWED_WORDS:
            continue
        if profanity.contains_profanity(word):
            return True
    return False


def is_spamming(user_id):
    """Returns True if this user has sent more than SPAM_LIMIT messages
    within the last SPAM_WINDOW seconds."""
    now = time.time()
    times = message_times.get(user_id, [])
    times = [t for t in times if now - t < SPAM_WINDOW]
    times.append(now)
    message_times[user_id] = times
    return len(times) > SPAM_LIMIT


async def is_dangerous_link(text):
    """Extracts URLs from the message and checks them against Google Safe
    Browsing. Returns True if any URL is flagged as malicious."""
    urls = URL_PATTERN.findall(text)
    if not urls:
        return False

    endpoint = f"https://safebrowsing.googleapis.com/v4/threatMatches:find?key={SAFE_BROWSING_API_KEY}"
    payload = {
        "client": {"clientId": "discord-bot", "clientVersion": "1.0"},
        "threatInfo": {
            "threatTypes": ["MALWARE", "SOCIAL_ENGINEERING", "UNWANTED_SOFTWARE", "POTENTIALLY_HARMFUL_APPLICATION"],
            "platformTypes": ["ANY_PLATFORM"],
            "threatEntryTypes": ["URL"],
            "threatEntries": [{"url": url} for url in urls]
        }
    }

    async with aiohttp.ClientSession() as session:
        async with session.post(endpoint, json=payload) as resp:
            data = await resp.json()
            return bool(data.get("matches"))
