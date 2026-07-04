"""
warnings_store.py

Handles reading and writing each member's warning count to warnings.json
so counts survive a bot restart. `warning_counts` is a plain dict shared
by every file that imports it — since dicts are mutable, updating it in
one file (e.g. events.py) is instantly visible everywhere else too.
"""

import os
import json

WARNINGS_FILE = "warnings.json"


def load_warnings():
    """Load saved warning counts from disk into a dict of {user_id: count}.
    Returns an empty dict if the file doesn't exist yet (first run)."""
    if not os.path.exists(WARNINGS_FILE):
        return {}
    with open(WARNINGS_FILE, "r", encoding="utf-8") as f:
        return {int(k): v for k, v in json.load(f).items()}


def save_warnings():
    """Write the current in-memory warning_counts dict back to disk."""
    with open(WARNINGS_FILE, "w", encoding="utf-8") as f:
        json.dump(warning_counts, f)


# Loaded once at import time, then shared (and mutated in place) by
# every other file that does `from warnings_store import warning_counts`.
warning_counts = load_warnings()
