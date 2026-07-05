# warnings_store.py

This file is the bridge between "warning counts in memory" and "warning counts saved to disk."

## The problem it solves

Without this file, every user's warning count would just live in a Python dictionary in memory — which means restarting the bot would wipe everyone's counts back to zero, letting repeat offenders dodge consequences just by the bot restarting.

## How it works

- **`load_warnings()`** — runs once, when the bot starts. Reads `warnings.json` if it exists and turns it back into a dictionary. If the file doesn't exist yet (first time running the bot), it just returns an empty dictionary.
- **`save_warnings()`** — writes the current `warning_counts` dictionary back out to `warnings.json`. This gets called every time someone's count changes.
- **`warning_counts`** — the actual dictionary, loaded once at the bottom of the file. Every other file that does `from warnings_store import warning_counts` gets a reference to this *same* dictionary — since dictionaries are mutable in Python, updating it in `events.py` is instantly visible in `commands.py` and `ui_modmenu.py` too, without needing to pass it around manually.

## Why `warnings.json` isn't in the GitHub repo

It's just data, not code — and it's specific to your server. It's listed in `.gitignore` so it never gets pushed, the same way `.env` doesn't.
