# config.py

This file was one of the easier ones to understand once I got what problem it solves. Before I had this file, I kept typing os.getenv("SOME_ID") in random places across different files, and it got messy fast. Now every setting lives in exactly one spot.

## Walking through the code

```python
import os
from dotenv import load_dotenv

load_dotenv()
```

os is a built in Python module for talking to the operating system, including reading environment variables. dotenv is a small library that reads a .env file and loads whatever is in it into those same environment variables. load_dotenv() is the line that actually goes and does that reading, right when the bot starts up.

```python
TOKEN = os.getenv("DISCORD_TOKEN")
MOD_LOG_CHANNEL_ID = int(os.getenv("MOD_LOG_CHANNEL_ID"))
WELCOME_CHANNEL_ID = int(os.getenv("WELCOME_CHANNEL_ID"))
NOTIFY_ROLE_ID = int(os.getenv("NOTIFY_ROLE_ID"))
SAFE_BROWSING_API_KEY = os.getenv("SAFE_BROWSING_API_KEY")
```

Each of these pulls one specific value out of the .env file. os.getenv always gives back a plain string, which is fine for the token and the API key, but Discord IDs need to be actual numbers to be usable later on, which is why those three get wrapped in int(...). I actually forgot to do that the first time I wrote this, and got a confusing error much later in the code, in a completely different file, which is a good reminder that a small mistake here can show up somewhere else entirely.

```python
TIMEOUT_AT = 5
BAN_AT = 10
TIMEOUT_DURATION = 600
```

These three control the whole warning escalation system. Once someone's warning count reaches TIMEOUT_AT, they get muted. Once it reaches BAN_AT, they get banned. TIMEOUT_DURATION is how long that mute actually lasts, measured in seconds, so 600 means 10 minutes.

```python
SPAM_LIMIT = 5
SPAM_WINDOW = 5
```

This pair works together to define what counts as spam. Together they mean more than 5 messages within 5 seconds counts as spamming. Changing either number changes how strict or lenient that detection feels.

```python
ALLOWED_WORDS = {"fuck", "fucking", "fuckin", "bitch", "bitches"}
```

This is the whitelist. Without it, the profanity filter would flag these words too, which was not what I wanted since plenty of normal conversation uses them casually.

## Why this file matters more than it looks

If I ever want to make the bot stricter or looser, this is the only file I touch. I do not have to go hunting through events.py or filters.py looking for a hardcoded number somewhere. Everything tunable lives right here.
