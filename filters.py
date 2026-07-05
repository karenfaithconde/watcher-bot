import re
import string
import time

import aiohttp
from better_profanity import profanity

from config import ALLOWED_WORDS, SPAM_LIMIT, SPAM_WINDOW, SAFE_BROWSING_API_KEY

profanity.load_censor_words()

URL_PATTERN = re.compile(r"https?://\S+")

# tracks recent message timestamps per user, for spam detection
message_times = {}


def is_flagged(text):
    # checks a message word by word, skips anything in ALLOWED_WORDS
    for word in text.split():
        cleaned = word.strip(string.punctuation).lower()
        if cleaned in ALLOWED_WORDS:
            continue
        if profanity.contains_profanity(word):
            return True
    return False


def is_spamming(user_id):
    # True if this user sent more than SPAM_LIMIT messages in the last SPAM_WINDOW seconds
    now = time.time()
    times = message_times.get(user_id, [])
    times = [t for t in times if now - t < SPAM_WINDOW]
    times.append(now)
    message_times[user_id] = times
    return len(times) > SPAM_LIMIT


async def is_dangerous_link(text):
    # checks any URLs in the message against Google Safe Browsing
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