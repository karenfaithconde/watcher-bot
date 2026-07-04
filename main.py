"""
main.py

The entry point — run this file to start the bot:

    python main.py

Importing `events` and `commands` is what actually registers all the
@bot.event and @bot.command handlers (each decorator runs the moment
its module is imported). This file just needs to trigger those imports
and then call bot.run().
"""

from bot_instance import bot
from config import TOKEN

import events    # noqa: F401  (imported for its side effect: registers events)
import commands  # noqa: F401  (imported for its side effect: registers commands)

bot.run(TOKEN)
