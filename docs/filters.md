# filters.py

This file answers one type of question: **"is this message bad, and if so, how?"** It never deletes messages, sends warnings, or bans anyone — that decision-making lives in `events.py`. This file just returns `True` or `False`.

## The three checks

### `is_flagged(text)`
Splits the message into individual words, strips punctuation, and checks each one against the `better_profanity` library — skipping anything in `ALLOWED_WORDS` (your whitelist). Returns `True` the moment it finds one flagged word.

### `is_spamming(user_id)`
Keeps a running list of timestamps for every message each user sends (`message_times`). Every time this runs, it throws out any timestamps older than `SPAM_WINDOW` seconds, adds the current one, and checks if the count is still over `SPAM_LIMIT`. This is what "too many messages too fast" actually means in code.

### `is_dangerous_link(text)`
Pulls any URLs out of the message using a regex pattern, then sends them to Google's Safe Browsing API to check if they're known malware/phishing sites. This one's `async` because it has to wait on a network response — the other two checks are instant since they don't leave your computer.

## Why these are kept separate from the "what to do" logic

Keeping detection separate from action makes each piece easier to test and reason about on its own — `events.py` doesn't need to know *how* something gets flagged, just *whether* it did.
