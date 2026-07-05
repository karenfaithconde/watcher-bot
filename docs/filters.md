# filters.py

This file answers one simple question over and over: is this message bad, and if so, why. It never deletes anything or bans anyone itself. That part lives in events.py. This file just returns True or False and lets events.py decide what to actually do about it.

## The imports

```python
import re
import string
import time

import aiohttp
from better_profanity import profanity

from config import ALLOWED_WORDS, SPAM_LIMIT, SPAM_WINDOW, SAFE_BROWSING_API_KEY
```

re is for pattern matching, which I use to pull links out of a message. string gives me a quick list of punctuation characters so I can strip them off words before checking them. time lets me track when messages were sent, in seconds. aiohttp is what actually lets this file talk to Google over the internet. better_profanity is the library doing the real word matching work, I am not writing that detection myself.

```python
profanity.load_censor_words()
```

This loads the library's built in word list into memory, once, when the bot starts. I originally had this line somewhere else entirely and could not figure out why detection was not working, turns out it just was not loaded yet.

```python
URL_PATTERN = re.compile(r"https?://\S+")
```

This is a regex pattern, basically a search rule, that matches anything starting with http:// or https:// followed by non whitespace characters. Compiling it once up here instead of rebuilding it every time is a small performance thing I picked up along the way.

```python
message_times = {}
```

An empty dictionary that is going to hold, for every user id, a list of timestamps for their recent messages. This is the memory behind spam detection.

## is_flagged

```python
def is_flagged(text):
    for word in text.split():
        cleaned = word.strip(string.punctuation).lower()
        if cleaned in ALLOWED_WORDS:
            continue
        if profanity.contains_profanity(word):
            return True
    return False
```

text.split() breaks the message into individual words. For each one, I strip off punctuation and lowercase it, so a word like Fuck! and fuck both get treated the same way. If that cleaned word is in my whitelist, ALLOWED_WORDS, I skip it entirely with continue. Otherwise I check it against the profanity library, and the moment any single word comes back flagged, I return True immediately without checking the rest of the message.

## is_spamming

```python
def is_spamming(user_id):
    now = time.time()
    times = message_times.get(user_id, [])
    times = [t for t in times if now - t < SPAM_WINDOW]
    times.append(now)
    message_times[user_id] = times
    return len(times) > SPAM_LIMIT
```

This one took me a bit to fully understand the first time I wrote it. Every time someone sends a message, I grab their list of previous timestamps, throw out anything older than SPAM_WINDOW seconds using that list comprehension, then add the current moment onto the end. Whatever is left over after that cleanup is only their recent activity, and if that count is higher than SPAM_LIMIT, they are spamming.

## is_dangerous_link

```python
async def is_dangerous_link(text):
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
```

This is the only function in the whole file marked async, and that is not an accident. Checking a link means actually leaving my computer and asking Google a question over the internet, which takes real time to come back, unlike the other two checks which finish instantly using only local data.

URL_PATTERN.findall(text) pulls every link out of the message into a list. If there are none, there is nothing to check, so it returns False right away. Otherwise it builds a payload, which is really just a structured request following the exact shape Google's Safe Browsing API expects, listing every url found and asking whether any of them match known malware or phishing sites. The response comes back as data, and data.get("matches") will only exist and contain something if at least one link was actually flagged, so wrapping it in bool(...) turns that into a clean True or False either way.

## Why these three live in one file together

None of these three checks know or care about each other. They do not call each other, and they do not touch Discord directly. Keeping them together just because they are all detection logic, separate from the punishment logic in events.py, made the whole project easier to reason about once I split it this way.
