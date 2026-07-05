# bot_instance.py

This file's only job is to create **one single bot object** that every other file can share.

## Why this file exists separately

If every file created its own `commands.Bot(...)`, you'd end up with multiple bots that don't know about each other's commands or events. Instead, this file creates the bot *once*, and everywhere else just imports it:

```python
from bot_instance import bot
```

That way, `events.py` can register `@bot.event` handlers, `commands.py` can register `@bot.command` handlers, and they're all attaching to the exact same bot.

## What's actually in it

- **Intents** — these tell Discord which kinds of data your bot wants to receive. `message_content` lets the bot read message text (needed for the profanity/spam/link filters), and `members` lets it see member join/leave events and full member info (needed for welcome messages and the `!p` profile check).
- **The bot object itself** — created with `command_prefix="!"`, meaning every text command starts with `!`.
