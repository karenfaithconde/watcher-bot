"""
config.py

Loads settings from the .env file and defines constants used across the
whole bot. Nothing in here talks to Discord directly — this file's only
job is to centralize configuration so every other file can import from
one place instead of re-reading environment variables everywhere.
"""

import os
from dotenv import load_dotenv

load_dotenv()

# --- Secrets / IDs pulled from .env ---
TOKEN = os.getenv("DISCORD_TOKEN")
MOD_LOG_CHANNEL_ID = int(os.getenv("MOD_LOG_CHANNEL_ID"))
WELCOME_CHANNEL_ID = int(os.getenv("WELCOME_CHANNEL_ID"))
NOTIFY_ROLE_ID = int(os.getenv("NOTIFY_ROLE_ID"))
SAFE_BROWSING_API_KEY = os.getenv("SAFE_BROWSING_API_KEY")

# --- Moderation thresholds ---
TIMEOUT_AT = 5          # warning count that triggers a timeout
BAN_AT = 10             # warning count that triggers a ban
TIMEOUT_DURATION = 600  # seconds (10 minutes)

# --- Spam detection tuning ---
SPAM_LIMIT = 5   # max messages allowed
SPAM_WINDOW = 5  # within this many seconds

# --- Words the profanity filter should NOT flag ---
ALLOWED_WORDS = {"fuck", "fucking", "fuckin", "bitch", "bitches"}
