import os
import json

WARNINGS_FILE = "warnings.json"


def load_warnings():
    # loads saved counts from disk, or starts empty if the file doesn't exist yet
    if not os.path.exists(WARNINGS_FILE):
        return {}
    with open(WARNINGS_FILE, "r", encoding="utf-8") as f:
        return {int(k): v for k, v in json.load(f).items()}


def save_warnings():
    # writes the current counts back to disk
    with open(WARNINGS_FILE, "w", encoding="utf-8") as f:
        json.dump(warning_counts, f)


warning_counts = load_warnings()