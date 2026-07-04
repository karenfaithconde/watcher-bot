"""
bot_instance.py

Creates the single shared `bot` object used everywhere else in the
project. Every other file that needs to register an event (@bot.event)
or a command (@bot.command) imports `bot` from here, so there's only
ever one bot instance no matter how many files reference it.
"""

import discord
from discord.ext import commands

intents = discord.Intents.default()
intents.message_content = True
intents.members = True

bot = commands.Bot(command_prefix="!", intents=intents)
