from bot_instance import bot
from config import TOKEN

# importing these actually registers all the @bot.event / @bot.command handlers
import events    # noqa: F401
import commands  # noqa: F401

bot.run(TOKEN)