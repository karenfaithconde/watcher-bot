import os
from dotenv import load_dotenv

load_dotenv()

# secrets / IDs from .env
TOKEN = os.getenv("DISCORD_TOKEN")
MOD_LOG_CHANNEL_ID = int(os.getenv("MOD_LOG_CHANNEL_ID"))
WELCOME_CHANNEL_ID = int(os.getenv("WELCOME_CHANNEL_ID"))
NOTIFY_ROLE_ID = int(os.getenv("NOTIFY_ROLE_ID"))
SAFE_BROWSING_API_KEY = os.getenv("SAFE_BROWSING_API_KEY")

# moderation thresholds
TIMEOUT_AT = 5          # warning count that triggers a timeout
BAN_AT = 10             # warning count that triggers a ban
TIMEOUT_DURATION = 600  # seconds (10 minutes)

# spam detection tuning
SPAM_LIMIT = 5   # max messages allowed
SPAM_WINDOW = 5  # within this many seconds

# words the profanity filter should NOT flag
ALLOWED_WORDS = {"fuck", "fucking", "fuckin", "bitch", "bitches"}