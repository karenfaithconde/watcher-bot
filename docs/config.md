# config.py

This file centralizes every setting the bot needs — so instead of every file separately reading environment variables, they all just import from here.

## Where the values actually come from

`load_dotenv()` reads your `.env` file (which never gets pushed to GitHub — see `.gitignore`) and loads it into the environment. Everything else in this file is just `os.getenv(...)` pulling specific values out of that.

## What's in here

- **Secrets/IDs** — your bot token, and the channel/role IDs the bot needs to know about (mod-log channel, welcome channel, notify role, Safe Browsing API key)
- **Moderation thresholds** — `TIMEOUT_AT` and `BAN_AT` control how many warnings trigger each punishment, `TIMEOUT_DURATION` controls how long a timeout lasts
- **Spam tuning** — `SPAM_LIMIT` and `SPAM_WINDOW` control what counts as "too many messages too fast"
- **`ALLOWED_WORDS`** — the whitelist of words the profanity filter should let through instead of flagging

## Why this matters for editing later

If you ever want to change how strict the bot is (e.g. ban after 15 warnings instead of 10), this is the only file you need to touch — everywhere else just reads `BAN_AT` from here instead of having the number hardcoded in multiple places.
