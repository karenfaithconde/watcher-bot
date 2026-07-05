# warnings_store.py

Small file, but it solves a problem I ran into early on that genuinely annoyed me. Every time I restarted the bot to test a change, everyone's warning counts would just vanish back to zero, which meant someone could dodge a ban just by me restarting the bot at the wrong moment. This file fixes that.

## The whole file

```python
import os
import json

WARNINGS_FILE = "warnings.json"


def load_warnings():
    if not os.path.exists(WARNINGS_FILE):
        return {}
    with open(WARNINGS_FILE, "r", encoding="utf-8") as f:
        return {int(k): v for k, v in json.load(f).items()}


def save_warnings():
    with open(WARNINGS_FILE, "w", encoding="utf-8") as f:
        json.dump(warning_counts, f)


warning_counts = load_warnings()
```

## load_warnings

```python
def load_warnings():
    if not os.path.exists(WARNINGS_FILE):
        return {}
    with open(WARNINGS_FILE, "r", encoding="utf-8") as f:
        return {int(k): v for k, v in json.load(f).items()}
```

os.path.exists checks whether warnings.json is even there yet. The very first time the bot ever runs, it will not be, since nobody has been warned yet, so this just returns an empty dictionary instead of crashing.

If the file does exist, json.load(f) reads it and turns it back into a Python dictionary. The part that confused me at first is right after that, {int(k): v for k, v in json.load(f).items()}. JSON only ever stores keys as text, even if they started out as numbers, so every user id gets saved as a string like "123456789". This line rebuilds the dictionary with those keys converted back into actual integers, since the rest of my code expects to compare real numbers, not text that happens to look like numbers.

## save_warnings

```python
def save_warnings():
    with open(WARNINGS_FILE, "w", encoding="utf-8") as f:
        json.dump(warning_counts, f)
```

This is the reverse direction, taking whatever is currently in warning_counts and writing it back out to the file. I call this every single time a warning count changes anywhere else in the project, so the file on disk never falls out of sync with what is actually happening in memory.

## warning_counts, the shared dictionary

```python
warning_counts = load_warnings()
```

This line runs once, right when the bot starts, and it is the part that makes sharing this across files actually work. Since dictionaries in Python are mutable, meaning they can be changed in place, every other file that does from warnings_store import warning_counts is not getting a copy, it is getting a reference to this exact same dictionary. So when events.py adds a warning, commands.py sees that updated count immediately too, without me needing to pass it around manually between files.

## Why warnings.json itself is not on GitHub

It is just data, specific to my own server, not code anyone else would need. It is listed in .gitignore for the same reason .env is, so it never accidentally gets pushed publicly.
