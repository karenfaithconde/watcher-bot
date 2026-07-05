# Watcher

Watcher is a Discord moderation bot I built to keep servers safer without needing a mod glued to the screen 24/7. It filters bad messages, keeps track of who's been warned, and gives moderators a clean in-Discord menu instead of having to memorize commands.

## What it does

- Deletes offensive language automatically (with a whitelist for casual swearing)
- Catches spam — too many messages too fast gets shut down
- Checks links against Google's Safe Browsing list and removes dangerous ones
- Tracks warnings per user and escalates to a timeout, then a ban, if things don't improve
- Gives mods a button-based menu (`!m`) instead of typing out commands — mute, warn, clear, ban, or unban with a couple of clicks
- Posts a welcome/leave message when people join or leave
- Has a toggle button so members can opt in or out of join-ping notifications
- `!p` gives a quick read on how "new" or suspicious an account looks, based on public info like account age and avatar
- A built-in help menu (`!setuphelp`) explains all of this right inside Discord, no docs required

Everything runs on prefix commands (`!`) — there's no slash command support yet.

## Project structure

```
Watcher/
├── main.py
├── bot_instance.py
├── config.py
├── commands.py
├── events.py
├── filters.py
├── ui_modmenu.py
├── ui_notify.py
├── ui_help.py
├── ui_profile.py
├── warnings_store.py
├── requirements.txt
├── .env.example
└── .gitignore
```

## What each file actually does

**`main.py`**
The starting point. Run this one file and everything else comes to life — it just pulls in the other files and tells the bot to log in.

**`bot_instance.py`**
Creates the one shared bot object every other file plugs into. Keeps things from accidentally creating multiple bots.

**`config.py`**
Pulls in all the settings (token, channel IDs, thresholds) from a `.env` file, so nothing sensitive is hardcoded in the actual code.

**`commands.py`**
Every command someone can type — `!m`, `!purge`, `!p`, `!setupnotify`, `!setuphelp`.

**`events.py`**
Everything that happens automatically, without anyone typing a command — checking messages for violations, welcoming new members, and posting a setup message when the bot first joins a server.

**`filters.py`**
The actual detection logic: is this message profanity? Is it spam? Is that link dangerous? Just yes/no answers — the "what to do about it" part lives in `events.py`.

**`ui_modmenu.py`**
The buttons and pop-up forms behind the `!m` moderation menu.

**`ui_notify.py`**
The join-ping toggle button members click to opt in/out.

**`ui_help.py`**
The dropdown menu behind `!setuphelp` — explains every feature right in Discord.

**`ui_profile.py`**
The logic behind `!p` — pulls account info and gives a rough risk read.

**`warnings_store.py`**
Saves and loads everyone's warning counts to a file, so nothing resets if the bot restarts.

## Setup

1. Clone the repo
```
git clone https://github.com/karenfaithconde/watcher-bot.git
```

2. Install the dependencies
```
pip install -r requirements.txt
```

3. Create a `.env` file (see `.env.example` for the format) and fill in your bot token and channel/role IDs

4. Run it
```
python main.py
```

## Requirements

See `requirements.txt` for the full list — nothing exotic, just `discord.py`, `python-dotenv`, `better-profanity`, and `aiohttp`.
